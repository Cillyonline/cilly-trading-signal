from dataclasses import dataclass
from decimal import Decimal

from app.models.enums import Bias, StrategyType
from app.strategies.contracts import (
    IndicatorContext,
    ScoreBreakdown,
    SignalEvaluationInput,
    SignalEvaluationResult,
    build_signal_result,
    calculate_risk_reward,
)

MAX_BASE_WIDTH_PERCENT = Decimal("0.15")
MAJOR_RESISTANCE_BUFFER = Decimal("0.03")
EXCESSIVE_BREAKOUT_ATR_MULTIPLE = Decimal("2.5")
BREAKOUT_STOP_BUFFER_ATR = Decimal("0.5")
TARGET_1_R_MULTIPLE = Decimal("2")
TARGET_2_R_MULTIPLE = Decimal("3")


@dataclass(frozen=True)
class BaseBreakoutInput:
    signal_input: SignalEvaluationInput
    daily: IndicatorContext
    trigger: IndicatorContext
    previous_ema20: Decimal | None
    previous_ema50: Decimal | None
    base_high: Decimal | None
    base_low: Decimal | None
    base_days: int
    base_high_is_clear: bool = True
    previous_move_constructive: bool = True
    volume_drying_up: bool = True
    asset_liquid: bool = True
    major_resistance_level: Decimal | None = None
    close_above_base_high_4h: bool = False
    close_above_base_high_daily: bool = False
    wick_above_base_high_only: bool = False
    close_near_high: bool = True
    setup_invalidated: bool = False
    target_1_override: Decimal | None = None
    target_2_override: Decimal | None = None


def evaluate_base_breakout_long(payload: BaseBreakoutInput) -> SignalEvaluationResult:
    signal_input = SignalEvaluationInput(
        symbol=payload.signal_input.symbol,
        asset_class=payload.signal_input.asset_class,
        strategy_type=StrategyType.BASE_BREAKOUT_LONG,
        weekly_bias=payload.signal_input.weekly_bias,
        daily_bias=payload.signal_input.daily_bias,
        context_timeframe=payload.signal_input.context_timeframe,
        setup_timeframe=payload.signal_input.setup_timeframe,
        trigger_timeframe=payload.signal_input.trigger_timeframe,
        weekly_indicators=payload.signal_input.weekly_indicators,
        daily_indicators=payload.daily,
        trigger_indicators=payload.trigger,
        data_quality_flags=[*payload.signal_input.data_quality_flags, *data_quality_flags(payload)],
        setup_invalidated=payload.signal_input.setup_invalidated or payload.setup_invalidated,
    )
    risk_flags = initial_risk_flags(payload)
    reasoning: list[str] = []

    trend_score, trend_reasons = score_trend(payload)
    structure_score, structure_reasons = score_base_structure(payload)
    momentum_score, momentum_reasons = score_momentum(payload)
    volume_score, volume_reasons = score_volume(payload)
    reasoning.extend(trend_reasons)
    reasoning.extend(structure_reasons)
    reasoning.extend(momentum_reasons)
    reasoning.extend(volume_reasons)

    entry_low = payload.base_high
    entry_high = payload.daily.close or payload.trigger.close
    stop_loss = calculate_stop_loss(payload)
    target_1 = payload.target_1_override or calculate_target(
        entry_low, stop_loss, TARGET_1_R_MULTIPLE
    )
    target_2 = payload.target_2_override or calculate_target(
        entry_low, stop_loss, TARGET_2_R_MULTIPLE
    )
    risk_reward = None
    if entry_low is not None and stop_loss is not None and target_1 is not None:
        risk_reward = calculate_risk_reward(entry_low, stop_loss, target_1)

    risk_reward_score = 15 if risk_reward is not None and risk_reward >= Decimal("2.0") else 0
    if risk_reward is not None:
        reasoning.append(f"Risk/reward check produced {risk_reward:.2f}R.")
    else:
        reasoning.append("Risk/reward check could not be calculated from entry, stop, and target.")

    has_trigger = has_valid_breakout_trigger(payload)
    if has_trigger:
        reasoning.append("Breakout confirmation passed with close above base high.")
    elif payload.wick_above_base_high_only:
        reasoning.append("Breakout confirmation failed because wick/spike alone is insufficient.")
        risk_flags.append("wick_without_close_confirmation")
    else:
        reasoning.append("Breakout confirmation is incomplete; wait for close above base high.")

    if resistance_nearby(payload):
        risk_flags.append("major_resistance_nearby")
    if not payload.asset_liquid:
        risk_flags.append("liquidity_unconfirmed")

    score_breakdown = ScoreBreakdown(
        trend=trend_score,
        structure=structure_score,
        momentum=momentum_score,
        volume=volume_score,
        risk_reward=risk_reward_score,
        risk_filters=0,
    )

    return build_signal_result(
        signal_input,
        score_breakdown,
        bias=Bias.BULLISH if trend_score >= 15 else Bias.NEUTRAL,
        reasoning=reasoning,
        risk_flags=dedupe(risk_flags),
        next_action=next_action(has_trigger, risk_reward),
        entry_low=entry_low,
        entry_high=entry_high,
        trigger_level=payload.base_high,
        stop_loss=stop_loss,
        target_1=target_1,
        target_2=target_2,
        risk_reward=risk_reward,
        invalidation_reason=invalidation_reason(payload),
        has_valid_trigger_plan=(
            has_trigger and risk_reward is not None and risk_reward >= Decimal("2.0")
        ),
    )


def score_trend(payload: BaseBreakoutInput) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    daily = payload.daily

    if daily.close is not None and daily.ema200 is not None and daily.close > daily.ema200:
        score += 10
        reasons.append("Trend check: daily close is above EMA200.")
    else:
        reasons.append("Trend check: daily close is not confirmed above EMA200.")

    if ema20_or_ema50_rising_or_stable(payload):
        score += 8
        reasons.append("Trend check: EMA20/EMA50 are rising or stable.")
    else:
        reasons.append("Trend check: EMA20/EMA50 stability is not confirmed.")

    if payload.previous_move_constructive:
        score += 5
        reasons.append("Trend check: prior move into the base is constructive.")
    else:
        reasons.append("Trend check: prior move into the base is not constructive.")

    if payload.signal_input.weekly_bias == Bias.BULLISH:
        score += 2
        reasons.append("Trend check: weekly context is bullish.")
    elif payload.signal_input.weekly_bias == Bias.NEUTRAL:
        score += 1
        reasons.append("Trend check: weekly context is neutral, so confirmation must be stronger.")

    return min(score, 25), reasons


def score_base_structure(payload: BaseBreakoutInput) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    if payload.base_days >= 5:
        score += 7
        reasons.append("Base quality check: consolidation lasts at least five candles.")
    else:
        reasons.append("Base quality check: consolidation is too short for high confidence.")

    if payload.base_high_is_clear and payload.base_high is not None:
        score += 6
        reasons.append("Base quality check: base high is clearly defined.")
    else:
        reasons.append("Base quality check: base high is not clearly defined.")

    if not base_is_too_wide(payload):
        score += 6
        reasons.append("Base quality check: base range is within the MVP width threshold.")
    else:
        reasons.append("Base quality check: base range is too wide for clean risk planning.")

    if payload.base_low is not None:
        score += 4
        reasons.append(
            "Base quality check: base low is available for stop and invalidation planning."
        )

    if not resistance_nearby(payload):
        score += 2
        reasons.append("Base quality check: no nearby major resistance is flagged.")
    else:
        reasons.append("Base quality check: base is close to a major resistance level.")

    return min(score, 25), reasons


def score_momentum(payload: BaseBreakoutInput) -> tuple[int, list[str]]:
    if has_valid_breakout_trigger(payload) and payload.close_near_high:
        return 15, ["Breakout confirmation: close is above base high and near the high."]
    if has_valid_breakout_trigger(payload):
        return 10, ["Breakout confirmation: close is above base high, but not near the high."]
    if payload.wick_above_base_high_only:
        return 4, ["Breakout confirmation: wick/spike exists but close confirmation is missing."]
    return 6, ["Breakout confirmation: base is forming but breakout is not confirmed yet."]


def score_volume(payload: BaseBreakoutInput) -> tuple[int, list[str]]:
    relative_volume = payload.daily.relative_volume
    if (
        payload.volume_drying_up
        and relative_volume is not None
        and relative_volume <= Decimal("1.0")
    ):
        return 15, ["Volume check: volume is drying up inside the base."]
    if payload.volume_drying_up:
        return 10, ["Volume check: base volume is marked as drying up, with limited metrics."]
    if relative_volume is not None and relative_volume > Decimal("1.5"):
        return 3, ["Volume check: volume is elevated and weakens base quality."]
    return 6, ["Volume check: volume pattern is mixed, so confidence is limited."]


def calculate_stop_loss(payload: BaseBreakoutInput) -> Decimal | None:
    if payload.base_low is None:
        return None
    atr_buffer = payload.daily.atr14 or Decimal("0")
    return payload.base_low - (atr_buffer * BREAKOUT_STOP_BUFFER_ATR)


def calculate_target(
    entry: Decimal | None, stop: Decimal | None, multiple: Decimal
) -> Decimal | None:
    if entry is None or stop is None or entry <= stop:
        return None
    return entry + ((entry - stop) * multiple)


def has_valid_breakout_trigger(payload: BaseBreakoutInput) -> bool:
    if payload.wick_above_base_high_only:
        return False
    return payload.close_above_base_high_4h or payload.close_above_base_high_daily


def base_is_too_wide(payload: BaseBreakoutInput) -> bool:
    if payload.base_high is None or payload.base_low is None or payload.base_low <= 0:
        return False
    return (payload.base_high - payload.base_low) / payload.base_low > MAX_BASE_WIDTH_PERCENT


def resistance_nearby(payload: BaseBreakoutInput) -> bool:
    if payload.major_resistance_level is None or payload.base_high is None:
        return False
    if payload.major_resistance_level <= payload.base_high:
        return True
    distance = (payload.major_resistance_level - payload.base_high) / payload.base_high
    return distance <= MAJOR_RESISTANCE_BUFFER


def breakout_is_extended(payload: BaseBreakoutInput) -> bool:
    if (
        payload.daily.close is None
        or payload.base_high is None
        or payload.daily.atr14 is None
        or payload.daily.atr14 <= 0
    ):
        return False
    return (
        (payload.daily.close - payload.base_high) / payload.daily.atr14
        > EXCESSIVE_BREAKOUT_ATR_MULTIPLE
    )


def ema20_or_ema50_rising_or_stable(payload: BaseBreakoutInput) -> bool:
    daily = payload.daily
    ema20_ok = (
        daily.ema20 is not None
        and payload.previous_ema20 is not None
        and daily.ema20 >= payload.previous_ema20
    )
    ema50_ok = (
        daily.ema50 is not None
        and payload.previous_ema50 is not None
        and daily.ema50 >= payload.previous_ema50
    )
    return ema20_ok or ema50_ok


def data_quality_flags(payload: BaseBreakoutInput) -> list[str]:
    flags: list[str] = []
    required_fields = {
        "daily_close_missing": payload.daily.close,
        "daily_ema200_missing": payload.daily.ema200,
        "daily_atr14_missing": payload.daily.atr14,
        "base_high_missing": payload.base_high,
        "base_low_missing": payload.base_low,
    }
    for flag, value in required_fields.items():
        if value is None:
            flags.append(flag)
    return flags


def initial_risk_flags(payload: BaseBreakoutInput) -> list[str]:
    flags: list[str] = []
    if base_is_too_wide(payload):
        flags.append("base_range_too_wide")
    if breakout_is_extended(payload):
        flags.append("breakout_extended_after_trigger")
    if payload.wick_above_base_high_only:
        flags.append("wick_without_close_confirmation")
    if not payload.volume_drying_up:
        flags.append("base_volume_not_drying_up")
    return flags


def invalidation_reason(payload: BaseBreakoutInput) -> str:
    if payload.base_low is not None:
        return "Close back inside the base or below base low invalidates the setup."
    return (
        "Setup invalidates if breakout fails, base structure breaks, "
        "or risk/reward falls below 2R."
    )


def next_action(has_trigger: bool, risk_reward: Decimal | None) -> str:
    if risk_reward is not None and risk_reward < Decimal("2.0"):
        return "No setup; risk/reward is below the minimum 2R requirement."
    if has_trigger:
        return "Review the armed breakout setup manually; no automatic trade is created."
    return "Keep on watchlist and wait for close confirmation above the base high."


def dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))

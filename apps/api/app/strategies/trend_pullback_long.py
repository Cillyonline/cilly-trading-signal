from dataclasses import dataclass, replace
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

PULLBACK_ZONE_TOLERANCE = Decimal("0.03")
OVEREXTENSION_ATR_MULTIPLE = Decimal("3")
AGGRESSIVE_RELATIVE_VOLUME = Decimal("1.5")
DEFAULT_ATR_BUFFER_MULTIPLE = Decimal("1")
TARGET_1_R_MULTIPLE = Decimal("2")
TARGET_2_R_MULTIPLE = Decimal("3")


@dataclass(frozen=True)
class TrendPullbackInput:
    signal_input: SignalEvaluationInput
    daily: IndicatorContext
    trigger: IndicatorContext
    previous_ema50: Decimal | None
    recent_swing_low: Decimal | None
    small_lower_high: Decimal | None
    close_above_small_lower_high: bool = False
    close_back_above_ema20: bool = False
    close_back_above_ema50: bool = False
    price_touch_only: bool = False
    pullback_low: Decimal | None = None
    support_level: Decimal | None = None
    previous_trend_clear: bool = True
    pullback_controlled: bool = True
    asset_liquid: bool = True
    strong_resistance_nearby: bool = False
    setup_invalidated: bool = False
    target_1_override: Decimal | None = None
    target_2_override: Decimal | None = None


def evaluate_trend_pullback_long(payload: TrendPullbackInput) -> SignalEvaluationResult:
    signal_input = SignalEvaluationInput(
        symbol=payload.signal_input.symbol,
        asset_class=payload.signal_input.asset_class,
        strategy_type=StrategyType.TREND_PULLBACK_LONG,
        weekly_bias=payload.signal_input.weekly_bias,
        daily_bias=payload.signal_input.daily_bias,
        context_timeframe=payload.signal_input.context_timeframe,
        setup_timeframe=payload.signal_input.setup_timeframe,
        trigger_timeframe=payload.signal_input.trigger_timeframe,
        weekly_indicators=payload.signal_input.weekly_indicators,
        daily_indicators=payload.daily,
        trigger_indicators=payload.trigger,
        data_quality_flags=[
            *payload.signal_input.data_quality_flags,
            *data_quality_flags(payload),
            *( ["uncontrolled_pullback"] if not payload.pullback_controlled else [] ),
        ],
        setup_invalidated=payload.signal_input.setup_invalidated or payload.setup_invalidated,
    )
    risk_flags = initial_risk_flags(payload)
    reasoning: list[str] = []

    trend_score, trend_reasons = score_trend(payload)
    structure_score, structure_reasons = score_structure(payload)
    momentum_score, momentum_reasons = score_momentum(payload)
    volume_score, volume_reasons = score_volume(payload)
    reasoning.extend(trend_reasons)
    reasoning.extend(structure_reasons)
    reasoning.extend(momentum_reasons)
    reasoning.extend(volume_reasons)

    entry_low = payload.daily.close
    entry_high = payload.trigger.close or payload.daily.close
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
    if target_1 is None:
        signal_input = replace(
            signal_input,
            data_quality_flags=[*signal_input.data_quality_flags, "missing_reward_target"],
        )

    risk_reward_score = 15 if risk_reward is not None and risk_reward >= Decimal("2.0") else 0
    if risk_reward is not None:
        reasoning.append(f"Risk/reward check produced {risk_reward:.2f}R.")
    else:
        reasoning.append("Risk/reward check could not be calculated from entry, stop, and target.")

    has_trigger = has_valid_trigger(payload)
    trigger_level = calculate_trigger_level(payload)
    if has_trigger:
        reasoning.append("Trigger check passed with 4H close confirmation.")
    elif payload.price_touch_only:
        reasoning.append("Trigger check failed because price touch alone is not confirmation.")
        risk_flags.append("price_touch_without_close_confirmation")
    else:
        reasoning.append("Trigger check is incomplete; wait for 4H close confirmation.")

    if payload.strong_resistance_nearby:
        risk_flags.append("strong_resistance_nearby")
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
        trigger_level=trigger_level,
        stop_loss=stop_loss,
        target_1=target_1,
        target_2=target_2,
        risk_reward=risk_reward,
        invalidation_reason=invalidation_reason(payload),
        has_valid_trigger_plan=(
            has_trigger and risk_reward is not None and risk_reward >= Decimal("2.0")
        ),
    )


def score_trend(payload: TrendPullbackInput) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    daily = payload.daily

    if daily.close is not None and daily.ema200 is not None and daily.close > daily.ema200:
        score += 10
        reasons.append("Trend check: daily close is above EMA200.")
    else:
        reasons.append("Trend check: daily close is not confirmed above EMA200.")

    if daily.ema20 is not None and daily.ema50 is not None and daily.ema20 > daily.ema50:
        score += 8
        reasons.append("Trend check: EMA20 is above EMA50.")
    elif ema50_is_rising(payload):
        score += 6
        reasons.append("Trend check: EMA50 is rising versus prior daily close proxy.")
    else:
        reasons.append("Trend check: EMA20/EMA50 trend confirmation is missing.")

    if payload.previous_trend_clear:
        score += 5
        reasons.append("Trend check: previous uptrend is clear enough for MVP evaluation.")
    else:
        reasons.append("Trend check: previous uptrend is not clear enough for high confidence.")
    if not is_overextended(payload):
        score += 2
        reasons.append("Trend check: price is not extremely extended versus EMA20/ATR.")
    else:
        reasons.append("Trend check: price appears extended versus EMA20/ATR.")

    return min(score, 25), reasons


def score_structure(payload: TrendPullbackInput) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    if is_near_pullback_zone(payload):
        score += 10
        reasons.append("Pullback check: price is near EMA20, EMA50, or support.")
    else:
        reasons.append("Pullback check: price is not near a defined pullback zone.")

    if payload.pullback_controlled:
        score += 6
        reasons.append("Pullback check: pullback is marked as controlled.")
    else:
        reasons.append("Pullback check: pullback control is not confirmed.")

    if payload.recent_swing_low is not None and payload.daily.close is not None:
        if payload.daily.close > payload.recent_swing_low:
            score += 5
            reasons.append("Structure check: daily close remains above recent swing low.")
        else:
            reasons.append("Structure check: daily close lost the recent swing low.")

    if payload.support_level is not None:
        score += 4
        reasons.append("Structure check: support level is available for invalidation planning.")

    return min(score, 25), reasons


def score_momentum(payload: TrendPullbackInput) -> tuple[int, list[str]]:
    rsi = payload.daily.rsi14
    if rsi is None:
        return 0, ["Momentum check: RSI14 is missing."]
    if Decimal("40") <= rsi <= Decimal("60"):
        return 15, ["Momentum check: RSI14 is in the ideal 40-60 pullback zone."]
    if Decimal("35") <= rsi < Decimal("40") or Decimal("60") < rsi <= Decimal("70"):
        return 8, ["Momentum check: RSI14 is acceptable but outside the ideal zone."]
    return 0, ["Momentum check: RSI14 is outside the acceptable pullback zone."]


def score_volume(payload: TrendPullbackInput) -> tuple[int, list[str]]:
    relative_volume = payload.daily.relative_volume
    if relative_volume is None:
        return 5, ["Volume check: relative volume is missing, so volume confidence is limited."]
    if relative_volume <= Decimal("1.0"):
        return 15, ["Volume check: pullback volume is quiet versus the 20-period average."]
    if relative_volume <= AGGRESSIVE_RELATIVE_VOLUME:
        return 8, ["Volume check: pullback volume is elevated but not aggressive."]
    return 0, ["Volume check: pullback volume is aggressive and weakens the setup."]


def calculate_stop_loss(payload: TrendPullbackInput) -> Decimal | None:
    if payload.recent_swing_low is None:
        return None
    atr_buffer = payload.daily.atr14 or Decimal("0")
    return payload.recent_swing_low - (atr_buffer * DEFAULT_ATR_BUFFER_MULTIPLE)


def calculate_target(
    entry: Decimal | None, stop: Decimal | None, multiple: Decimal
) -> Decimal | None:
    if entry is None or stop is None or entry <= stop:
        return None
    return entry + ((entry - stop) * multiple)


def calculate_trigger_level(payload: TrendPullbackInput) -> Decimal | None:
    if payload.small_lower_high is not None:
        return payload.small_lower_high
    if payload.close_back_above_ema20:
        return payload.trigger.ema20
    if payload.close_back_above_ema50:
        return payload.trigger.ema50
    return None


def has_valid_trigger(payload: TrendPullbackInput) -> bool:
    if payload.price_touch_only:
        return False
    return (
        payload.close_above_small_lower_high
        or payload.close_back_above_ema20
        or payload.close_back_above_ema50
    )


def is_near_pullback_zone(payload: TrendPullbackInput) -> bool:
    price = payload.daily.close
    if price is None:
        return False
    zones = [payload.daily.ema20, payload.daily.ema50, payload.support_level]
    return any(zone is not None and within_tolerance(price, zone) for zone in zones)


def within_tolerance(price: Decimal, level: Decimal) -> bool:
    if level <= 0:
        return False
    distance = abs(price - level) / level
    return distance <= PULLBACK_ZONE_TOLERANCE


def ema50_is_rising(payload: TrendPullbackInput) -> bool:
    daily = payload.daily
    if daily.ema50 is None or payload.previous_ema50 is None:
        return False
    return daily.ema50 > payload.previous_ema50


def is_overextended(payload: TrendPullbackInput) -> bool:
    daily = payload.daily
    if daily.close is None or daily.ema20 is None or daily.atr14 is None or daily.atr14 <= 0:
        return False
    return (daily.close - daily.ema20) / daily.atr14 > OVEREXTENSION_ATR_MULTIPLE


def data_quality_flags(payload: TrendPullbackInput) -> list[str]:
    flags: list[str] = []
    required_daily_fields = {
        "daily_close_missing": payload.daily.close,
        "daily_ema20_missing": payload.daily.ema20,
        "daily_ema50_missing": payload.daily.ema50,
        "daily_ema200_missing": payload.daily.ema200,
        "daily_rsi14_missing": payload.daily.rsi14,
        "daily_atr14_missing": payload.daily.atr14,
    }
    for flag, value in required_daily_fields.items():
        if value is None:
            flags.append(flag)
    if payload.recent_swing_low is None:
        flags.append("recent_swing_low_missing")
    return flags


def initial_risk_flags(payload: TrendPullbackInput) -> list[str]:
    flags: list[str] = []
    if is_overextended(payload):
        flags.append("price_extended_vs_ema20_atr")
    if not payload.pullback_controlled:
        flags.append("pullback_control_unclear")
        flags.append("uncontrolled_pullback")
    if (
        payload.daily.relative_volume is not None
        and payload.daily.relative_volume > AGGRESSIVE_RELATIVE_VOLUME
    ):
        flags.append("aggressive_pullback_volume")
    return flags


def invalidation_reason(payload: TrendPullbackInput) -> str:
    if payload.support_level is not None:
        return "Daily close below support or EMA50 with structure break invalidates the setup."
    if payload.recent_swing_low is not None:
        return "Daily close below the recent swing low invalidates the setup."
    return "Setup invalidates if trend context turns bearish or risk/reward falls below 2R."


def next_action(has_trigger: bool, risk_reward: Decimal | None) -> str:
    if risk_reward is not None and risk_reward < Decimal("2.0"):
        return "No setup; risk/reward is below the minimum 2R requirement."
    if has_trigger:
        return "Review the armed pullback setup manually; no automatic trade is created."
    return "Keep on watchlist and wait for 4H close confirmation before considering action."


def dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))

from dataclasses import dataclass, field
from decimal import Decimal

from app.models.enums import AssetClass, Bias, ScoreClass, SignalStatus, StrategyType, Timeframe

MIN_RISK_REWARD = Decimal("2.0")

NO_TRADE_REASON_MESSAGES = {
    "stock_market_regime_bearish": (
        "No Trade: stored stock benchmark context is bearish for long-only review."
    ),
    "crypto_regime_bearish": (
        "No Trade: stored BTC/ETH regime context is bearish for long-only review."
    ),
    "relative_strength_underperforming": (
        "No Trade: candidate is materially underperforming available benchmark context."
    ),
    "weekly_context_bearish": (
        "No Trade: weekly context is bearish, so long-only setup review is blocked."
    ),
    "daily_context_bearish": (
        "No Trade: daily context is bearish, so long-only setup review is blocked."
    ),
    "risk_reward_below_minimum": "No Trade: planned reward is below the minimum 2R requirement.",
    "missing_stop_loss": "No Trade: stop loss is missing, so risk cannot be defined.",
    "missing_reward_target": "No Trade: reward target is missing, so R:R cannot be validated.",
    "entry_not_above_stop": "No Trade: entry is not above stop, so the long risk plan is invalid.",
    "poor_data_quality": (
        "No Trade: required data is missing, stale, partial, or otherwise insufficient."
    ),
    "required_timeframe_data_missing": (
        "No Trade: one or more required timeframes are missing for setup review."
    ),
    "required_market_data_not_fresh": (
        "No Trade: required market data is stale, partial, failed, missing, or unknown."
    ),
    "insufficient_candle_history": (
        "No Trade: candle history is too short for reliable indicator and setup review."
    ),
    "required_indicator_missing": (
        "No Trade: required indicator context is missing after analysis."
    ),
    "setup_already_invalidated": (
        "No Trade: setup is already invalidated by the stored analysis state."
    ),
    "pullback_not_controlled": "No Trade: pullback is not controlled enough for this strategy.",
    "pullback_volume_aggressive": (
        "No Trade: pullback volume is aggressive, so selling pressure is not controlled."
    ),
    "base_too_wide": "No Trade: base range is too wide for clean risk planning.",
    "breakout_too_extended": "No Trade: breakout is extended beyond the trigger zone.",
    "breakout_close_not_near_high": (
        "No Trade: breakout close is not near the high, so confirmation quality is weak."
    ),
    "base_high_not_clear": "No Trade: base high is not clear enough for breakout review.",
    "strong_resistance_nearby": "No Trade: setup is directly below strong resistance.",
}

NO_TRADE_NEXT_ACTIONS = {
    "stock_market_regime_bearish": (
        "Wait for stored SPY/QQQ context to recover before reviewing new stock long setups."
    ),
    "crypto_regime_bearish": (
        "Wait for stored BTC/ETH context to recover before reviewing new crypto long setups."
    ),
    "relative_strength_underperforming": (
        "Keep it off the active list until relative strength improves versus stored benchmark "
        "context."
    ),
    "weekly_context_bearish": (
        "Wait for weekly context to turn neutral or bullish before manual long review."
    ),
    "daily_context_bearish": "Wait for daily trend context to repair before manual long review.",
    "risk_reward_below_minimum": (
        "Adjust the plan only if structure supports at least 2R; otherwise skip this setup."
    ),
    "missing_stop_loss": "Define a technical stop below structure before reviewing any trigger.",
    "missing_reward_target": (
        "Define a structure-based or minimum-R target before reviewing any trigger."
    ),
    "entry_not_above_stop": (
        "Rebuild the entry and stop plan; the current long risk plan is invalid."
    ),
    "poor_data_quality": (
        "Refresh or provide the missing/stale timeframe and benchmark data before review."
    ),
    "required_timeframe_data_missing": (
        "Import all required timeframes before reviewing this long setup."
    ),
    "required_market_data_not_fresh": (
        "Refresh stale, partial, failed, missing, or unknown market data before review."
    ),
    "insufficient_candle_history": (
        "Provide enough candle history for the required indicators before review."
    ),
    "required_indicator_missing": (
        "Re-run analysis after indicator context is available; otherwise keep No Trade."
    ),
    "setup_already_invalidated": (
        "Wait for a fresh setup instead of reusing the invalidated structure."
    ),
    "pullback_not_controlled": (
        "Wait for price to stabilize and reclaim a valid trigger level with close confirmation."
    ),
    "pullback_volume_aggressive": (
        "Wait for quieter pullback volume before reviewing this trend-pullback setup."
    ),
    "base_too_wide": "Wait for a tighter base with a clearer stop and invalidation level.",
    "breakout_too_extended": (
        "Wait for a reset, retest, or new base instead of chasing the extended move."
    ),
    "breakout_close_not_near_high": (
        "Wait for a stronger close near the high before reviewing this breakout."
    ),
    "base_high_not_clear": "Wait for a clearer base high before reviewing breakout confirmation.",
    "strong_resistance_nearby": (
        "Wait for price to clear resistance or form a new setup with room for at least 2R."
    ),
}


@dataclass(frozen=True)
class IndicatorContext:
    close: Decimal | None = None
    ema20: Decimal | None = None
    ema50: Decimal | None = None
    ema200: Decimal | None = None
    rsi14: Decimal | None = None
    atr14: Decimal | None = None
    volume_avg20: Decimal | None = None
    relative_volume: Decimal | None = None


@dataclass(frozen=True)
class SignalEvaluationInput:
    symbol: str
    asset_class: AssetClass
    strategy_type: StrategyType
    weekly_bias: Bias
    daily_bias: Bias
    context_timeframe: Timeframe = Timeframe.ONE_WEEK
    setup_timeframe: Timeframe = Timeframe.ONE_DAY
    trigger_timeframe: Timeframe = Timeframe.FOUR_HOURS
    weekly_indicators: IndicatorContext = field(default_factory=IndicatorContext)
    daily_indicators: IndicatorContext = field(default_factory=IndicatorContext)
    trigger_indicators: IndicatorContext = field(default_factory=IndicatorContext)
    data_quality_flags: list[str] = field(default_factory=list)
    context_risk_flags: list[str] = field(default_factory=list)
    context_no_trade_reasons: list[str] = field(default_factory=list)
    score_cap: int | None = None
    setup_invalidated: bool = False


@dataclass(frozen=True)
class ScoreBreakdown:
    trend: int = 0
    structure: int = 0
    momentum: int = 0
    volume: int = 0
    risk_reward: int = 0
    risk_filters: int = 0

    def __post_init__(self) -> None:
        bounds = {
            "trend": (0, 25),
            "structure": (0, 25),
            "momentum": (0, 15),
            "volume": (0, 15),
            "risk_reward": (0, 15),
            "risk_filters": (-20, 0),
        }
        for field_name, (minimum, maximum) in bounds.items():
            value = getattr(self, field_name)
            if not minimum <= value <= maximum:
                raise ValueError(f"{field_name} score must be between {minimum} and {maximum}.")

    @property
    def total(self) -> int:
        return max(
            0,
            min(
                100,
                self.trend
                + self.structure
                + self.momentum
                + self.volume
                + self.risk_reward
                + self.risk_filters,
            ),
        )


@dataclass(frozen=True)
class SignalEvaluationResult:
    strategy_type: StrategyType
    status: SignalStatus
    bias: Bias
    score: int
    score_class: ScoreClass
    timeframe_context: Timeframe
    timeframe_setup: Timeframe
    timeframe_trigger: Timeframe
    entry_low: Decimal | None
    entry_high: Decimal | None
    trigger_level: Decimal | None
    stop_loss: Decimal | None
    target_1: Decimal | None
    target_2: Decimal | None
    risk_reward: Decimal | None
    invalidation_reason: str | None
    reasoning: list[str]
    risk_flags: list[str]
    next_action: str
    no_trade_reasons: list[str]

    def __post_init__(self) -> None:
        if self.status == SignalStatus.TRIGGERED:
            raise ValueError("MVP signal evaluation must not emit triggered status.")
        if not self.reasoning:
            raise ValueError("Signal evaluation must include reasoning.")
        if not self.next_action:
            raise ValueError("Signal evaluation must include a next action.")

    def to_signal_kwargs(self) -> dict[str, object]:
        return {
            "strategy_type": self.strategy_type,
            "status": self.status,
            "bias": self.bias,
            "score": self.score,
            "score_class": self.score_class,
            "timeframe_context": self.timeframe_context,
            "timeframe_setup": self.timeframe_setup,
            "timeframe_trigger": self.timeframe_trigger,
            "entry_low": self.entry_low,
            "entry_high": self.entry_high,
            "trigger_level": self.trigger_level,
            "stop_loss": self.stop_loss,
            "target_1": self.target_1,
            "target_2": self.target_2,
            "risk_reward": self.risk_reward,
            "invalidation_reason": self.invalidation_reason,
            "reasoning": self.reasoning,
            "risk_flags": self.risk_flags,
            "no_trade_reasons": self.no_trade_reasons,
            "next_action": self.next_action,
        }


def classify_score(score: int) -> ScoreClass:
    bounded_score = max(0, min(100, score))
    if bounded_score >= 80:
        return ScoreClass.A_SETUP
    if bounded_score >= 65:
        return ScoreClass.B_SETUP
    if bounded_score >= 50:
        return ScoreClass.WATCHLIST
    return ScoreClass.NO_TRADE


def map_status(score_class: ScoreClass, has_valid_trigger_plan: bool) -> SignalStatus:
    if score_class == ScoreClass.NO_TRADE:
        return SignalStatus.NO_SETUP
    if score_class == ScoreClass.WATCHLIST:
        return SignalStatus.WATCHLIST
    if has_valid_trigger_plan:
        return SignalStatus.ARMED
    return SignalStatus.WATCHLIST


def calculate_risk_reward(entry: Decimal, stop: Decimal, target: Decimal) -> Decimal | None:
    risk = entry - stop
    if risk <= 0:
        return None
    reward = target - entry
    if reward <= 0:
        return None
    return reward / risk


def collect_common_no_trade_reasons(
    signal_input: SignalEvaluationInput,
    entry: Decimal | None = None,
    stop: Decimal | None = None,
    risk_reward: Decimal | None = None,
) -> list[str]:
    reasons: list[str] = []

    if risk_reward is not None and risk_reward < MIN_RISK_REWARD:
        reasons.append("risk_reward_below_minimum")
    if signal_input.weekly_bias == Bias.BEARISH:
        reasons.append("weekly_context_bearish")
    if signal_input.daily_bias == Bias.BEARISH:
        reasons.append("daily_context_bearish")
    if stop is None:
        reasons.append("missing_stop_loss")
    if entry is not None and stop is not None and entry <= stop:
        reasons.append("entry_not_above_stop")
    reasons.extend(data_quality_no_trade_reasons(signal_input.data_quality_flags))
    if signal_input.setup_invalidated:
        reasons.append("setup_already_invalidated")
    if "missing_reward_target" in signal_input.data_quality_flags:
        reasons.append("missing_reward_target")
    if "uncontrolled_pullback" in signal_input.data_quality_flags:
        reasons.append("pullback_not_controlled")
    if "aggressive_pullback_volume" in signal_input.data_quality_flags:
        reasons.append("pullback_volume_aggressive")
    if "base_range_too_wide" in signal_input.data_quality_flags:
        reasons.append("base_too_wide")
    if "breakout_extended_after_trigger" in signal_input.data_quality_flags:
        reasons.append("breakout_too_extended")
    if "breakout_close_not_near_high" in signal_input.data_quality_flags:
        reasons.append("breakout_close_not_near_high")
    if "base_high_not_clear" in signal_input.data_quality_flags:
        reasons.append("base_high_not_clear")
    if "strong_resistance_nearby" in signal_input.data_quality_flags:
        reasons.append("strong_resistance_nearby")
    reasons.extend(signal_input.context_no_trade_reasons)

    return dedupe(reasons)


def data_quality_no_trade_reasons(flags: list[str]) -> list[str]:
    reasons: list[str] = []
    for flag in flags:
        if flag.startswith("missing_") and flag.endswith("_data"):
            reasons.append("required_timeframe_data_missing")
        elif flag.startswith("market_data_"):
            reasons.append("required_market_data_not_fresh")
        elif flag.endswith("_insufficient_candle_history"):
            reasons.append("insufficient_candle_history")
        elif flag.endswith("_ema200_missing"):
            reasons.append("required_indicator_missing")

    known_gate_flags = {
        "missing_reward_target",
        "uncontrolled_pullback",
        "base_range_too_wide",
        "breakout_extended_after_trigger",
        "base_high_not_clear",
        "strong_resistance_nearby",
    }
    has_unmapped_quality_flags = any(
        flag not in known_gate_flags
        and not (flag.startswith("missing_") and flag.endswith("_data"))
        and not flag.startswith("market_data_")
        and not flag.endswith("_insufficient_candle_history")
        and not flag.endswith("_ema200_missing")
        for flag in flags
    )
    if flags and not reasons and has_unmapped_quality_flags:
        reasons.append("poor_data_quality")

    return dedupe(reasons)


def build_signal_result(
    signal_input: SignalEvaluationInput,
    score_breakdown: ScoreBreakdown,
    bias: Bias,
    reasoning: list[str],
    risk_flags: list[str],
    next_action: str,
    entry_low: Decimal | None = None,
    entry_high: Decimal | None = None,
    trigger_level: Decimal | None = None,
    stop_loss: Decimal | None = None,
    target_1: Decimal | None = None,
    target_2: Decimal | None = None,
    risk_reward: Decimal | None = None,
    invalidation_reason: str | None = None,
    has_valid_trigger_plan: bool = False,
) -> SignalEvaluationResult:
    no_trade_reasons = collect_common_no_trade_reasons(
        signal_input,
        entry=entry_low,
        stop=stop_loss,
        risk_reward=risk_reward,
    )
    score = score_breakdown.total
    if signal_input.score_cap is not None:
        score = min(score, signal_input.score_cap)
    score_class = classify_score(score)
    status = map_status(score_class, has_valid_trigger_plan)

    if no_trade_reasons:
        score_class = ScoreClass.NO_TRADE
        status = SignalStatus.NO_SETUP

    merged_risk_flags = [*risk_flags, *signal_input.context_risk_flags, *no_trade_reasons]
    merged_reasoning = [*reasoning]
    if signal_input.score_cap is not None and score == signal_input.score_cap:
        merged_reasoning.append("Market context cap applied; confidence remains below A-Setup.")
    if no_trade_reasons:
        merged_reasoning.extend(explain_no_trade_reasons(no_trade_reasons))
        next_action = next_action_for_no_trade(no_trade_reasons)

    return SignalEvaluationResult(
        strategy_type=signal_input.strategy_type,
        status=status,
        bias=bias,
        score=score,
        score_class=score_class,
        timeframe_context=signal_input.context_timeframe,
        timeframe_setup=signal_input.setup_timeframe,
        timeframe_trigger=signal_input.trigger_timeframe,
        entry_low=entry_low,
        entry_high=entry_high,
        trigger_level=trigger_level,
        stop_loss=stop_loss,
        target_1=target_1,
        target_2=target_2,
        risk_reward=risk_reward,
        invalidation_reason=invalidation_reason,
        reasoning=merged_reasoning,
        risk_flags=merged_risk_flags,
        next_action=next_action,
        no_trade_reasons=no_trade_reasons,
    )


def explain_no_trade_reasons(reasons: list[str]) -> list[str]:
    return [NO_TRADE_REASON_MESSAGES.get(reason, f"No Trade: {reason}.") for reason in reasons]


def next_action_for_no_trade(reasons: list[str]) -> str:
    for reason in reasons:
        action = NO_TRADE_NEXT_ACTIONS.get(reason)
        if action is not None:
            return action
    return "No setup; wait for clearer context, structure, trigger, and risk before manual review."


def dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))

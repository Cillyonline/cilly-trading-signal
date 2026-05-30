from dataclasses import dataclass, field
from decimal import Decimal

from app.models.enums import AssetClass, Bias, ScoreClass, SignalStatus, StrategyType, Timeframe

MIN_RISK_REWARD = Decimal("2.0")


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
    if signal_input.data_quality_flags:
        reasons.append("poor_data_quality")
    if signal_input.setup_invalidated:
        reasons.append("setup_already_invalidated")
    if "missing_reward_target" in signal_input.data_quality_flags:
        reasons.append("missing_reward_target")
    if "uncontrolled_pullback" in signal_input.data_quality_flags:
        reasons.append("pullback_not_controlled")
    if "base_range_too_wide" in signal_input.data_quality_flags:
        reasons.append("base_too_wide")
    if "breakout_extended_after_trigger" in signal_input.data_quality_flags:
        reasons.append("breakout_too_extended")
    if "base_high_not_clear" in signal_input.data_quality_flags:
        reasons.append("base_high_not_clear")
    reasons.extend(signal_input.context_no_trade_reasons)

    return reasons


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
        merged_reasoning.append("Hard No-Trade rule applied; setup remains No Setup.")

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

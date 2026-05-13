from dataclasses import dataclass

from app.models.enums import Bias, ScoreClass, SignalStatus, StrategyType
from app.strategies.base_breakout_long import BaseBreakoutInput, evaluate_base_breakout_long
from app.strategies.contracts import (
    ScoreBreakdown,
    SignalEvaluationInput,
    SignalEvaluationResult,
    build_signal_result,
)
from app.strategies.trend_pullback_long import (
    TrendPullbackInput,
    evaluate_trend_pullback_long,
)

STATUS_PRIORITY = {
    SignalStatus.ARMED: 3,
    SignalStatus.WATCHLIST: 2,
    SignalStatus.NO_SETUP: 1,
}
STRATEGY_PRIORITY = {
    StrategyType.TREND_PULLBACK_LONG: 2,
    StrategyType.BASE_BREAKOUT_LONG: 1,
}


@dataclass(frozen=True)
class SignalEngineInput:
    fallback_input: SignalEvaluationInput
    trend_pullback: TrendPullbackInput | None = None
    base_breakout: BaseBreakoutInput | None = None


def evaluate_mvp_signal_engine(payload: SignalEngineInput) -> SignalEvaluationResult:
    results: list[SignalEvaluationResult] = []
    if payload.trend_pullback is not None:
        results.append(evaluate_trend_pullback_long(payload.trend_pullback))
    if payload.base_breakout is not None:
        results.append(evaluate_base_breakout_long(payload.base_breakout))

    if not results:
        return no_setup_result(payload.fallback_input, ["No MVP strategy input was provided."])

    candidates = [result for result in results if result.status != SignalStatus.NO_SETUP]
    if not candidates:
        return merge_no_setup_results(payload.fallback_input, results)

    return max(candidates, key=result_rank)


def result_rank(result: SignalEvaluationResult) -> tuple[int, int, int]:
    return (
        STATUS_PRIORITY[result.status],
        result.score,
        STRATEGY_PRIORITY[result.strategy_type],
    )


def merge_no_setup_results(
    fallback_input: SignalEvaluationInput, results: list[SignalEvaluationResult]
) -> SignalEvaluationResult:
    best_result = max(
        results,
        key=lambda result: (result.score, STRATEGY_PRIORITY[result.strategy_type]),
    )
    reasons = dedupe(reason for result in results for reason in result.no_trade_reasons)
    risk_flags = dedupe(flag for result in results for flag in result.risk_flags)
    reasoning = [
        "No MVP strategy produced a valid setup candidate.",
        *[reason for result in results for reason in result.reasoning],
    ]

    return SignalEvaluationResult(
        strategy_type=best_result.strategy_type,
        status=SignalStatus.NO_SETUP,
        bias=Bias.NEUTRAL,
        score=best_result.score,
        score_class=ScoreClass.NO_TRADE,
        timeframe_context=fallback_input.context_timeframe,
        timeframe_setup=fallback_input.setup_timeframe,
        timeframe_trigger=fallback_input.trigger_timeframe,
        entry_low=best_result.entry_low,
        entry_high=best_result.entry_high,
        trigger_level=best_result.trigger_level,
        stop_loss=best_result.stop_loss,
        target_1=best_result.target_1,
        target_2=best_result.target_2,
        risk_reward=best_result.risk_reward,
        invalidation_reason=best_result.invalidation_reason,
        reasoning=reasoning,
        risk_flags=risk_flags,
        next_action="No setup; wait for clearer conditions before manual review.",
        no_trade_reasons=reasons or ["no_valid_strategy_candidate"],
    )


def no_setup_result(
    fallback_input: SignalEvaluationInput, reasoning: list[str]
) -> SignalEvaluationResult:
    return build_signal_result(
        fallback_input,
        ScoreBreakdown(),
        bias=Bias.NEUTRAL,
        reasoning=reasoning,
        risk_flags=["no_strategy_input"],
        next_action="No setup; provide strategy inputs before evaluating a signal.",
        stop_loss=None,
    )


def dedupe(values: object) -> list[str]:
    return list(dict.fromkeys(values))

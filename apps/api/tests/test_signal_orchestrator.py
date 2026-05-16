from decimal import Decimal

from app.models.enums import AssetClass, Bias, ScoreClass, SignalStatus, StrategyType
from app.strategies.base_breakout_long import BaseBreakoutInput
from app.strategies.contracts import IndicatorContext, SignalEvaluationInput
from app.strategies.orchestrator import SignalEngineInput, evaluate_mvp_signal_engine
from app.strategies.trend_pullback_long import TrendPullbackInput


def fallback_input(
    strategy_type: StrategyType = StrategyType.TREND_PULLBACK_LONG,
    weekly_bias: Bias = Bias.BULLISH,
) -> SignalEvaluationInput:
    return SignalEvaluationInput(
        symbol="AAPL",
        asset_class=AssetClass.STOCK,
        strategy_type=strategy_type,
        weekly_bias=weekly_bias,
        daily_bias=Bias.BULLISH,
    )


def trend_pullback_input(weekly_bias: Bias = Bias.BULLISH) -> TrendPullbackInput:
    return TrendPullbackInput(
        signal_input=fallback_input(StrategyType.TREND_PULLBACK_LONG, weekly_bias=weekly_bias),
        daily=IndicatorContext(
            close=Decimal("100"),
            ema20=Decimal("98"),
            ema50=Decimal("94"),
            ema200=Decimal("80"),
            rsi14=Decimal("52"),
            atr14=Decimal("2"),
            relative_volume=Decimal("0.8"),
        ),
        trigger=IndicatorContext(close=Decimal("101"), ema20=Decimal("100")),
        previous_ema50=Decimal("93"),
        recent_swing_low=Decimal("94"),
        small_lower_high=Decimal("101"),
        close_above_small_lower_high=True,
        support_level=Decimal("96"),
    )


def base_breakout_input(weekly_bias: Bias = Bias.BULLISH) -> BaseBreakoutInput:
    return BaseBreakoutInput(
        signal_input=fallback_input(StrategyType.BASE_BREAKOUT_LONG, weekly_bias=weekly_bias),
        daily=IndicatorContext(
            close=Decimal("103"),
            ema20=Decimal("99"),
            ema50=Decimal("97"),
            ema200=Decimal("80"),
            atr14=Decimal("2"),
            relative_volume=Decimal("0.8"),
        ),
        trigger=IndicatorContext(close=Decimal("103")),
        previous_ema20=Decimal("98"),
        previous_ema50=Decimal("96"),
        base_high=Decimal("100"),
        base_low=Decimal("94"),
        base_days=8,
        close_above_base_high_4h=True,
    )


def test_no_strategy_input_returns_no_setup() -> None:
    result = evaluate_mvp_signal_engine(SignalEngineInput(fallback_input=fallback_input()))

    assert result.status == SignalStatus.NO_SETUP
    assert result.score_class == ScoreClass.NO_TRADE
    assert result.no_trade_reasons == ["missing_stop_loss"]
    assert "no_strategy_input" in result.risk_flags


def test_only_trend_pullback_valid_returns_trend_pullback_result() -> None:
    result = evaluate_mvp_signal_engine(
        SignalEngineInput(
            fallback_input=fallback_input(),
            trend_pullback=trend_pullback_input(),
        )
    )

    assert result.strategy_type == StrategyType.TREND_PULLBACK_LONG
    assert result.status == SignalStatus.ARMED


def test_only_base_breakout_valid_returns_base_breakout_result() -> None:
    result = evaluate_mvp_signal_engine(
        SignalEngineInput(
            fallback_input=fallback_input(),
            base_breakout=base_breakout_input(),
        )
    )

    assert result.strategy_type == StrategyType.BASE_BREAKOUT_LONG
    assert result.status == SignalStatus.ARMED


def test_both_valid_selects_highest_quality_deterministically() -> None:
    result = evaluate_mvp_signal_engine(
        SignalEngineInput(
            fallback_input=fallback_input(),
            trend_pullback=trend_pullback_input(),
            base_breakout=base_breakout_input(),
        )
    )

    assert result.status == SignalStatus.ARMED
    assert result.strategy_type == StrategyType.TREND_PULLBACK_LONG


def test_no_trade_rule_blocks_otherwise_valid_setups() -> None:
    result = evaluate_mvp_signal_engine(
        SignalEngineInput(
            fallback_input=fallback_input(),
            trend_pullback=trend_pullback_input(weekly_bias=Bias.BEARISH),
            base_breakout=base_breakout_input(weekly_bias=Bias.BEARISH),
        )
    )

    assert result.status == SignalStatus.NO_SETUP
    assert result.score_class == ScoreClass.NO_TRADE
    assert "weekly_context_bearish" in result.no_trade_reasons


def test_output_has_signal_compatible_fields_and_no_trade_fields() -> None:
    result = evaluate_mvp_signal_engine(
        SignalEngineInput(fallback_input=fallback_input(), trend_pullback=trend_pullback_input())
    )
    signal_kwargs = result.to_signal_kwargs()

    assert set(signal_kwargs) == {
        "strategy_type",
        "status",
        "bias",
        "score",
        "score_class",
        "timeframe_context",
        "timeframe_setup",
        "timeframe_trigger",
        "entry_low",
        "entry_high",
        "trigger_level",
        "stop_loss",
        "target_1",
        "target_2",
        "risk_reward",
        "invalidation_reason",
        "reasoning",
        "risk_flags",
        "no_trade_reasons",
        "next_action",
    }
    assert "trade" not in signal_kwargs
    assert "alert" not in signal_kwargs
    assert result.reasoning
    assert result.next_action


def test_output_avoids_buy_sell_instruction_language() -> None:
    result = evaluate_mvp_signal_engine(
        SignalEngineInput(fallback_input=fallback_input(), trend_pullback=trend_pullback_input())
    )
    text = " ".join([*result.reasoning, result.next_action]).lower()

    assert "buy" not in text
    assert "sell" not in text
    assert "automatic trade" in text

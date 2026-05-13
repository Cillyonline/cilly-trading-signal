from decimal import Decimal

from app.models.enums import AssetClass, Bias, ScoreClass, SignalStatus, StrategyType
from app.strategies.contracts import IndicatorContext, SignalEvaluationInput
from app.strategies.trend_pullback_long import (
    TrendPullbackInput,
    evaluate_trend_pullback_long,
)


def base_signal_input(weekly_bias: Bias = Bias.BULLISH) -> SignalEvaluationInput:
    return SignalEvaluationInput(
        symbol="AAPL",
        asset_class=AssetClass.STOCK,
        strategy_type=StrategyType.TREND_PULLBACK_LONG,
        weekly_bias=weekly_bias,
        daily_bias=Bias.BULLISH,
    )


def base_daily_context() -> IndicatorContext:
    return IndicatorContext(
        close=Decimal("100"),
        ema20=Decimal("98"),
        ema50=Decimal("94"),
        ema200=Decimal("80"),
        rsi14=Decimal("52"),
        atr14=Decimal("2"),
        relative_volume=Decimal("0.8"),
    )


def base_trigger_context() -> IndicatorContext:
    return IndicatorContext(
        close=Decimal("101"),
        ema20=Decimal("100"),
        ema50=Decimal("96"),
    )


def trend_payload(**overrides: object) -> TrendPullbackInput:
    payload = {
        "signal_input": base_signal_input(),
        "daily": base_daily_context(),
        "trigger": base_trigger_context(),
        "previous_ema50": Decimal("93"),
        "recent_swing_low": Decimal("94"),
        "small_lower_high": Decimal("101"),
        "close_above_small_lower_high": True,
        "close_back_above_ema20": False,
        "close_back_above_ema50": False,
        "price_touch_only": False,
        "support_level": Decimal("96"),
    }
    payload.update(overrides)
    return TrendPullbackInput(**payload)


def test_valid_trend_pullback_long_produces_armed() -> None:
    result = evaluate_trend_pullback_long(trend_payload())

    assert result.strategy_type == StrategyType.TREND_PULLBACK_LONG
    assert result.status == SignalStatus.ARMED
    assert result.score_class == ScoreClass.A_SETUP
    assert result.entry_low == Decimal("100")
    assert result.entry_high == Decimal("101")
    assert result.trigger_level == Decimal("101")
    assert result.stop_loss == Decimal("92")
    assert result.target_1 == Decimal("116")
    assert result.target_2 == Decimal("124")
    assert result.risk_reward == Decimal("2")
    assert result.invalidation_reason is not None
    assert result.no_trade_reasons == []


def test_incomplete_trend_pullback_long_produces_watchlist() -> None:
    result = evaluate_trend_pullback_long(
        trend_payload(
            close_above_small_lower_high=False,
            close_back_above_ema20=False,
            close_back_above_ema50=False,
            small_lower_high=Decimal("102"),
        )
    )

    assert result.status == SignalStatus.WATCHLIST
    assert result.score_class in {ScoreClass.A_SETUP, ScoreClass.B_SETUP}
    assert result.status != SignalStatus.TRIGGERED
    assert "wait for 4H close confirmation" in result.next_action


def test_bearish_weekly_context_forces_no_setup() -> None:
    result = evaluate_trend_pullback_long(
        trend_payload(signal_input=base_signal_input(weekly_bias=Bias.BEARISH))
    )

    assert result.status == SignalStatus.NO_SETUP
    assert result.score_class == ScoreClass.NO_TRADE
    assert result.no_trade_reasons == ["weekly_context_bearish"]
    assert "weekly_context_bearish" in result.risk_flags


def test_risk_reward_below_minimum_forces_no_setup() -> None:
    result = evaluate_trend_pullback_long(
        trend_payload(target_1_override=Decimal("110"), target_2_override=Decimal("112"))
    )

    assert result.risk_reward == Decimal("1.25")
    assert result.status == SignalStatus.NO_SETUP
    assert result.score_class == ScoreClass.NO_TRADE
    assert "risk_reward_below_minimum" in result.no_trade_reasons


def test_missing_stop_forces_no_setup() -> None:
    result = evaluate_trend_pullback_long(trend_payload(recent_swing_low=None))

    assert result.stop_loss is None
    assert result.status == SignalStatus.NO_SETUP
    assert result.score_class == ScoreClass.NO_TRADE
    assert "missing_stop_loss" in result.no_trade_reasons


def test_price_touch_only_does_not_arm_setup() -> None:
    result = evaluate_trend_pullback_long(
        trend_payload(price_touch_only=True, close_above_small_lower_high=True)
    )

    assert result.status == SignalStatus.WATCHLIST
    assert "price_touch_without_close_confirmation" in result.risk_flags
    assert any("price touch alone" in reason for reason in result.reasoning)


def test_reasoning_mentions_trend_pullback_trigger_risk_and_no_trade_checks() -> None:
    result = evaluate_trend_pullback_long(trend_payload())
    reasoning = " ".join(result.reasoning).lower()

    assert "trend check" in reasoning
    assert "pullback check" in reasoning
    assert "trigger check" in reasoning
    assert "risk/reward check" in reasoning
    assert result.risk_flags == []
    assert result.no_trade_reasons == []


def test_aggressive_volume_is_deterministic_risk_flag() -> None:
    daily = base_daily_context()
    high_volume_daily = IndicatorContext(
        close=daily.close,
        ema20=daily.ema20,
        ema50=daily.ema50,
        ema200=daily.ema200,
        rsi14=daily.rsi14,
        atr14=daily.atr14,
        relative_volume=Decimal("1.8"),
    )

    result = evaluate_trend_pullback_long(trend_payload(daily=high_volume_daily))

    assert "aggressive_pullback_volume" in result.risk_flags
    assert result.status in {SignalStatus.WATCHLIST, SignalStatus.ARMED}

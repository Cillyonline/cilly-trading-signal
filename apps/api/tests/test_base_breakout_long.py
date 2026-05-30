from decimal import Decimal

from app.models.enums import AssetClass, Bias, ScoreClass, SignalStatus, StrategyType
from app.strategies.base_breakout_long import (
    BaseBreakoutInput,
    evaluate_base_breakout_long,
)
from app.strategies.contracts import IndicatorContext, SignalEvaluationInput


def base_signal_input(weekly_bias: Bias = Bias.BULLISH) -> SignalEvaluationInput:
    return SignalEvaluationInput(
        symbol="MSFT",
        asset_class=AssetClass.STOCK,
        strategy_type=StrategyType.BASE_BREAKOUT_LONG,
        weekly_bias=weekly_bias,
        daily_bias=Bias.BULLISH,
    )


def base_daily_context() -> IndicatorContext:
    return IndicatorContext(
        close=Decimal("103"),
        ema20=Decimal("99"),
        ema50=Decimal("97"),
        ema200=Decimal("80"),
        atr14=Decimal("2"),
        relative_volume=Decimal("0.8"),
    )


def base_trigger_context() -> IndicatorContext:
    return IndicatorContext(close=Decimal("103"))


def breakout_payload(**overrides: object) -> BaseBreakoutInput:
    payload = {
        "signal_input": base_signal_input(),
        "daily": base_daily_context(),
        "trigger": base_trigger_context(),
        "previous_ema20": Decimal("98"),
        "previous_ema50": Decimal("96"),
        "base_high": Decimal("100"),
        "base_low": Decimal("94"),
        "base_days": 8,
        "close_above_base_high_4h": True,
        "close_above_base_high_daily": False,
        "wick_above_base_high_only": False,
    }
    payload.update(overrides)
    return BaseBreakoutInput(**payload)


def test_valid_base_breakout_long_produces_armed() -> None:
    result = evaluate_base_breakout_long(breakout_payload())

    assert result.strategy_type == StrategyType.BASE_BREAKOUT_LONG
    assert result.status == SignalStatus.ARMED
    assert result.score_class == ScoreClass.A_SETUP
    assert result.entry_low == Decimal("100")
    assert result.entry_high == Decimal("103")
    assert result.trigger_level == Decimal("100")
    assert result.stop_loss == Decimal("93.0")
    assert result.target_1 == Decimal("114.0")
    assert result.target_2 == Decimal("121.0")
    assert result.risk_reward == Decimal("2")
    assert result.invalidation_reason is not None
    assert result.no_trade_reasons == []


def test_base_forming_without_breakout_confirmation_produces_watchlist() -> None:
    result = evaluate_base_breakout_long(
        breakout_payload(close_above_base_high_4h=False, close_above_base_high_daily=False)
    )

    assert result.status == SignalStatus.WATCHLIST
    assert result.score_class in {ScoreClass.A_SETUP, ScoreClass.B_SETUP}
    assert "wait for close confirmation" in result.next_action


def test_wick_spike_without_close_confirmation_does_not_arm() -> None:
    result = evaluate_base_breakout_long(
        breakout_payload(wick_above_base_high_only=True, close_above_base_high_4h=True)
    )

    assert result.status == SignalStatus.WATCHLIST
    assert "wick_without_close_confirmation" in result.risk_flags
    assert any("wick/spike alone" in reason for reason in result.reasoning)


def test_risk_reward_below_minimum_forces_no_setup() -> None:
    result = evaluate_base_breakout_long(
        breakout_payload(target_1_override=Decimal("110"), target_2_override=Decimal("112"))
    )

    assert result.risk_reward == Decimal("1.428571428571428571428571429")
    assert result.status == SignalStatus.NO_SETUP
    assert result.score_class == ScoreClass.NO_TRADE
    assert "risk_reward_below_minimum" in result.no_trade_reasons


def test_bearish_weekly_context_forces_no_setup() -> None:
    result = evaluate_base_breakout_long(
        breakout_payload(signal_input=base_signal_input(weekly_bias=Bias.BEARISH))
    )

    assert result.status == SignalStatus.NO_SETUP
    assert result.score_class == ScoreClass.NO_TRADE
    assert result.no_trade_reasons == ["weekly_context_bearish"]


def test_invalid_stop_or_target_forces_no_setup() -> None:
    result = evaluate_base_breakout_long(breakout_payload(base_low=None))

    assert result.stop_loss is None
    assert result.target_1 is None
    assert result.status == SignalStatus.NO_SETUP
    assert result.score_class == ScoreClass.NO_TRADE
    assert "missing_stop_loss" in result.no_trade_reasons


def test_base_too_wide_is_deterministic_risk_flag() -> None:
    result = evaluate_base_breakout_long(breakout_payload(base_low=Decimal("80")))

    assert result.status == SignalStatus.NO_SETUP
    assert "base_range_too_wide" in result.risk_flags
    assert "base_too_wide" in result.no_trade_reasons
    assert any("base range is too wide" in reason.lower() for reason in result.reasoning)


def test_extended_breakout_forces_no_setup() -> None:
    daily = base_daily_context()
    extended_daily = IndicatorContext(
        close=Decimal("108.5"),
        ema20=daily.ema20,
        ema50=daily.ema50,
        ema200=daily.ema200,
        atr14=daily.atr14,
        relative_volume=daily.relative_volume,
    )

    result = evaluate_base_breakout_long(breakout_payload(daily=extended_daily))

    assert result.status == SignalStatus.NO_SETUP
    assert "breakout_extended_after_trigger" in result.risk_flags
    assert "breakout_too_extended" in result.no_trade_reasons


def test_unclear_base_high_forces_no_setup() -> None:
    result = evaluate_base_breakout_long(breakout_payload(base_high_is_clear=False))

    assert result.status == SignalStatus.NO_SETUP
    assert "base_high_not_clear" in result.risk_flags
    assert "base_high_not_clear" in result.no_trade_reasons


def test_major_resistance_nearby_is_risk_flagged() -> None:
    result = evaluate_base_breakout_long(
        breakout_payload(major_resistance_level=Decimal("102"))
    )

    assert "major_resistance_nearby" in result.risk_flags
    assert any("major resistance" in reason.lower() for reason in result.reasoning)


def test_reasoning_mentions_base_breakout_risk_and_no_trade_checks() -> None:
    result = evaluate_base_breakout_long(breakout_payload())
    reasoning = " ".join(result.reasoning).lower()

    assert "base quality check" in reasoning
    assert "breakout confirmation" in reasoning
    assert "risk/reward check" in reasoning
    assert result.risk_flags == []
    assert result.no_trade_reasons == []

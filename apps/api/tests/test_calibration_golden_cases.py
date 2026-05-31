from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal

import pytest

from app.models.enums import AssetClass, Bias, ScoreClass, SignalStatus, StrategyType
from app.services.analysis_quality import build_analysis_quality_report
from app.strategies.base_breakout_long import BaseBreakoutInput, evaluate_base_breakout_long
from app.strategies.contracts import IndicatorContext, SignalEvaluationInput, SignalEvaluationResult
from app.strategies.trend_pullback_long import TrendPullbackInput, evaluate_trend_pullback_long


@dataclass(frozen=True)
class GoldenCase:
    name: str
    evaluate: Callable[[], SignalEvaluationResult]
    expected_status: SignalStatus
    expected_score_class: ScoreClass
    expected_quality: dict[str, str]
    expected_risk_flags: set[str] = field(default_factory=set)
    expected_no_trade_reasons: set[str] = field(default_factory=set)


GOLDEN_CASES = [
    GoldenCase(
        name="trend_pullback_a_setup_armed",
        evaluate=lambda: evaluate_trend_pullback_long(trend_payload()),
        expected_status=SignalStatus.ARMED,
        expected_score_class=ScoreClass.A_SETUP,
        expected_quality={"trigger": "passed", "risk_plan": "passed"},
    ),
    GoldenCase(
        name="trend_pullback_watchlist_without_trigger",
        evaluate=lambda: evaluate_trend_pullback_long(
            trend_payload(close_above_small_lower_high=False, small_lower_high=Decimal("102"))
        ),
        expected_status=SignalStatus.WATCHLIST,
        expected_score_class=ScoreClass.A_SETUP,
        expected_quality={"trigger": "missing", "risk_plan": "passed"},
    ),
    GoldenCase(
        name="trend_pullback_no_trade_uncontrolled_pullback",
        evaluate=lambda: evaluate_trend_pullback_long(trend_payload(pullback_controlled=False)),
        expected_status=SignalStatus.NO_SETUP,
        expected_score_class=ScoreClass.NO_TRADE,
        expected_no_trade_reasons={"pullback_not_controlled"},
        expected_risk_flags={"uncontrolled_pullback"},
        expected_quality={"structure": "blocked"},
    ),
    GoldenCase(
        name="base_breakout_a_setup_armed",
        evaluate=lambda: evaluate_base_breakout_long(base_breakout_payload()),
        expected_status=SignalStatus.ARMED,
        expected_score_class=ScoreClass.A_SETUP,
        expected_quality={"trigger": "passed", "risk_plan": "passed"},
    ),
    GoldenCase(
        name="base_breakout_no_trade_wide_base",
        evaluate=lambda: evaluate_base_breakout_long(
            base_breakout_payload(base_low=Decimal("80"))
        ),
        expected_status=SignalStatus.NO_SETUP,
        expected_score_class=ScoreClass.NO_TRADE,
        expected_no_trade_reasons={"base_too_wide"},
        expected_risk_flags={"base_range_too_wide"},
        expected_quality={"structure": "blocked"},
    ),
    GoldenCase(
        name="stock_missing_benchmark_context_caps_to_b_setup",
        evaluate=lambda: evaluate_trend_pullback_long(
            trend_payload(
                signal_input=trend_signal_input(
                    context_risk_flags=["stock_benchmark_context_missing"],
                    score_cap=79,
                )
            )
        ),
        expected_status=SignalStatus.ARMED,
        expected_score_class=ScoreClass.B_SETUP,
        expected_risk_flags={"stock_benchmark_context_missing"},
        expected_quality={"market_regime": "warning", "data_quality": "warning"},
    ),
    GoldenCase(
        name="crypto_bearish_regime_blocks_long_review",
        evaluate=lambda: evaluate_trend_pullback_long(
            trend_payload(
                signal_input=trend_signal_input(
                    symbol="ETHUSDT",
                    asset_class=AssetClass.CRYPTO,
                    context_no_trade_reasons=["crypto_regime_bearish"],
                )
            )
        ),
        expected_status=SignalStatus.NO_SETUP,
        expected_score_class=ScoreClass.NO_TRADE,
        expected_no_trade_reasons={"crypto_regime_bearish"},
        expected_quality={"market_regime": "blocked"},
    ),
    GoldenCase(
        name="base_breakout_no_trade_missing_risk_plan",
        evaluate=lambda: evaluate_base_breakout_long(base_breakout_payload(base_low=None)),
        expected_status=SignalStatus.NO_SETUP,
        expected_score_class=ScoreClass.NO_TRADE,
        expected_no_trade_reasons={"missing_stop_loss", "missing_reward_target"},
        expected_quality={"risk_plan": "blocked", "data_quality": "blocked"},
    ),
    GoldenCase(
        name="review_finding_too_permissive_breakout_extended_blocks_chase",
        evaluate=lambda: evaluate_base_breakout_long(
            base_breakout_payload(
                base_high=Decimal("100"),
                base_low=Decimal("94"),
                daily=base_daily(close=Decimal("107")),
                trigger=IndicatorContext(close=Decimal("107")),
            )
        ),
        expected_status=SignalStatus.NO_SETUP,
        expected_score_class=ScoreClass.NO_TRADE,
        expected_no_trade_reasons={"breakout_too_extended"},
        expected_risk_flags={"breakout_extended_after_trigger"},
        expected_quality={"structure": "blocked", "trigger": "blocked"},
    ),
    GoldenCase(
        name="review_finding_too_strict_watchlist_missing_trigger_not_blocked",
        evaluate=lambda: evaluate_base_breakout_long(
            base_breakout_payload(close_above_base_high_4h=False, close_above_base_high_daily=False)
        ),
        expected_status=SignalStatus.WATCHLIST,
        expected_score_class=ScoreClass.A_SETUP,
        expected_quality={"trigger": "missing", "risk_plan": "passed"},
    ),
    GoldenCase(
        name="review_finding_unclear_risk_plan_missing_target_blocks",
        evaluate=lambda: evaluate_trend_pullback_long(
            trend_payload(target_1_override=None, target_2_override=None, recent_swing_low=None)
        ),
        expected_status=SignalStatus.NO_SETUP,
        expected_score_class=ScoreClass.NO_TRADE,
        expected_no_trade_reasons={"missing_stop_loss", "missing_reward_target"},
        expected_quality={"risk_plan": "blocked", "data_quality": "blocked"},
    ),
    GoldenCase(
        name="review_finding_too_permissive_trend_pullback_resistance_blocks",
        evaluate=lambda: evaluate_trend_pullback_long(
            trend_payload(strong_resistance_nearby=True)
        ),
        expected_status=SignalStatus.NO_SETUP,
        expected_score_class=ScoreClass.NO_TRADE,
        expected_no_trade_reasons={"strong_resistance_nearby"},
        expected_risk_flags={"strong_resistance_nearby"},
        expected_quality={"structure": "blocked"},
    ),
    GoldenCase(
        name="review_finding_too_permissive_trend_pullback_aggressive_volume_blocks",
        evaluate=lambda: evaluate_trend_pullback_long(
            trend_payload(
                daily=IndicatorContext(
                    close=Decimal("100"),
                    ema20=Decimal("98"),
                    ema50=Decimal("94"),
                    ema200=Decimal("80"),
                    rsi14=Decimal("52"),
                    atr14=Decimal("2"),
                    relative_volume=Decimal("1.8"),
                )
            )
        ),
        expected_status=SignalStatus.NO_SETUP,
        expected_score_class=ScoreClass.NO_TRADE,
        expected_no_trade_reasons={"pullback_volume_aggressive"},
        expected_risk_flags={"aggressive_pullback_volume"},
        expected_quality={"structure": "blocked", "volume": "warning"},
    ),
    GoldenCase(
        name="review_finding_too_permissive_base_breakout_resistance_blocks",
        evaluate=lambda: evaluate_base_breakout_long(
            base_breakout_payload(major_resistance_level=Decimal("102"))
        ),
        expected_status=SignalStatus.NO_SETUP,
        expected_score_class=ScoreClass.NO_TRADE,
        expected_no_trade_reasons={"strong_resistance_nearby"},
        expected_risk_flags={"major_resistance_nearby", "strong_resistance_nearby"},
        expected_quality={"structure": "blocked"},
    ),
]


@pytest.mark.parametrize("case", GOLDEN_CASES, ids=[case.name for case in GOLDEN_CASES])
def test_calibration_golden_case(case: GoldenCase) -> None:
    result = case.evaluate()
    quality_report = {
        check["key"]: check["status"] for check in build_analysis_quality_report(result)
    }

    assert result.status == case.expected_status
    assert result.score_class == case.expected_score_class
    assert case.expected_risk_flags.issubset(set(result.risk_flags))
    assert case.expected_no_trade_reasons.issubset(set(result.no_trade_reasons))
    for key, expected_status in case.expected_quality.items():
        assert quality_report[key] == expected_status


def trend_signal_input(
    symbol: str = "AAPL",
    asset_class: AssetClass = AssetClass.STOCK,
    weekly_bias: Bias = Bias.BULLISH,
    context_risk_flags: list[str] | None = None,
    context_no_trade_reasons: list[str] | None = None,
    score_cap: int | None = None,
) -> SignalEvaluationInput:
    return SignalEvaluationInput(
        symbol=symbol,
        asset_class=asset_class,
        strategy_type=StrategyType.TREND_PULLBACK_LONG,
        weekly_bias=weekly_bias,
        daily_bias=Bias.BULLISH,
        context_risk_flags=context_risk_flags or [],
        context_no_trade_reasons=context_no_trade_reasons or [],
        score_cap=score_cap,
    )


def breakout_signal_input(weekly_bias: Bias = Bias.BULLISH) -> SignalEvaluationInput:
    return SignalEvaluationInput(
        symbol="MSFT",
        asset_class=AssetClass.STOCK,
        strategy_type=StrategyType.BASE_BREAKOUT_LONG,
        weekly_bias=weekly_bias,
        daily_bias=Bias.BULLISH,
    )


def trend_payload(**overrides: object) -> TrendPullbackInput:
    payload = {
        "signal_input": trend_signal_input(),
        "daily": IndicatorContext(
            close=Decimal("100"),
            ema20=Decimal("98"),
            ema50=Decimal("94"),
            ema200=Decimal("80"),
            rsi14=Decimal("52"),
            atr14=Decimal("2"),
            relative_volume=Decimal("0.8"),
        ),
        "trigger": IndicatorContext(close=Decimal("101"), ema20=Decimal("100")),
        "previous_ema50": Decimal("93"),
        "recent_swing_low": Decimal("94"),
        "small_lower_high": Decimal("101"),
        "close_above_small_lower_high": True,
        "support_level": Decimal("96"),
    }
    payload.update(overrides)
    return TrendPullbackInput(**payload)


def base_breakout_payload(**overrides: object) -> BaseBreakoutInput:
    payload = {
        "signal_input": breakout_signal_input(),
        "daily": IndicatorContext(
            close=Decimal("103"),
            ema20=Decimal("99"),
            ema50=Decimal("97"),
            ema200=Decimal("80"),
            atr14=Decimal("2"),
            relative_volume=Decimal("0.8"),
        ),
        "trigger": IndicatorContext(close=Decimal("103")),
        "previous_ema20": Decimal("98"),
        "previous_ema50": Decimal("96"),
        "base_high": Decimal("100"),
        "base_low": Decimal("94"),
        "base_days": 8,
        "close_above_base_high_4h": True,
    }
    payload.update(overrides)
    return BaseBreakoutInput(**payload)


def base_daily(close: Decimal = Decimal("103")) -> IndicatorContext:
    return IndicatorContext(
        close=close,
        ema20=Decimal("99"),
        ema50=Decimal("97"),
        ema200=Decimal("80"),
        atr14=Decimal("2"),
        relative_volume=Decimal("0.8"),
    )

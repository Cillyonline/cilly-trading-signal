from decimal import Decimal

from app.models.enums import Bias, ScoreClass, SignalStatus, StrategyType, Timeframe
from app.services.analysis_quality import build_analysis_quality_report
from app.strategies.contracts import SignalEvaluationResult


def test_quality_report_marks_armed_setup_checks_passed() -> None:
    report = build_analysis_quality_report(
        signal_result(status=SignalStatus.ARMED, risk_reward=Decimal("2.4"))
    )

    assert status_for(report, "trigger") == "passed"
    assert status_for(report, "risk_plan") == "passed"
    assert status_for(report, "market_regime") == "passed"


def test_quality_report_marks_watchlist_trigger_missing() -> None:
    report = build_analysis_quality_report(
        signal_result(status=SignalStatus.WATCHLIST, risk_reward=Decimal("2.4"))
    )

    assert status_for(report, "trigger") == "missing"
    assert status_for(report, "risk_plan") == "passed"


def test_quality_report_marks_no_trade_blockers() -> None:
    report = build_analysis_quality_report(
        signal_result(
            status=SignalStatus.NO_SETUP,
            score_class=ScoreClass.NO_TRADE,
            risk_reward=None,
            no_trade_reasons=["poor_data_quality", "weekly_context_bearish"],
            risk_flags=["missing_1W_data", "poor_data_quality"],
        )
    )

    assert status_for(report, "market_regime") == "blocked"
    assert status_for(report, "data_quality") == "blocked"
    assert status_for(report, "risk_plan") == "blocked"


def test_quality_report_marks_context_warnings() -> None:
    report = build_analysis_quality_report(
        signal_result(
            risk_flags=["stock_benchmark_context_missing", "relative_strength_unavailable"],
        )
    )

    assert status_for(report, "market_regime") == "warning"
    assert status_for(report, "asset_overlay") == "warning"


def signal_result(
    status: SignalStatus = SignalStatus.ARMED,
    score_class: ScoreClass = ScoreClass.B_SETUP,
    risk_reward: Decimal | None = Decimal("2.1"),
    risk_flags: list[str] | None = None,
    no_trade_reasons: list[str] | None = None,
) -> SignalEvaluationResult:
    return SignalEvaluationResult(
        strategy_type=StrategyType.TREND_PULLBACK_LONG,
        status=status,
        bias=Bias.BULLISH,
        score=75,
        score_class=score_class,
        timeframe_context=Timeframe.ONE_WEEK,
        timeframe_setup=Timeframe.ONE_DAY,
        timeframe_trigger=Timeframe.FOUR_HOURS,
        entry_low=Decimal("100"),
        entry_high=Decimal("101"),
        trigger_level=Decimal("101"),
        stop_loss=Decimal("95"),
        target_1=Decimal("112"),
        target_2=Decimal("118"),
        risk_reward=risk_reward,
        invalidation_reason="Daily close below support invalidates the setup.",
        reasoning=["Test reasoning."],
        risk_flags=risk_flags or [],
        next_action="Review manually; no automatic trade is created.",
        no_trade_reasons=no_trade_reasons or [],
    )


def status_for(report: list[dict[str, str]], key: str) -> str:
    return next(item["status"] for item in report if item["key"] == key)

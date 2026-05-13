from decimal import Decimal

import pytest

from app.models.enums import AssetClass, Bias, ScoreClass, SignalStatus, StrategyType
from app.strategies.contracts import (
    ScoreBreakdown,
    SignalEvaluationInput,
    SignalEvaluationResult,
    build_signal_result,
    calculate_risk_reward,
    classify_score,
    collect_common_no_trade_reasons,
    map_status,
)


def signal_input(
    weekly_bias: Bias = Bias.BULLISH,
    daily_bias: Bias = Bias.BULLISH,
    data_quality_flags: list[str] | None = None,
    setup_invalidated: bool = False,
) -> SignalEvaluationInput:
    return SignalEvaluationInput(
        symbol="AAPL",
        asset_class=AssetClass.STOCK,
        strategy_type=StrategyType.TREND_PULLBACK_LONG,
        weekly_bias=weekly_bias,
        daily_bias=daily_bias,
        data_quality_flags=data_quality_flags or [],
        setup_invalidated=setup_invalidated,
    )


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (49, ScoreClass.NO_TRADE),
        (50, ScoreClass.WATCHLIST),
        (64, ScoreClass.WATCHLIST),
        (65, ScoreClass.B_SETUP),
        (79, ScoreClass.B_SETUP),
        (80, ScoreClass.A_SETUP),
        (100, ScoreClass.A_SETUP),
    ],
)
def test_score_class_boundaries(score: int, expected: ScoreClass) -> None:
    assert classify_score(score) == expected


def test_score_breakdown_total_is_bounded() -> None:
    score = ScoreBreakdown(
        trend=25,
        structure=25,
        momentum=15,
        volume=15,
        risk_reward=15,
        risk_filters=0,
    )

    assert score.total == 95


def test_score_breakdown_rejects_out_of_range_category() -> None:
    with pytest.raises(ValueError, match="trend score"):
        ScoreBreakdown(trend=26)


def test_status_mapping_never_emits_triggered() -> None:
    statuses = {
        map_status(ScoreClass.NO_TRADE, has_valid_trigger_plan=True),
        map_status(ScoreClass.WATCHLIST, has_valid_trigger_plan=True),
        map_status(ScoreClass.B_SETUP, has_valid_trigger_plan=False),
        map_status(ScoreClass.B_SETUP, has_valid_trigger_plan=True),
        map_status(ScoreClass.A_SETUP, has_valid_trigger_plan=True),
    }

    assert SignalStatus.TRIGGERED not in statuses


def test_calculate_risk_reward_requires_valid_entry_stop_target() -> None:
    assert calculate_risk_reward(
        entry=Decimal("100"), stop=Decimal("90"), target=Decimal("125")
    ) == Decimal("2.5")
    assert calculate_risk_reward(
        entry=Decimal("100"), stop=Decimal("100"), target=Decimal("125")
    ) is None
    assert calculate_risk_reward(
        entry=Decimal("100"), stop=Decimal("90"), target=Decimal("99")
    ) is None


@pytest.mark.parametrize(
    ("input_payload", "entry", "stop", "risk_reward", "expected_reason"),
    [
        (
            signal_input(),
            Decimal("100"),
            Decimal("90"),
            Decimal("1.9"),
            "risk_reward_below_minimum",
        ),
        (
            signal_input(weekly_bias=Bias.BEARISH),
            Decimal("100"),
            Decimal("90"),
            Decimal("2.0"),
            "weekly_context_bearish",
        ),
        (signal_input(), Decimal("100"), None, Decimal("2.0"), "missing_stop_loss"),
        (signal_input(), Decimal("90"), Decimal("90"), Decimal("2.0"), "entry_not_above_stop"),
        (
            signal_input(data_quality_flags=["missing_ema200"]),
            Decimal("100"),
            Decimal("90"),
            Decimal("2.0"),
            "poor_data_quality",
        ),
        (
            signal_input(setup_invalidated=True),
            Decimal("100"),
            Decimal("90"),
            Decimal("2.0"),
            "setup_already_invalidated",
        ),
    ],
)
def test_common_no_trade_reasons(
    input_payload: SignalEvaluationInput,
    entry: Decimal | None,
    stop: Decimal | None,
    risk_reward: Decimal | None,
    expected_reason: str,
) -> None:
    reasons = collect_common_no_trade_reasons(
        input_payload,
        entry=entry,
        stop=stop,
        risk_reward=risk_reward,
    )

    assert expected_reason in reasons


def test_build_signal_result_maps_watchlist_and_explainability_fields() -> None:
    result = build_signal_result(
        signal_input(),
        ScoreBreakdown(trend=15, structure=15, momentum=10, volume=5, risk_reward=10),
        bias=Bias.BULLISH,
        reasoning=["Trend is constructive but setup is not ready."],
        risk_flags=[],
        next_action="Keep on watchlist; wait for confirmation.",
        entry_low=Decimal("100"),
        stop_loss=Decimal("90"),
        risk_reward=Decimal("2.5"),
        has_valid_trigger_plan=False,
    )

    assert result.status == SignalStatus.WATCHLIST
    assert result.score_class == ScoreClass.WATCHLIST
    assert result.reasoning
    assert result.risk_flags == []
    assert result.next_action
    assert result.no_trade_reasons == []


def test_hard_no_trade_overrides_high_score() -> None:
    result = build_signal_result(
        signal_input(weekly_bias=Bias.BEARISH),
        ScoreBreakdown(
            trend=25,
            structure=25,
            momentum=15,
            volume=15,
            risk_reward=15,
        ),
        bias=Bias.BULLISH,
        reasoning=["Setup has technical strength."],
        risk_flags=[],
        next_action="No setup; wait for context to improve.",
        entry_low=Decimal("100"),
        stop_loss=Decimal("90"),
        risk_reward=Decimal("3.0"),
        has_valid_trigger_plan=True,
    )

    assert result.score == 95
    assert result.status == SignalStatus.NO_SETUP
    assert result.score_class == ScoreClass.NO_TRADE
    assert result.no_trade_reasons == ["weekly_context_bearish"]
    assert "weekly_context_bearish" in result.risk_flags
    assert "Hard No-Trade rule applied" in result.reasoning[-1]


def test_build_signal_result_can_emit_armed_but_not_triggered() -> None:
    result = build_signal_result(
        signal_input(),
        ScoreBreakdown(trend=25, structure=25, momentum=15, volume=5, risk_reward=10),
        bias=Bias.BULLISH,
        reasoning=["Context, setup, trigger plan, and risk are aligned."],
        risk_flags=[],
        next_action="Review the prepared setup manually; no automatic trade is created.",
        entry_low=Decimal("100"),
        entry_high=Decimal("101"),
        trigger_level=Decimal("101"),
        stop_loss=Decimal("95"),
        target_1=Decimal("112"),
        target_2=Decimal("118"),
        risk_reward=Decimal("2.2"),
        invalidation_reason="Daily close below setup support invalidates the setup.",
        has_valid_trigger_plan=True,
    )

    assert result.status == SignalStatus.ARMED
    assert result.status != SignalStatus.TRIGGERED
    assert result.to_signal_kwargs()["status"] == SignalStatus.ARMED


def test_signal_result_rejects_triggered_status() -> None:
    with pytest.raises(ValueError, match="must not emit triggered"):
        SignalEvaluationResult(
            strategy_type=StrategyType.TREND_PULLBACK_LONG,
            status=SignalStatus.TRIGGERED,
            bias=Bias.BULLISH,
            score=80,
            score_class=ScoreClass.A_SETUP,
            timeframe_context=signal_input().context_timeframe,
            timeframe_setup=signal_input().setup_timeframe,
            timeframe_trigger=signal_input().trigger_timeframe,
            entry_low=None,
            entry_high=None,
            trigger_level=None,
            stop_loss=None,
            target_1=None,
            target_2=None,
            risk_reward=None,
            invalidation_reason=None,
            reasoning=["Invalid test result."],
            risk_flags=[],
            next_action="Do not emit triggered.",
            no_trade_reasons=[],
        )

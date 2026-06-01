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
    data_quality_no_trade_reasons,
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


@pytest.mark.parametrize(
    ("flags", "expected_reasons"),
    [
        (["missing_1W_data"], ["required_timeframe_data_missing"]),
        (["market_data_stale_1D"], ["required_market_data_not_fresh"]),
        (["1D_insufficient_candle_history"], ["insufficient_candle_history"]),
        (["4H_ema200_missing"], ["required_indicator_missing"]),
        (["provider_payload_invalid"], ["poor_data_quality"]),
        (["missing_1D_data", "missing_4H_data"], ["required_timeframe_data_missing"]),
    ],
)
def test_data_quality_no_trade_reasons_are_specific(
    flags: list[str], expected_reasons: list[str]
) -> None:
    assert data_quality_no_trade_reasons(flags) == expected_reasons


def test_specific_data_quality_reasons_override_high_score() -> None:
    result = build_signal_result(
        signal_input(data_quality_flags=["market_data_stale_1D", "1D_ema200_missing"]),
        ScoreBreakdown(trend=25, structure=25, momentum=15, volume=15, risk_reward=15),
        bias=Bias.BULLISH,
        reasoning=["Setup has technical strength."],
        risk_flags=[],
        next_action="Generic placeholder should be replaced.",
        entry_low=Decimal("100"),
        stop_loss=Decimal("95"),
        target_1=Decimal("112"),
        risk_reward=Decimal("2.4"),
        has_valid_trigger_plan=True,
    )

    assert result.status == SignalStatus.NO_SETUP
    assert result.score_class == ScoreClass.NO_TRADE
    assert result.no_trade_reasons == [
        "required_market_data_not_fresh",
        "required_indicator_missing",
    ]
    assert "required_market_data_not_fresh" in result.risk_flags
    assert "Keep No Trade" in result.next_action
    assert "refresh stale, partial, failed, missing, or unknown market data" in result.next_action


@pytest.mark.parametrize(
    ("flags", "expected_reasons"),
    [
        (
            ["market_data_partial_1D", "provider_sync_failed_4H"],
            ["required_market_data_not_fresh"],
        ),
        (
            ["market_data_unknown_1W", "missing_4H_data"],
            ["required_market_data_not_fresh", "required_timeframe_data_missing"],
        ),
    ],
)
def test_paper_batch_missing_context_variants_stay_no_trade(
    flags: list[str], expected_reasons: list[str]
) -> None:
    result = build_signal_result(
        signal_input(data_quality_flags=flags),
        ScoreBreakdown(trend=25, structure=25, momentum=15, volume=15, risk_reward=15),
        bias=Bias.BULLISH,
        reasoning=["Setup has technical strength."],
        risk_flags=[],
        next_action="Generic placeholder should be replaced.",
        entry_low=Decimal("100"),
        stop_loss=Decimal("95"),
        target_1=Decimal("112"),
        risk_reward=Decimal("2.4"),
        has_valid_trigger_plan=True,
    )

    assert result.status == SignalStatus.NO_SETUP
    assert result.score_class == ScoreClass.NO_TRADE
    assert result.no_trade_reasons == expected_reasons
    assert set(expected_reasons).issubset(result.risk_flags)
    assert "Keep No Trade" in result.next_action
    assert "refresh stale, partial, failed, missing, or unknown market data" in result.next_action


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
    assert "weekly context is bearish" in result.reasoning[-1]
    assert result.next_action == (
        "Wait for weekly context to turn neutral or bullish before manual long review."
    )


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


def test_context_risk_flags_cap_a_setup_confidence() -> None:
    result = build_signal_result(
        SignalEvaluationInput(
            symbol="AAPL",
            asset_class=AssetClass.STOCK,
            strategy_type=StrategyType.TREND_PULLBACK_LONG,
            weekly_bias=Bias.BULLISH,
            daily_bias=Bias.BULLISH,
            context_risk_flags=["stock_benchmark_context_missing"],
            score_cap=79,
        ),
        ScoreBreakdown(trend=25, structure=25, momentum=15, volume=15, risk_reward=15),
        bias=Bias.BULLISH,
        reasoning=["Context, setup, trigger plan, and risk are aligned."],
        risk_flags=[],
        next_action="Review manually; no automatic trade is created.",
        entry_low=Decimal("100"),
        entry_high=Decimal("101"),
        trigger_level=Decimal("101"),
        stop_loss=Decimal("95"),
        target_1=Decimal("112"),
        risk_reward=Decimal("2.2"),
        has_valid_trigger_plan=True,
    )

    assert result.score == 79
    assert result.score_class == ScoreClass.B_SETUP
    assert result.status == SignalStatus.ARMED
    assert "stock_benchmark_context_missing" in result.risk_flags
    assert "Market context cap applied" in result.reasoning[-1]


def test_context_no_trade_reasons_override_score() -> None:
    result = build_signal_result(
        SignalEvaluationInput(
            symbol="AAPL",
            asset_class=AssetClass.STOCK,
            strategy_type=StrategyType.TREND_PULLBACK_LONG,
            weekly_bias=Bias.BULLISH,
            daily_bias=Bias.BULLISH,
            context_no_trade_reasons=["stock_market_regime_bearish"],
        ),
        ScoreBreakdown(trend=25, structure=25, momentum=15, volume=15, risk_reward=15),
        bias=Bias.BULLISH,
        reasoning=["Setup has technical strength."],
        risk_flags=[],
        next_action="No setup; wait for context to improve.",
        entry_low=Decimal("100"),
        stop_loss=Decimal("95"),
        target_1=Decimal("112"),
        risk_reward=Decimal("2.4"),
        has_valid_trigger_plan=True,
    )

    assert result.status == SignalStatus.NO_SETUP
    assert result.score_class == ScoreClass.NO_TRADE
    assert "stock_market_regime_bearish" in result.no_trade_reasons
    assert result.next_action == (
        "Wait for stored SPY/QQQ context to recover before reviewing new stock long setups."
    )


@pytest.mark.parametrize(
    ("reason", "expected_action_fragment"),
    [
        ("poor_data_quality", "Refresh or provide the missing/stale timeframe"),
        ("missing_stop_loss", "Define a technical stop below structure"),
        ("risk_reward_below_minimum", "supports at least 2R"),
        ("base_too_wide", "Wait for a tighter base"),
        ("pullback_not_controlled", "Wait for price to stabilize"),
        ("required_timeframe_data_missing", "Keep No Trade and import all required timeframes"),
        ("required_market_data_not_fresh", "Keep No Trade and refresh stale"),
        ("insufficient_candle_history", "Keep No Trade until enough candle history"),
        ("required_indicator_missing", "Keep No Trade and re-run analysis"),
    ],
)
def test_no_trade_next_action_is_specific(reason: str, expected_action_fragment: str) -> None:
    result = build_signal_result(
        SignalEvaluationInput(
            symbol="AAPL",
            asset_class=AssetClass.STOCK,
            strategy_type=StrategyType.TREND_PULLBACK_LONG,
            weekly_bias=Bias.BULLISH,
            daily_bias=Bias.BULLISH,
            context_no_trade_reasons=[reason],
        ),
        ScoreBreakdown(trend=25, structure=25, momentum=15, volume=15, risk_reward=15),
        bias=Bias.BULLISH,
        reasoning=["Setup has technical strength."],
        risk_flags=[],
        next_action="Generic placeholder should be replaced.",
        entry_low=Decimal("100"),
        stop_loss=Decimal("95"),
        target_1=Decimal("112"),
        risk_reward=Decimal("2.4"),
        has_valid_trigger_plan=True,
    )

    assert result.status == SignalStatus.NO_SETUP
    assert expected_action_fragment in result.next_action
    assert result.next_action != "Generic placeholder should be replaced."
    assert any(reasoning.startswith("No Trade:") for reasoning in result.reasoning)


@pytest.mark.parametrize(
    ("reason", "expected_reasoning_fragment"),
    [
        ("required_timeframe_data_missing", "full timeframe set is available"),
        ("required_market_data_not_fresh", "current setup quality cannot be trusted"),
        ("insufficient_candle_history", "keep this as missing context"),
        ("required_indicator_missing", "cannot be reviewed safely"),
    ],
)
def test_missing_context_no_trade_reasoning_is_actionable(
    reason: str, expected_reasoning_fragment: str
) -> None:
    result = build_signal_result(
        SignalEvaluationInput(
            symbol="AAPL",
            asset_class=AssetClass.STOCK,
            strategy_type=StrategyType.TREND_PULLBACK_LONG,
            weekly_bias=Bias.BULLISH,
            daily_bias=Bias.BULLISH,
            context_no_trade_reasons=[reason],
        ),
        ScoreBreakdown(trend=25, structure=25, momentum=15, volume=15, risk_reward=15),
        bias=Bias.BULLISH,
        reasoning=["Setup has technical strength."],
        risk_flags=[],
        next_action="Generic placeholder should be replaced.",
        entry_low=Decimal("100"),
        stop_loss=Decimal("95"),
        target_1=Decimal("112"),
        risk_reward=Decimal("2.4"),
        has_valid_trigger_plan=True,
    )

    assert result.status == SignalStatus.NO_SETUP
    assert result.score_class == ScoreClass.NO_TRADE
    assert any(expected_reasoning_fragment in item for item in result.reasoning)
    assert "Keep No Trade" in result.next_action


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

from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.enums import Bias, MarketDataStatus, StrategyType
from app.models.market_data import IndicatorSnapshot, MarketDataCandle, MarketDataSeries
from app.schemas.analysis import MarketDataAnalysisResult, SignalAnalysisResult
from app.services.indicators import (
    calculate_indicator_snapshots,
    indicator_input_from_model,
)
from app.services.signals import upsert_signal_from_analysis
from app.strategies.contracts import IndicatorContext, SignalEvaluationInput
from app.strategies.orchestrator import SignalEngineInput, evaluate_mvp_signal_engine
from app.strategies.trend_pullback_long import TrendPullbackInput

MIN_ANALYSIS_CANDLES = 200


def analyze_market_data_series(db: Session, series: MarketDataSeries) -> MarketDataAnalysisResult:
    candles = list(
        db.scalars(
            select(MarketDataCandle)
            .where(MarketDataCandle.series_id == series.id)
            .order_by(MarketDataCandle.timestamp)
        )
    )
    snapshots = calculate_indicator_snapshots(
        [indicator_input_from_model(candle) for candle in candles]
    )

    db.execute(delete(IndicatorSnapshot).where(IndicatorSnapshot.series_id == series.id))
    db.flush()
    db.add_all(
        IndicatorSnapshot(series_id=series.id, **snapshot.to_indicator_snapshot_kwargs())
        for snapshot in snapshots
    )

    latest_snapshot = snapshots[-1] if snapshots else None
    signal_result = evaluate_mvp_signal_engine(
        build_signal_engine_input(series, candles, latest_snapshot)
    )

    series.status = (
        MarketDataStatus.ANALYZED
        if len(candles) >= MIN_ANALYSIS_CANDLES
        else MarketDataStatus.FAILED
    )
    if len(candles) < MIN_ANALYSIS_CANDLES:
        series.validation_errors = [
            {
                "message": (
                    f"At least {MIN_ANALYSIS_CANDLES} candles are required for signal analysis."
                )
            }
        ]
    else:
        series.validation_errors = None

    signal = upsert_signal_from_analysis(
        db,
        user_id=series.watchlist_item.user_id,
        watchlist_item_id=series.watchlist_item_id,
        result=signal_result,
    )

    db.commit()
    db.refresh(signal)

    return MarketDataAnalysisResult(
        series_id=series.id,
        status=series.status,
        candle_count=len(candles),
        indicator_snapshot_count=len(snapshots),
        signal=SignalAnalysisResult(**signal_result.__dict__),
    )


def build_signal_engine_input(
    series: MarketDataSeries,
    candles: list[MarketDataCandle],
    latest_snapshot: object,
) -> SignalEngineInput:
    fallback_input = SignalEvaluationInput(
        symbol=series.watchlist_item.symbol,
        asset_class=series.watchlist_item.asset_class,
        strategy_type=StrategyType.TREND_PULLBACK_LONG,
        weekly_bias=Bias.NEUTRAL,
        daily_bias=Bias.NEUTRAL,
        data_quality_flags=data_quality_flags(candles, latest_snapshot),
    )

    if len(candles) < MIN_ANALYSIS_CANDLES or latest_snapshot is None:
        return SignalEngineInput(fallback_input=fallback_input)

    latest_candle = candles[-1]
    recent_lows = [candle.low for candle in candles[-20:]]
    recent_highs = [candle.high for candle in candles[-20:]]
    daily_context = IndicatorContext(
        close=latest_candle.close,
        ema20=latest_snapshot.ema20,
        ema50=latest_snapshot.ema50,
        ema200=latest_snapshot.ema200,
        rsi14=latest_snapshot.rsi14,
        atr14=latest_snapshot.atr14,
        volume_avg20=latest_snapshot.volume_avg20,
        relative_volume=latest_snapshot.relative_volume,
    )
    trend_input = TrendPullbackInput(
        signal_input=fallback_input,
        daily=daily_context,
        trigger=IndicatorContext(
            close=latest_candle.close,
            ema20=latest_snapshot.ema20,
            ema50=latest_snapshot.ema50,
        ),
        previous_ema50=previous_ema50_from_snapshots(candles, latest_snapshot),
        recent_swing_low=min(recent_lows) if recent_lows else None,
        small_lower_high=max(recent_highs) if recent_highs else None,
        close_above_small_lower_high=False,
        close_back_above_ema20=False,
        close_back_above_ema50=False,
        support_level=min(recent_lows) if recent_lows else None,
        previous_trend_clear=True,
        pullback_controlled=True,
    )
    return SignalEngineInput(fallback_input=fallback_input, trend_pullback=trend_input)


def previous_ema50_from_snapshots(
    candles: list[MarketDataCandle], latest_snapshot: object
) -> Decimal | None:
    if len(candles) < 2 or latest_snapshot.ema50 is None:
        return None
    return latest_snapshot.ema50 - Decimal("0.00000001")


def data_quality_flags(candles: list[MarketDataCandle], latest_snapshot: object) -> list[str]:
    flags: list[str] = []
    if len(candles) < MIN_ANALYSIS_CANDLES:
        flags.append("insufficient_candle_history")
    if latest_snapshot is None or latest_snapshot.ema200 is None:
        flags.append("ema200_missing")
    return flags

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.enums import Bias, MarketDataStatus, StrategyType, Timeframe
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
REQUIRED_TIMEFRAMES = (Timeframe.ONE_WEEK, Timeframe.ONE_DAY, Timeframe.FOUR_HOURS)


class TimeframeAnalysisData:
    def __init__(
        self,
        series: MarketDataSeries,
        candles: list[MarketDataCandle],
        snapshots: list[object],
    ) -> None:
        self.series = series
        self.candles = candles
        self.snapshots = snapshots

    @property
    def latest_candle(self) -> MarketDataCandle | None:
        return self.candles[-1] if self.candles else None

    @property
    def latest_snapshot(self) -> object | None:
        return self.snapshots[-1] if self.snapshots else None


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

    signal_result = evaluate_mvp_signal_engine(
        build_signal_engine_input(db, series, candles, snapshots)
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
    db: Session,
    series: MarketDataSeries,
    candles: list[MarketDataCandle],
    snapshots: list[object],
) -> SignalEngineInput:
    timeframe_data = load_timeframe_analysis_data(db, series, candles, snapshots)
    missing_timeframes = [
        timeframe.value for timeframe in REQUIRED_TIMEFRAMES if timeframe not in timeframe_data
    ]
    data_quality: list[str] = []
    data_quality.extend(f"missing_{timeframe}_data" for timeframe in missing_timeframes)
    data_quality.extend(timeframe_quality_flags(timeframe_data))

    fallback_input = SignalEvaluationInput(
        symbol=series.watchlist_item.symbol,
        asset_class=series.watchlist_item.asset_class,
        strategy_type=StrategyType.TREND_PULLBACK_LONG,
        weekly_bias=weekly_bias_from_data(timeframe_data.get(Timeframe.ONE_WEEK)),
        daily_bias=Bias.NEUTRAL,
        weekly_indicators=context_from_timeframe(timeframe_data.get(Timeframe.ONE_WEEK)),
        daily_indicators=context_from_timeframe(timeframe_data.get(Timeframe.ONE_DAY)),
        trigger_indicators=context_from_timeframe(timeframe_data.get(Timeframe.FOUR_HOURS)),
        data_quality_flags=data_quality,
    )

    if missing_timeframes or data_quality:
        return SignalEngineInput(fallback_input=fallback_input)

    daily_data = timeframe_data[Timeframe.ONE_DAY]
    trigger_data = timeframe_data[Timeframe.FOUR_HOURS]
    daily_context = context_from_timeframe(daily_data)
    trigger_context = context_from_timeframe(trigger_data)
    recent_daily_lows = [candle.low for candle in daily_data.candles[-20:]]
    recent_trigger_highs = [candle.high for candle in trigger_data.candles[-20:]]
    previous_daily_snapshot = previous_snapshot(daily_data.snapshots)
    trend_input = TrendPullbackInput(
        signal_input=fallback_input,
        daily=daily_context,
        trigger=trigger_context,
        previous_ema50=getattr(previous_daily_snapshot, "ema50", None),
        recent_swing_low=min(recent_daily_lows) if recent_daily_lows else None,
        small_lower_high=max(recent_trigger_highs) if recent_trigger_highs else None,
        close_above_small_lower_high=close_above_level(
            trigger_context.close,
            max(recent_trigger_highs[:-1]) if len(recent_trigger_highs) > 1 else None,
        ),
        close_back_above_ema20=close_above_level(trigger_context.close, trigger_context.ema20),
        close_back_above_ema50=close_above_level(trigger_context.close, trigger_context.ema50),
        support_level=min(recent_daily_lows) if recent_daily_lows else None,
        previous_trend_clear=True,
        pullback_controlled=True,
    )
    return SignalEngineInput(fallback_input=fallback_input, trend_pullback=trend_input)


def load_timeframe_analysis_data(
    db: Session,
    source_series: MarketDataSeries,
    source_candles: list[MarketDataCandle],
    source_snapshots: list[object],
) -> dict[Timeframe, TimeframeAnalysisData]:
    latest_series = {
        source_series.timeframe: TimeframeAnalysisData(
            source_series,
            source_candles,
            source_snapshots,
        )
    }
    candidates = list(
        db.scalars(
            select(MarketDataSeries)
            .where(MarketDataSeries.watchlist_item_id == source_series.watchlist_item_id)
            .where(
                MarketDataSeries.status.in_(
                    (MarketDataStatus.ANALYZED, MarketDataStatus.VALIDATED)
                )
            )
            .where(MarketDataSeries.timeframe.in_(REQUIRED_TIMEFRAMES))
            .order_by(MarketDataSeries.imported_at.desc(), MarketDataSeries.id.desc())
        )
    )
    for candidate in candidates:
        if candidate.timeframe in latest_series:
            continue
        candidate_candles = load_candles(db, candidate)
        candidate_snapshots = load_snapshots(db, candidate)
        if not candidate_snapshots:
            candidate_snapshots = calculate_indicator_snapshots(
                [indicator_input_from_model(candle) for candle in candidate_candles]
            )
        latest_series[candidate.timeframe] = TimeframeAnalysisData(
            candidate,
            candidate_candles,
            candidate_snapshots,
        )
    return latest_series


def load_candles(db: Session, series: MarketDataSeries) -> list[MarketDataCandle]:
    return list(
        db.scalars(
            select(MarketDataCandle)
            .where(MarketDataCandle.series_id == series.id)
            .order_by(MarketDataCandle.timestamp)
        )
    )


def load_snapshots(db: Session, series: MarketDataSeries) -> list[IndicatorSnapshot]:
    return list(
        db.scalars(
            select(IndicatorSnapshot)
            .where(IndicatorSnapshot.series_id == series.id)
            .order_by(IndicatorSnapshot.timestamp)
        )
    )


def context_from_timeframe(data: TimeframeAnalysisData | None) -> IndicatorContext:
    if data is None or data.latest_candle is None or data.latest_snapshot is None:
        return IndicatorContext()
    snapshot = data.latest_snapshot
    return IndicatorContext(
        close=data.latest_candle.close,
        ema20=getattr(snapshot, "ema20", None),
        ema50=getattr(snapshot, "ema50", None),
        ema200=getattr(snapshot, "ema200", None),
        rsi14=getattr(snapshot, "rsi14", None),
        atr14=getattr(snapshot, "atr14", None),
        volume_avg20=getattr(snapshot, "volume_avg20", None),
        relative_volume=getattr(snapshot, "relative_volume", None),
    )


def weekly_bias_from_data(data: TimeframeAnalysisData | None) -> Bias:
    context = context_from_timeframe(data)
    if context.close is None or context.ema20 is None or context.ema50 is None:
        return Bias.NEUTRAL
    if context.close > context.ema20 and context.ema20 >= context.ema50:
        return Bias.BULLISH
    if context.close < context.ema50:
        return Bias.BEARISH
    return Bias.NEUTRAL


def previous_snapshot(snapshots: list[object]) -> object | None:
    if len(snapshots) < 2:
        return None
    return snapshots[-2]


def close_above_level(close: object, level: object) -> bool:
    return close is not None and level is not None and close > level


def timeframe_quality_flags(timeframe_data: dict[Timeframe, TimeframeAnalysisData]) -> list[str]:
    flags: list[str] = []
    for timeframe, data in timeframe_data.items():
        latest_snapshot = data.latest_snapshot
        if len(data.candles) < MIN_ANALYSIS_CANDLES:
            flags.append(f"{timeframe.value}_insufficient_candle_history")
        if latest_snapshot is None or getattr(latest_snapshot, "ema200", None) is None:
            flags.append(f"{timeframe.value}_ema200_missing")
    return flags

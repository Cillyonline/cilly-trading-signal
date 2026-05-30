from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.enums import (
    AssetClass,
    MarketDataSource,
    MarketDataFreshnessStatus,
    MarketDataStatus,
    SignalStatus,
    StrategyType,
    Timeframe,
    UserRole,
)
from app.models.market_data import IndicatorSnapshot, MarketDataCandle, MarketDataSeries
from app.models.user import User
from app.models.watchlist import WatchlistItem
from app.services.analysis import analyze_market_data_series, build_signal_engine_input
from app.strategies.orchestrator import evaluate_mvp_signal_engine


def test_build_signal_input_uses_distinct_weekly_daily_and_4h_data() -> None:
    with make_session() as db:
        watchlist_item = create_watchlist_item(db)
        weekly = create_series_with_data(db, watchlist_item, Timeframe.ONE_WEEK, Decimal("120"))
        daily = create_series_with_data(db, watchlist_item, Timeframe.ONE_DAY, Decimal("100"))
        trigger = create_series_with_data(db, watchlist_item, Timeframe.FOUR_HOURS, Decimal("103"))

        payload = build_signal_engine_input(
            db,
            daily,
            load_series_candles(db, daily),
            load_series_snapshots(db, daily),
        )

        assert payload.trend_pullback is not None
        assert payload.fallback_input.weekly_indicators.close == Decimal("120.00000000")
        assert payload.trend_pullback.daily.close == Decimal("100.00000000")
        assert payload.trend_pullback.trigger.close == Decimal("103.00000000")
        assert payload.trend_pullback.previous_ema50 == Decimal("94.00000000")
        assert weekly.id != daily.id != trigger.id


def test_build_signal_input_creates_base_breakout_candidate() -> None:
    with make_session() as db:
        watchlist_item = create_watchlist_item(db)
        create_series_with_data(db, watchlist_item, Timeframe.ONE_WEEK, Decimal("120"))
        daily = create_series_with_base_breakout(
            db,
            watchlist_item,
            Timeframe.ONE_DAY,
            breakout_close=Decimal("111"),
        )
        trigger = create_series_with_base_breakout(
            db,
            watchlist_item,
            Timeframe.FOUR_HOURS,
            breakout_close=Decimal("111"),
        )

        payload = build_signal_engine_input(
            db,
            daily,
            load_series_candles(db, daily),
            load_series_snapshots(db, daily),
        )

        assert payload.base_breakout is not None
        assert payload.base_breakout.base_high == Decimal("110.00000000")
        assert payload.base_breakout.base_low == Decimal("100.00000000")
        assert payload.base_breakout.close_above_base_high_4h is True
        assert trigger.id != daily.id


def test_base_breakout_can_be_selected_by_orchestrator() -> None:
    with make_session() as db:
        watchlist_item = create_watchlist_item(db)
        create_series_with_data(db, watchlist_item, Timeframe.ONE_WEEK, Decimal("120"))
        daily = create_series_with_base_breakout(
            db,
            watchlist_item,
            Timeframe.ONE_DAY,
            breakout_close=Decimal("111"),
        )
        create_series_with_base_breakout(
            db,
            watchlist_item,
            Timeframe.FOUR_HOURS,
            breakout_close=Decimal("111"),
        )

        result = evaluate_mvp_signal_engine(
            build_signal_engine_input(
                db,
                daily,
                load_series_candles(db, daily),
                load_series_snapshots(db, daily),
            )
        )

        assert result.strategy_type == StrategyType.BASE_BREAKOUT_LONG
        assert result.status == SignalStatus.ARMED


def test_missing_stock_benchmark_context_caps_confidence() -> None:
    with make_session() as db:
        watchlist_item = create_watchlist_item(db)
        create_series_with_data(db, watchlist_item, Timeframe.ONE_WEEK, Decimal("120"))
        daily = create_series_with_base_breakout(
            db,
            watchlist_item,
            Timeframe.ONE_DAY,
            breakout_close=Decimal("111"),
        )
        create_series_with_base_breakout(
            db,
            watchlist_item,
            Timeframe.FOUR_HOURS,
            breakout_close=Decimal("111"),
        )

        result = evaluate_mvp_signal_engine(
            build_signal_engine_input(
                db,
                daily,
                load_series_candles(db, daily),
                load_series_snapshots(db, daily),
            )
        )

        assert result.status == SignalStatus.ARMED
        assert result.score <= 79
        assert "stock_benchmark_context_missing" in result.risk_flags


def test_bearish_stock_benchmark_context_blocks_long_setup() -> None:
    with make_session() as db:
        watchlist_item = create_watchlist_item(db)
        create_series_with_data(db, watchlist_item, Timeframe.ONE_WEEK, Decimal("120"))
        daily = create_series_with_base_breakout(
            db,
            watchlist_item,
            Timeframe.ONE_DAY,
            breakout_close=Decimal("111"),
        )
        create_series_with_base_breakout(
            db,
            watchlist_item,
            Timeframe.FOUR_HOURS,
            breakout_close=Decimal("111"),
        )
        spy = create_watchlist_item(db, symbol="SPY")
        create_series_with_data(
            db,
            spy,
            Timeframe.ONE_DAY,
            Decimal("350"),
            trend="bearish",
        )
        qqq = create_watchlist_item(db, symbol="QQQ")
        create_series_with_data(
            db,
            qqq,
            Timeframe.ONE_DAY,
            Decimal("300"),
            trend="bearish",
        )

        result = evaluate_mvp_signal_engine(
            build_signal_engine_input(
                db,
                daily,
                load_series_candles(db, daily),
                load_series_snapshots(db, daily),
            )
        )

        assert result.status == SignalStatus.NO_SETUP
        assert "stock_market_regime_bearish" in result.no_trade_reasons


def test_relative_strength_underperformance_blocks_mixed_regime_setup() -> None:
    with make_session() as db:
        watchlist_item = create_watchlist_item(db)
        create_series_with_data(db, watchlist_item, Timeframe.ONE_WEEK, Decimal("120"))
        daily = create_series_with_base_breakout(
            db,
            watchlist_item,
            Timeframe.ONE_DAY,
            breakout_close=Decimal("111"),
        )
        create_series_with_base_breakout(
            db,
            watchlist_item,
            Timeframe.FOUR_HOURS,
            breakout_close=Decimal("111"),
        )
        spy = create_watchlist_item(db, symbol="SPY")
        create_series_with_data(
            db,
            spy,
            Timeframe.ONE_DAY,
            Decimal("350"),
            first_close=Decimal("1"),
        )
        qqq = create_watchlist_item(db, symbol="QQQ")
        create_series_with_data(
            db,
            qqq,
            Timeframe.ONE_DAY,
            Decimal("300"),
            trend="neutral",
            first_close=Decimal("1"),
        )

        result = evaluate_mvp_signal_engine(
            build_signal_engine_input(
                db,
                daily,
                load_series_candles(db, daily),
                load_series_snapshots(db, daily),
            )
        )

        assert result.status == SignalStatus.NO_SETUP
        assert "relative_strength_underperforming" in result.no_trade_reasons


def test_wick_only_base_breakout_does_not_arm() -> None:
    with make_session() as db:
        watchlist_item = create_watchlist_item(db)
        create_series_with_data(db, watchlist_item, Timeframe.ONE_WEEK, Decimal("120"))
        daily = create_series_with_base_breakout(
            db,
            watchlist_item,
            Timeframe.ONE_DAY,
            breakout_close=Decimal("109"),
            breakout_high=Decimal("112"),
        )
        create_series_with_base_breakout(
            db,
            watchlist_item,
            Timeframe.FOUR_HOURS,
            breakout_close=Decimal("109"),
            breakout_high=Decimal("112"),
        )

        result = evaluate_mvp_signal_engine(
            build_signal_engine_input(
                db,
                daily,
                load_series_candles(db, daily),
                load_series_snapshots(db, daily),
            )
        )

        assert result.status != SignalStatus.ARMED
        assert "wick_without_close_confirmation" in result.risk_flags


def test_analyze_market_data_persists_base_breakout_signal() -> None:
    with make_session() as db:
        watchlist_item = create_watchlist_item(db)
        create_series_with_data(db, watchlist_item, Timeframe.ONE_WEEK, Decimal("120"))
        daily = create_series_with_base_breakout(
            db,
            watchlist_item,
            Timeframe.ONE_DAY,
            breakout_close=Decimal("111"),
            with_snapshots=False,
        )
        create_series_with_base_breakout(
            db,
            watchlist_item,
            Timeframe.FOUR_HOURS,
            breakout_close=Decimal("111"),
        )

        result = analyze_market_data_series(db, daily)

        assert result.signal.strategy_type == StrategyType.BASE_BREAKOUT_LONG
        assert result.signal.status == SignalStatus.ARMED
        assert result.signal.trigger_level == Decimal("110")


def test_missing_weekly_context_returns_conservative_no_setup() -> None:
    with make_session() as db:
        watchlist_item = create_watchlist_item(db)
        daily = create_series_with_data(db, watchlist_item, Timeframe.ONE_DAY, Decimal("100"))
        create_series_with_data(db, watchlist_item, Timeframe.FOUR_HOURS, Decimal("103"))

        result = evaluate_mvp_signal_engine(
            build_signal_engine_input(
                db,
                daily,
                load_series_candles(db, daily),
                load_series_snapshots(db, daily),
            )
        )

        assert result.status == SignalStatus.NO_SETUP
        assert "missing_1W_data" in result.risk_flags
        assert "poor_data_quality" in result.no_trade_reasons


def test_missing_4h_trigger_data_prevents_armed_status() -> None:
    with make_session() as db:
        watchlist_item = create_watchlist_item(db)
        create_series_with_data(db, watchlist_item, Timeframe.ONE_WEEK, Decimal("120"))
        daily = create_series_with_data(db, watchlist_item, Timeframe.ONE_DAY, Decimal("100"))

        result = evaluate_mvp_signal_engine(
            build_signal_engine_input(
                db,
                daily,
                load_series_candles(db, daily),
                load_series_snapshots(db, daily),
            )
        )

    assert result.status == SignalStatus.NO_SETUP
    assert "missing_4H_data" in result.risk_flags


def test_stale_required_timeframe_data_prevents_armed_status() -> None:
    with make_session() as db:
        watchlist_item = create_watchlist_item(db)
        create_series_with_data(db, watchlist_item, Timeframe.ONE_WEEK, Decimal("120"))
        daily = create_series_with_data(
            db,
            watchlist_item,
            Timeframe.ONE_DAY,
            Decimal("100"),
            freshness_status=MarketDataFreshnessStatus.STALE,
        )
        create_series_with_data(db, watchlist_item, Timeframe.FOUR_HOURS, Decimal("103"))

        result = evaluate_mvp_signal_engine(
            build_signal_engine_input(
                db,
                daily,
                load_series_candles(db, daily),
                load_series_snapshots(db, daily),
            )
        )

        assert result.status == SignalStatus.NO_SETUP
        assert "market_data_stale_1D" in result.risk_flags
        assert "poor_data_quality" in result.no_trade_reasons


def test_unknown_required_timeframe_data_prevents_armed_status() -> None:
    with make_session() as db:
        watchlist_item = create_watchlist_item(db)
        weekly = create_series_with_data(
            db,
            watchlist_item,
            Timeframe.ONE_WEEK,
            Decimal("120"),
            freshness_status=MarketDataFreshnessStatus.UNKNOWN,
        )
        daily = create_series_with_data(db, watchlist_item, Timeframe.ONE_DAY, Decimal("100"))
        create_series_with_data(db, watchlist_item, Timeframe.FOUR_HOURS, Decimal("103"))

        result = evaluate_mvp_signal_engine(
            build_signal_engine_input(
                db,
                daily,
                load_series_candles(db, daily),
                load_series_snapshots(db, daily),
            )
        )

        assert weekly.freshness_status == MarketDataFreshnessStatus.UNKNOWN
        assert result.status == SignalStatus.NO_SETUP
        assert "market_data_unknown_1W" in result.risk_flags
        assert "poor_data_quality" in result.no_trade_reasons


def test_single_daily_import_cannot_produce_armed_setup() -> None:
    with make_session() as db:
        watchlist_item = create_watchlist_item(db)
        daily = create_series_with_data(db, watchlist_item, Timeframe.ONE_DAY, Decimal("100"))

        result = evaluate_mvp_signal_engine(
            build_signal_engine_input(
                db,
                daily,
                load_series_candles(db, daily),
                load_series_snapshots(db, daily),
            )
        )

        assert result.status == SignalStatus.NO_SETUP
        assert "missing_1W_data" in result.risk_flags
        assert "missing_4H_data" in result.risk_flags


def test_missing_source_history_returns_no_strategy_input() -> None:
    with make_session() as db:
        watchlist_item = create_watchlist_item(db)
        daily = create_series_with_data(
            db,
            watchlist_item,
            Timeframe.ONE_DAY,
            Decimal("100"),
            candle_count=20,
        )

        result = evaluate_mvp_signal_engine(
            build_signal_engine_input(
                db,
                daily,
                load_series_candles(db, daily),
                load_series_snapshots(db, daily),
            )
        )

        assert result.status == SignalStatus.NO_SETUP
        assert "1D_insufficient_candle_history" in result.risk_flags


def make_session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def create_watchlist_item(db: Session, symbol: str = "AAPL") -> WatchlistItem:
    user = db.query(User).filter(User.email == "admin@example.com").one_or_none()
    if user is None:
        user = User(
            email="admin@example.com",
            password_hash="hash",
            display_name=None,
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(user)
        db.flush()
    item = WatchlistItem(
        symbol=symbol,
        asset_class=AssetClass.STOCK,
        user_id=user.id,
        name=None,
        exchange=None,
        currency=None,
        notes=None,
        last_analyzed_at=None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def create_series_with_data(
    db: Session,
    watchlist_item: WatchlistItem,
    timeframe: Timeframe,
    latest_close: Decimal,
    candle_count: int = 201,
    freshness_status: MarketDataFreshnessStatus = MarketDataFreshnessStatus.FRESH,
    trend: str = "bullish",
    first_close: Decimal | None = None,
) -> MarketDataSeries:
    series = MarketDataSeries(
        watchlist_item_id=watchlist_item.id,
        source=MarketDataSource.TRADINGVIEW_CSV,
        timeframe=timeframe,
        candle_count=candle_count,
        status=MarketDataStatus.ANALYZED,
        freshness_status=freshness_status,
        validation_errors=None,
        file_name=f"{timeframe.value}.csv",
    )
    db.add(series)
    db.flush()

    start = datetime(2024, 1, 1, tzinfo=UTC)
    if first_close is None:
        first_close = (
            latest_close + Decimal(candle_count - 1)
            if trend == "bearish"
            else latest_close - Decimal(candle_count - 1)
        )
    for index in range(candle_count):
        close = first_close + (
            (latest_close - first_close) * Decimal(index) / Decimal(candle_count - 1)
        )
        if trend == "bearish":
            ema50 = close + Decimal("5")
            ema200 = close + Decimal("20")
        elif trend == "neutral":
            ema50 = latest_close - Decimal("5") + (
                Decimal(candle_count - 1 - index) / Decimal("10")
            )
            ema200 = close - Decimal("20")
        else:
            ema50 = close - Decimal("5")
            ema200 = close - Decimal("20")
        timestamp = start + timedelta(days=index)
        db.add(
            MarketDataCandle(
                series_id=series.id,
                timestamp=timestamp,
                open=close - Decimal("1"),
                high=close + Decimal("2"),
                low=close - Decimal("2"),
                close=close,
                volume=Decimal("1000"),
            )
        )
        db.add(
            IndicatorSnapshot(
                series_id=series.id,
                timestamp=timestamp,
                ema20=close - Decimal("2"),
                ema50=ema50,
                ema200=ema200,
                rsi14=Decimal("52"),
                atr14=Decimal("2"),
                volume_avg20=Decimal("1000"),
                relative_volume=Decimal("0.8"),
            )
        )
    db.commit()
    db.refresh(series)
    return series


def create_series_with_base_breakout(
    db: Session,
    watchlist_item: WatchlistItem,
    timeframe: Timeframe,
    breakout_close: Decimal,
    breakout_high: Decimal | None = None,
    with_snapshots: bool = True,
    freshness_status: MarketDataFreshnessStatus = MarketDataFreshnessStatus.FRESH,
) -> MarketDataSeries:
    candle_count = 201
    series = MarketDataSeries(
        watchlist_item_id=watchlist_item.id,
        source=MarketDataSource.TRADINGVIEW_CSV,
        timeframe=timeframe,
        candle_count=candle_count,
        status=MarketDataStatus.ANALYZED,
        freshness_status=freshness_status,
        validation_errors=None,
        file_name=f"{timeframe.value}-base.csv",
    )
    db.add(series)
    db.flush()

    start = datetime(2024, 1, 1, tzinfo=UTC)
    for index in range(candle_count):
        timestamp = start + timedelta(days=index)
        if index >= candle_count - 21 and index < candle_count - 1:
            close = Decimal("105")
            high = Decimal("110")
            low = Decimal("100")
        elif index == candle_count - 1:
            close = breakout_close
            high = breakout_high or breakout_close + Decimal("1")
            low = Decimal("106")
        else:
            close = Decimal("90") + Decimal(index) * Decimal("0.05")
            high = close + Decimal("1")
            low = close - Decimal("1")
        db.add(
            MarketDataCandle(
                series_id=series.id,
                timestamp=timestamp,
                open=close - Decimal("0.5"),
                high=high,
                low=low,
                close=close,
                volume=Decimal("1000"),
            )
        )
        if with_snapshots:
            db.add(
                IndicatorSnapshot(
                    series_id=series.id,
                    timestamp=timestamp,
                    ema20=close - Decimal("1"),
                    ema50=close - Decimal("2"),
                    ema200=close - Decimal("20"),
                    rsi14=Decimal("55"),
                    atr14=Decimal("2"),
                    volume_avg20=Decimal("1000"),
                    relative_volume=Decimal("0.8"),
                )
            )
    db.commit()
    db.refresh(series)
    return series


def load_series_candles(db: Session, series: MarketDataSeries) -> list[MarketDataCandle]:
    return (
        db.query(MarketDataCandle)
        .filter(MarketDataCandle.series_id == series.id)
        .order_by(MarketDataCandle.timestamp)
        .all()
    )


def load_series_snapshots(db: Session, series: MarketDataSeries) -> list[IndicatorSnapshot]:
    return (
        db.query(IndicatorSnapshot)
        .filter(IndicatorSnapshot.series_id == series.id)
        .order_by(IndicatorSnapshot.timestamp)
        .all()
    )

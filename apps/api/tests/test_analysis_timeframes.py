from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.enums import (
    AssetClass,
    MarketDataSource,
    MarketDataStatus,
    SignalStatus,
    Timeframe,
    UserRole,
)
from app.models.market_data import IndicatorSnapshot, MarketDataCandle, MarketDataSeries
from app.models.user import User
from app.models.watchlist import WatchlistItem
from app.services.analysis import build_signal_engine_input
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


def create_watchlist_item(db: Session) -> WatchlistItem:
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
        symbol="AAPL",
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
) -> MarketDataSeries:
    series = MarketDataSeries(
        watchlist_item_id=watchlist_item.id,
        source=MarketDataSource.TRADINGVIEW_CSV,
        timeframe=timeframe,
        candle_count=candle_count,
        status=MarketDataStatus.ANALYZED,
        validation_errors=None,
        file_name=f"{timeframe.value}.csv",
    )
    db.add(series)
    db.flush()

    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    first_close = latest_close - Decimal(candle_count - 1)
    for index in range(candle_count):
        close = first_close + Decimal(index)
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
                ema50=close - Decimal("5"),
                ema200=close - Decimal("20"),
                rsi14=Decimal("52"),
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

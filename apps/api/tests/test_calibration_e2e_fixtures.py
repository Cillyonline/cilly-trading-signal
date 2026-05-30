from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.enums import (
    AssetClass,
    MarketDataFreshnessStatus,
    MarketDataSource,
    MarketDataStatus,
    ScoreClass,
    SignalStatus,
    StrategyType,
    Timeframe,
    UserRole,
)
from app.models.market_data import IndicatorSnapshot, MarketDataCandle, MarketDataSeries
from app.models.user import User
from app.models.watchlist import WatchlistItem
from app.services.analysis import build_signal_engine_input
from app.services.analysis_quality import build_analysis_quality_report
from app.strategies.orchestrator import evaluate_mvp_signal_engine


def test_e2e_stock_base_breakout_with_supportive_benchmarks_arms() -> None:
    with make_session() as db:
        candidate = create_watchlist_item(db, "AAPL", AssetClass.STOCK)
        create_series_with_data(db, candidate, Timeframe.ONE_WEEK, Decimal("120"))
        daily = create_series_with_base_breakout(db, candidate, Timeframe.ONE_DAY, Decimal("111"))
        create_series_with_base_breakout(db, candidate, Timeframe.FOUR_HOURS, Decimal("111"))
        create_benchmark(db, "SPY", AssetClass.STOCK, Decimal("350"), first_close=Decimal("330"))
        create_benchmark(db, "QQQ", AssetClass.STOCK, Decimal("300"), first_close=Decimal("285"))

        result = evaluate_from_series(db, daily)
        quality = quality_statuses(result)

        assert result.strategy_type == StrategyType.BASE_BREAKOUT_LONG
        assert result.status == SignalStatus.ARMED
        assert result.score_class == ScoreClass.A_SETUP
        assert "stock_benchmark_context_missing" not in result.risk_flags
        assert quality["market_regime"] == "passed"
        assert quality["asset_overlay"] == "passed"
        assert quality["trigger"] == "passed"
        assert quality["risk_plan"] == "passed"


def test_e2e_stock_missing_benchmark_context_caps_confidence() -> None:
    with make_session() as db:
        candidate = create_watchlist_item(db, "MSFT", AssetClass.STOCK)
        create_series_with_data(db, candidate, Timeframe.ONE_WEEK, Decimal("120"))
        daily = create_series_with_base_breakout(db, candidate, Timeframe.ONE_DAY, Decimal("111"))
        create_series_with_base_breakout(db, candidate, Timeframe.FOUR_HOURS, Decimal("111"))

        result = evaluate_from_series(db, daily)
        quality = quality_statuses(result)

        assert result.status == SignalStatus.ARMED
        assert result.score_class == ScoreClass.B_SETUP
        assert result.score <= 79
        assert "stock_benchmark_context_missing" in result.risk_flags
        assert quality["market_regime"] == "warning"
        assert quality["data_quality"] == "warning"


def test_e2e_stock_stale_benchmark_context_warns_and_caps() -> None:
    with make_session() as db:
        candidate = create_watchlist_item(db, "NVDA", AssetClass.STOCK)
        create_series_with_data(db, candidate, Timeframe.ONE_WEEK, Decimal("120"))
        daily = create_series_with_base_breakout(db, candidate, Timeframe.ONE_DAY, Decimal("111"))
        create_series_with_base_breakout(db, candidate, Timeframe.FOUR_HOURS, Decimal("111"))
        create_benchmark(
            db,
            "SPY",
            AssetClass.STOCK,
            Decimal("350"),
            first_close=Decimal("330"),
            freshness_status=MarketDataFreshnessStatus.STALE,
        )
        create_benchmark(db, "QQQ", AssetClass.STOCK, Decimal("300"), first_close=Decimal("285"))

        result = evaluate_from_series(db, daily)
        quality = quality_statuses(result)

        assert result.status == SignalStatus.ARMED
        assert result.score_class == ScoreClass.B_SETUP
        assert "stock_benchmark_context_stale" in result.risk_flags
        assert quality["market_regime"] == "warning"
        assert quality["data_quality"] == "warning"


def test_e2e_stock_mixed_regime_and_underperformance_blocks() -> None:
    with make_session() as db:
        candidate = create_watchlist_item(db, "LAG", AssetClass.STOCK)
        create_series_with_data(db, candidate, Timeframe.ONE_WEEK, Decimal("120"))
        daily = create_series_with_base_breakout(db, candidate, Timeframe.ONE_DAY, Decimal("111"))
        create_series_with_base_breakout(db, candidate, Timeframe.FOUR_HOURS, Decimal("111"))
        create_benchmark(db, "SPY", AssetClass.STOCK, Decimal("350"), first_close=Decimal("1"))
        create_benchmark(
            db,
            "QQQ",
            AssetClass.STOCK,
            Decimal("300"),
            trend="neutral",
            first_close=Decimal("1"),
        )

        result = evaluate_from_series(db, daily)
        quality = quality_statuses(result)

        assert result.status == SignalStatus.NO_SETUP
        assert "stock_market_regime_mixed" in result.risk_flags
        assert "relative_strength_underperforming" in result.no_trade_reasons
        assert quality["asset_overlay"] == "blocked"


def test_e2e_crypto_base_breakout_with_supportive_btc_eth_arms() -> None:
    with make_session() as db:
        candidate = create_watchlist_item(db, "SOLUSDT", AssetClass.CRYPTO)
        create_series_with_data(db, candidate, Timeframe.ONE_WEEK, Decimal("120"))
        daily = create_series_with_base_breakout(db, candidate, Timeframe.ONE_DAY, Decimal("111"))
        create_series_with_base_breakout(db, candidate, Timeframe.FOUR_HOURS, Decimal("111"))
        create_benchmark(
            db, "BTCUSDT", AssetClass.CRYPTO, Decimal("70000"), first_close=Decimal("68000")
        )
        create_benchmark(
            db, "ETHUSDT", AssetClass.CRYPTO, Decimal("3500"), first_close=Decimal("3300")
        )

        result = evaluate_from_series(db, daily)
        quality = quality_statuses(result)

        assert result.status == SignalStatus.ARMED
        assert result.score_class == ScoreClass.A_SETUP
        assert "crypto_regime_context_missing" not in result.risk_flags
        assert quality["market_regime"] == "passed"
        assert quality["asset_overlay"] == "passed"


def test_e2e_crypto_bearish_btc_eth_blocks_long_setup() -> None:
    with make_session() as db:
        candidate = create_watchlist_item(db, "SOLUSDT", AssetClass.CRYPTO)
        create_series_with_data(db, candidate, Timeframe.ONE_WEEK, Decimal("120"))
        daily = create_series_with_base_breakout(db, candidate, Timeframe.ONE_DAY, Decimal("111"))
        create_series_with_base_breakout(db, candidate, Timeframe.FOUR_HOURS, Decimal("111"))
        create_benchmark(db, "BTCUSDT", AssetClass.CRYPTO, Decimal("70000"), trend="bearish")
        create_benchmark(db, "ETHUSDT", AssetClass.CRYPTO, Decimal("3500"), trend="bearish")

        result = evaluate_from_series(db, daily)
        quality = quality_statuses(result)

        assert result.status == SignalStatus.NO_SETUP
        assert "crypto_regime_bearish" in result.no_trade_reasons
        assert quality["market_regime"] == "blocked"


def make_session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return testing_session()


def create_watchlist_item(
    db: Session, symbol: str, asset_class: AssetClass
) -> WatchlistItem:
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
        asset_class=asset_class,
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


def create_benchmark(
    db: Session,
    symbol: str,
    asset_class: AssetClass,
    latest_close: Decimal,
    trend: str = "bullish",
    first_close: Decimal | None = None,
    freshness_status: MarketDataFreshnessStatus = MarketDataFreshnessStatus.FRESH,
) -> MarketDataSeries:
    return create_series_with_data(
        db,
        create_watchlist_item(db, symbol, asset_class),
        Timeframe.ONE_DAY,
        latest_close,
        trend=trend,
        first_close=first_close,
        freshness_status=freshness_status,
    )


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
    series = create_series(db, watchlist_item, timeframe, candle_count, freshness_status)
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
        add_candle_and_snapshot(
            db,
            series,
            timestamp=start + timedelta(days=index),
            close=close,
            high=close + Decimal("2"),
            low=close - Decimal("2"),
            ema20=close - Decimal("2"),
            ema50=ema50,
            ema200=ema200,
        )
    db.commit()
    db.refresh(series)
    return series


def create_series_with_base_breakout(
    db: Session,
    watchlist_item: WatchlistItem,
    timeframe: Timeframe,
    breakout_close: Decimal,
    freshness_status: MarketDataFreshnessStatus = MarketDataFreshnessStatus.FRESH,
) -> MarketDataSeries:
    candle_count = 201
    series = create_series(db, watchlist_item, timeframe, candle_count, freshness_status)
    start = datetime(2024, 1, 1, tzinfo=UTC)
    for index in range(candle_count):
        if index >= candle_count - 21 and index < candle_count - 1:
            close = Decimal("105")
            high = Decimal("110")
            low = Decimal("100")
        elif index == candle_count - 1:
            close = breakout_close
            high = breakout_close + Decimal("1")
            low = Decimal("106")
        else:
            close = Decimal("90") + Decimal(index) * Decimal("0.05")
            high = close + Decimal("1")
            low = close - Decimal("1")
        add_candle_and_snapshot(
            db,
            series,
            timestamp=start + timedelta(days=index),
            close=close,
            high=high,
            low=low,
            ema20=close - Decimal("1"),
            ema50=close - Decimal("2"),
            ema200=close - Decimal("20"),
            rsi14=Decimal("55"),
        )
    db.commit()
    db.refresh(series)
    return series


def create_series(
    db: Session,
    watchlist_item: WatchlistItem,
    timeframe: Timeframe,
    candle_count: int,
    freshness_status: MarketDataFreshnessStatus,
) -> MarketDataSeries:
    series = MarketDataSeries(
        watchlist_item_id=watchlist_item.id,
        source=MarketDataSource.TRADINGVIEW_CSV,
        timeframe=timeframe,
        candle_count=candle_count,
        status=MarketDataStatus.ANALYZED,
        freshness_status=freshness_status,
        validation_errors=None,
        file_name=f"{watchlist_item.symbol}-{timeframe.value}.csv",
    )
    db.add(series)
    db.flush()
    return series


def add_candle_and_snapshot(
    db: Session,
    series: MarketDataSeries,
    timestamp: datetime,
    close: Decimal,
    high: Decimal,
    low: Decimal,
    ema20: Decimal,
    ema50: Decimal,
    ema200: Decimal,
    rsi14: Decimal = Decimal("52"),
) -> None:
    db.add(
        MarketDataCandle(
            series_id=series.id,
            timestamp=timestamp,
            open=close - Decimal("1"),
            high=high,
            low=low,
            close=close,
            volume=Decimal("1000"),
        )
    )
    db.add(
        IndicatorSnapshot(
            series_id=series.id,
            timestamp=timestamp,
            ema20=ema20,
            ema50=ema50,
            ema200=ema200,
            rsi14=rsi14,
            atr14=Decimal("2"),
            volume_avg20=Decimal("1000"),
            relative_volume=Decimal("0.8"),
        )
    )


def evaluate_from_series(db: Session, series: MarketDataSeries):
    candles = load_series_candles(db, series)
    snapshots = load_series_snapshots(db, series)
    return evaluate_mvp_signal_engine(build_signal_engine_input(db, series, candles, snapshots))


def quality_statuses(result) -> dict[str, str]:
    return {check["key"]: check["status"] for check in build_analysis_quality_report(result)}


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

from datetime import UTC, datetime, timedelta

from app.models.enums import (
    MarketDataFreshnessStatus,
    MarketDataSource,
    MarketDataSyncStatus,
    Timeframe,
)
from app.models.market_data import MarketDataSeries
from app.services.market_data_sync import (
    MarketDataSyncPlan,
    MarketDataSyncResult,
    build_market_data_sync_plan,
    evaluate_market_data_freshness,
    sync_market_data_series,
)


class FakeMarketDataProvider:
    def __init__(self, result: MarketDataSyncResult) -> None:
        self.result = result
        self.requests: list[MarketDataSyncPlan] = []

    def sync(self, plan: MarketDataSyncPlan) -> MarketDataSyncResult:
        self.requests.append(plan)
        return self.result


def test_build_market_data_sync_plan_normalizes_provider_metadata() -> None:
    plan = build_market_data_sync_plan(
        symbol=" btcusdt ",
        timeframe=Timeframe.ONE_DAY,
        provider_sync_enabled=True,
        provider_name=" Alpha_Vantage ",
    )

    assert plan.enabled is True
    assert plan.symbol == "BTCUSDT"
    assert plan.provider_name == "alpha_vantage"
    assert plan.provider_symbol == "BTCUSDT"
    assert plan.provider_timeframe == "1D"


def test_sync_skips_without_calling_provider_when_disabled() -> None:
    now = datetime(2026, 5, 29, tzinfo=UTC)
    series = make_series(end_time=now - timedelta(days=1))
    provider = FakeMarketDataProvider(
        MarketDataSyncResult(
            sync_status=MarketDataSyncStatus.SUCCESS,
            freshness_status=MarketDataFreshnessStatus.FRESH,
        )
    )
    plan = build_market_data_sync_plan(
        symbol="AAPL",
        timeframe=Timeframe.ONE_DAY,
        provider_sync_enabled=False,
        provider_name="alpha_vantage",
    )

    result = sync_market_data_series(series, plan, provider, now=now)

    assert provider.requests == []
    assert result.sync_status == MarketDataSyncStatus.SKIPPED
    assert result.freshness_status == MarketDataFreshnessStatus.FRESH
    assert series.sync_status == MarketDataSyncStatus.SKIPPED
    assert series.sync_error_code == "sync_disabled"


def test_sync_applies_success_result_without_network_dependency() -> None:
    now = datetime(2026, 5, 29, tzinfo=UTC)
    data_end_at = now - timedelta(hours=2)
    series = make_series()
    provider = FakeMarketDataProvider(
        MarketDataSyncResult(
            sync_status=MarketDataSyncStatus.SUCCESS,
            freshness_status=MarketDataFreshnessStatus.FRESH,
            provider_name="alpha_vantage",
            provider_symbol="AAPL",
            provider_timeframe="1D",
            data_end_at=data_end_at,
        )
    )
    plan = build_market_data_sync_plan(
        symbol="AAPL",
        timeframe=Timeframe.ONE_DAY,
        provider_sync_enabled=True,
        provider_name="alpha_vantage",
    )

    result = sync_market_data_series(series, plan, provider, now=now)

    assert provider.requests == [plan]
    assert result.sync_status == MarketDataSyncStatus.SUCCESS
    assert series.source == MarketDataSource.PROVIDER
    assert series.provider_name == "alpha_vantage"
    assert series.end_time == data_end_at
    assert series.last_synced_at == now
    assert series.sync_error_code is None


def test_sync_applies_failed_result_safely() -> None:
    now = datetime(2026, 5, 29, tzinfo=UTC)
    series = make_series(end_time=None)
    provider = FakeMarketDataProvider(
        MarketDataSyncResult(
            sync_status=MarketDataSyncStatus.FAILED,
            freshness_status=MarketDataFreshnessStatus.FAILED,
            provider_name="alpha_vantage",
            error_code="provider_error",
            error_message="Provider request failed.",
        )
    )
    plan = build_market_data_sync_plan(
        symbol="AAPL",
        timeframe=Timeframe.ONE_DAY,
        provider_sync_enabled=True,
        provider_name="alpha_vantage",
    )

    result = sync_market_data_series(series, plan, provider, now=now)

    assert result.sync_status == MarketDataSyncStatus.FAILED
    assert series.freshness_status == MarketDataFreshnessStatus.FAILED
    assert series.sync_error_code == "provider_error"
    assert series.sync_error_message == "Provider request failed."


def test_sync_applies_partial_result_safely() -> None:
    now = datetime(2026, 5, 29, tzinfo=UTC)
    series = make_series()
    provider = FakeMarketDataProvider(
        MarketDataSyncResult(
            sync_status=MarketDataSyncStatus.PARTIAL,
            freshness_status=MarketDataFreshnessStatus.PARTIAL,
            provider_name="alpha_vantage",
            data_end_at=now - timedelta(days=2),
            error_code="missing_candles",
            error_message="Provider returned an incomplete candle range.",
        )
    )
    plan = build_market_data_sync_plan(
        symbol="AAPL",
        timeframe=Timeframe.ONE_DAY,
        provider_sync_enabled=True,
        provider_name="alpha_vantage",
    )

    sync_market_data_series(series, plan, provider, now=now)

    assert series.sync_status == MarketDataSyncStatus.PARTIAL
    assert series.freshness_status == MarketDataFreshnessStatus.PARTIAL
    assert series.sync_error_code == "missing_candles"


def test_evaluate_market_data_freshness_marks_old_data_stale() -> None:
    now = datetime(2026, 5, 29, tzinfo=UTC)
    series = make_series(end_time=now - timedelta(days=4), timeframe=Timeframe.ONE_DAY)

    assert evaluate_market_data_freshness(series, now) == MarketDataFreshnessStatus.STALE


def make_series(
    *,
    end_time: datetime | None = None,
    timeframe: Timeframe = Timeframe.ONE_DAY,
) -> MarketDataSeries:
    return MarketDataSeries(
        watchlist_item_id=1,
        source=MarketDataSource.TRADINGVIEW_CSV,
        timeframe=timeframe,
        end_time=end_time,
        candle_count=0,
        sync_status=MarketDataSyncStatus.NOT_APPLICABLE,
    )

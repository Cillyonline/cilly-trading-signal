from datetime import UTC, datetime, timedelta

from app.models.enums import (
    MarketDataFreshnessStatus,
    MarketDataSource,
    MarketDataSyncStatus,
    Timeframe,
)
from app.models.market_data import MarketDataSeries
from app.services.market_data_sync import (
    AlphaVantageDailyProvider,
    MarketDataSyncPlan,
    MarketDataSyncResult,
    build_market_data_sync_plan,
    evaluate_market_data_freshness,
    parse_alpha_vantage_daily_response,
    sync_market_data_series,
)


class FakeMarketDataProvider:
    def __init__(self, result: MarketDataSyncResult) -> None:
        self.result = result
        self.requests: list[MarketDataSyncPlan] = []

    def sync(self, plan: MarketDataSyncPlan) -> MarketDataSyncResult:
        self.requests.append(plan)
        return self.result


class FakeProviderTransport:
    def __init__(self, payload: object) -> None:
        self.payload = payload
        self.urls: list[str] = []

    def get_json(self, url: str) -> object:
        self.urls.append(url)
        return self.payload


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


def test_alpha_vantage_daily_provider_parses_success_response_without_network() -> None:
    transport = FakeProviderTransport(alpha_vantage_payload("2026-05-29"))
    provider = AlphaVantageDailyProvider("test-api-key", transport=transport)
    plan = build_market_data_sync_plan(
        symbol="AAPL",
        timeframe=Timeframe.ONE_DAY,
        provider_sync_enabled=True,
        provider_name="alpha_vantage",
    )

    result = provider.sync(plan)

    assert len(transport.urls) == 1
    assert "test-api-key" in transport.urls[0]
    assert result.sync_status == MarketDataSyncStatus.SUCCESS
    assert result.provider_name == "alpha_vantage"
    assert result.data_end_at == datetime(2026, 5, 29, tzinfo=UTC)


def test_alpha_vantage_daily_provider_rejects_unsupported_timeframe() -> None:
    transport = FakeProviderTransport(alpha_vantage_payload("2026-05-29"))
    provider = AlphaVantageDailyProvider("test-api-key", transport=transport)
    plan = build_market_data_sync_plan(
        symbol="AAPL",
        timeframe=Timeframe.FOUR_HOURS,
        provider_sync_enabled=True,
        provider_name="alpha_vantage",
    )

    result = provider.sync(plan)

    assert transport.urls == []
    assert result.sync_status == MarketDataSyncStatus.FAILED
    assert result.error_code == "unsupported_timeframe"


def test_alpha_vantage_daily_provider_handles_rate_limit_response() -> None:
    provider = AlphaVantageDailyProvider(
        "test-api-key",
        transport=FakeProviderTransport({"Note": "API call frequency exceeded."}),
    )
    plan = build_market_data_sync_plan(
        symbol="AAPL",
        timeframe=Timeframe.ONE_DAY,
        provider_sync_enabled=True,
        provider_name="alpha_vantage",
    )

    result = provider.sync(plan)

    assert result.sync_status == MarketDataSyncStatus.FAILED
    assert result.error_code == "provider_rate_limited"
    assert "test-api-key" not in (result.error_message or "")


def test_alpha_vantage_parser_handles_empty_series_as_partial() -> None:
    provider = AlphaVantageDailyProvider(
        "test-api-key",
        transport=FakeProviderTransport({"Time Series (Daily)": {}}),
    )
    plan = build_market_data_sync_plan(
        symbol="AAPL",
        timeframe=Timeframe.ONE_DAY,
        provider_sync_enabled=True,
        provider_name="alpha_vantage",
    )

    result = provider.sync(plan)

    assert result.sync_status == MarketDataSyncStatus.PARTIAL
    assert result.freshness_status == MarketDataFreshnessStatus.PARTIAL
    assert result.error_code == "provider_empty_response"


def test_alpha_vantage_parser_rejects_invalid_payload() -> None:
    candles, error_code = parse_alpha_vantage_daily_response(
        {"Time Series (Daily)": {"2026-05-29": {"1. open": "100"}}}
    )

    assert candles == []
    assert error_code == "provider_invalid_response"


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


def alpha_vantage_payload(date_text: str) -> dict[str, object]:
    return {
        "Meta Data": {"2. Symbol": "AAPL"},
        "Time Series (Daily)": {
            date_text: {
                "1. open": "100.00",
                "2. high": "110.00",
                "3. low": "95.00",
                "4. close": "105.00",
                "5. adjusted close": "105.00",
                "6. volume": "1234567",
            }
        },
    }

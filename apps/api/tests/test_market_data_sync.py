from datetime import UTC, datetime, timedelta
from decimal import Decimal
from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.enums import (
    MarketDataFreshnessStatus,
    MarketDataSource,
    MarketDataSyncStatus,
    Timeframe,
)
from app.models.market_data import MarketDataCandle, MarketDataSeries
from app.services.market_data_sync import (
    AlphaVantageDailyProvider,
    MarketDataSyncPlan,
    MarketDataSyncResult,
    ProviderCandle,
    TwelveDataProvider,
    build_market_data_sync_plan,
    evaluate_market_data_freshness,
    persist_provider_sync_result,
    parse_alpha_vantage_daily_response,
    parse_twelve_data_response,
    provider_failure_message,
    provider_timeframe_capabilities,
    sync_market_data_series,
)


@pytest.fixture()
def db_session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = testing_session()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


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


def test_provider_timeframe_capabilities_explain_alpha_vantage_limits() -> None:
    capabilities = provider_timeframe_capabilities("alpha_vantage")

    by_timeframe = {capability.timeframe: capability for capability in capabilities}
    assert by_timeframe[Timeframe.ONE_DAY].supported is True
    assert by_timeframe[Timeframe.FOUR_HOURS].supported is False
    assert "CSV fallback" in by_timeframe[Timeframe.FOUR_HOURS].reason


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


def test_sync_rejects_unsupported_timeframe_before_provider_call() -> None:
    series = make_series(timeframe=Timeframe.FOUR_HOURS)
    provider = FakeMarketDataProvider(
        MarketDataSyncResult(
            sync_status=MarketDataSyncStatus.SUCCESS,
            freshness_status=MarketDataFreshnessStatus.FRESH,
        )
    )
    plan = build_market_data_sync_plan(
        symbol="AAPL",
        timeframe=Timeframe.FOUR_HOURS,
        provider_sync_enabled=True,
        provider_name="alpha_vantage",
    )

    result = sync_market_data_series(series, plan, provider)

    assert provider.requests == []
    assert result.sync_status == MarketDataSyncStatus.FAILED
    assert result.error_code == "unsupported_timeframe"
    assert "4H" in (result.error_message or "")
    assert series.sync_error_code == "unsupported_timeframe"


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
    assert "CSV fallback" in (result.error_message or "")


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
    assert "CSV fallback" in (result.error_message or "")


def test_alpha_vantage_parser_rejects_invalid_payload() -> None:
    candles, error_code = parse_alpha_vantage_daily_response(
        {"Time Series (Daily)": {"2026-05-29": {"1. open": "100"}}}
    )

    assert candles == []
    assert error_code == "provider_invalid_response"


@pytest.mark.parametrize(
    ("timeframe", "expected_interval"),
    [
        (Timeframe.ONE_WEEK, "1week"),
        (Timeframe.ONE_DAY, "1day"),
        (Timeframe.FOUR_HOURS, "4h"),
    ],
)
def test_twelve_data_provider_parses_success_response_without_network(
    timeframe: Timeframe,
    expected_interval: str,
) -> None:
    transport = FakeProviderTransport(twelve_data_payload("2026-05-29"))
    provider = TwelveDataProvider("test-api-key", transport=transport)
    plan = build_market_data_sync_plan(
        symbol="AAPL",
        timeframe=timeframe,
        provider_sync_enabled=True,
        provider_name="twelve_data",
    )

    result = provider.sync(plan)

    assert len(transport.urls) == 1
    assert "test-api-key" in transport.urls[0]
    assert "apikey=test-api-key" in transport.urls[0]
    assert f"interval={expected_interval}" in transport.urls[0]
    assert result.sync_status == MarketDataSyncStatus.SUCCESS
    assert result.provider_name == "twelve_data"
    assert result.data_end_at == datetime(2026, 5, 29, tzinfo=UTC)
    assert len(result.candles) == 1
    assert result.candles[0].close == Decimal("105.00")


def test_twelve_data_provider_handles_rate_limit_response() -> None:
    provider = TwelveDataProvider(
        "test-api-key",
        transport=FakeProviderTransport({"status": "error", "code": 429, "message": "rate limit"}),
    )
    plan = build_market_data_sync_plan(
        symbol="AAPL",
        timeframe=Timeframe.ONE_DAY,
        provider_sync_enabled=True,
        provider_name="twelve_data",
    )

    result = provider.sync(plan)

    assert result.sync_status == MarketDataSyncStatus.FAILED
    assert result.error_code == "provider_rate_limited"
    assert "rate limit" in (result.error_message or "").lower()
    assert "test-api-key" not in (result.error_message or "")


def test_twelve_data_provider_handles_api_error_response() -> None:
    provider = TwelveDataProvider(
        "test-api-key",
        transport=FakeProviderTransport({"status": "error", "code": 400, "message": "bad request"}),
    )
    plan = build_market_data_sync_plan(
        symbol="AAPL",
        timeframe=Timeframe.ONE_DAY,
        provider_sync_enabled=True,
        provider_name="twelve_data",
    )

    result = provider.sync(plan)

    assert result.sync_status == MarketDataSyncStatus.FAILED
    assert result.error_code == "provider_symbol_or_entitlement"
    assert "entitlement" in (result.error_message or "").lower()
    assert "bad request" not in (result.error_message or "").lower()


@pytest.mark.parametrize(
    "error_code",
    [
        "provider_transport_error",
        "provider_rate_limited",
        "provider_symbol_or_entitlement",
        "provider_invalid_response",
        "provider_empty_response",
    ],
)
def test_provider_failure_messages_are_sanitized_and_operator_actionable(
    error_code: str,
) -> None:
    message = provider_failure_message(error_code)

    assert "CSV fallback" in message
    assert "test-api-key" not in message
    assert "apikey" not in message.lower()
    assert "http" not in message.lower()
    assert "bad request" not in message.lower()


def test_twelve_data_parser_handles_empty_values_as_partial() -> None:
    provider = TwelveDataProvider(
        "test-api-key",
        transport=FakeProviderTransport({"meta": {"symbol": "AAPL"}, "values": [], "status": "ok"}),
    )
    plan = build_market_data_sync_plan(
        symbol="AAPL",
        timeframe=Timeframe.ONE_DAY,
        provider_sync_enabled=True,
        provider_name="twelve_data",
    )

    result = provider.sync(plan)

    assert result.sync_status == MarketDataSyncStatus.PARTIAL
    assert result.freshness_status == MarketDataFreshnessStatus.PARTIAL
    assert result.error_code == "provider_empty_response"
    assert "CSV fallback" in (result.error_message or "")


def test_twelve_data_parser_rejects_invalid_payload() -> None:
    candles, error_code = parse_twelve_data_response(
        {"values": [{"datetime": "2026-05-29", "open": "100"}]}
    )

    assert candles == []
    assert error_code == "provider_invalid_response"


def test_twelve_data_parser_rejects_non_dict_payload() -> None:
    candles, error_code = parse_twelve_data_response(["not", "a", "dict"])

    assert candles == []
    assert error_code == "provider_invalid_response"


def test_twelve_data_parser_rejects_missing_values_field() -> None:
    candles, error_code = parse_twelve_data_response({"status": "ok"})

    assert candles == []
    assert error_code == "provider_invalid_response"


def test_provider_timeframe_capabilities_explain_twelve_data_limits() -> None:
    capabilities = provider_timeframe_capabilities("twelve_data")

    by_timeframe = {capability.timeframe: capability for capability in capabilities}
    assert by_timeframe[Timeframe.ONE_WEEK].supported is True
    assert by_timeframe[Timeframe.ONE_DAY].supported is True
    assert by_timeframe[Timeframe.FOUR_HOURS].supported is True


def test_persist_provider_sync_result_replaces_provider_candles(db_session) -> None:
    series = make_series(source=MarketDataSource.PROVIDER)
    db_session.add(series)
    db_session.flush()
    db_session.add(
        MarketDataCandle(
            series_id=series.id,
            timestamp=datetime(2026, 5, 1, tzinfo=UTC),
            open=Decimal("1"),
            high=Decimal("1"),
            low=Decimal("1"),
            close=Decimal("1"),
            volume=Decimal("1"),
        )
    )
    db_session.flush()
    result = MarketDataSyncResult(
        sync_status=MarketDataSyncStatus.SUCCESS,
        freshness_status=MarketDataFreshnessStatus.FRESH,
        provider_name="alpha_vantage",
        provider_symbol="AAPL",
        provider_timeframe="1D",
        candles=(
            provider_candle("2026-05-28", "100"),
            provider_candle("2026-05-29", "101"),
        ),
    )

    persist_provider_sync_result(db_session, series, result, datetime(2026, 5, 30, tzinfo=UTC))
    db_session.flush()

    candles = db_session.query(MarketDataCandle).order_by(MarketDataCandle.timestamp).all()
    assert [candle.close for candle in candles] == [
        Decimal("100.00000000"),
        Decimal("101.00000000"),
    ]
    assert series.candle_count == 2
    assert series.start_time == datetime(2026, 5, 28, tzinfo=UTC)
    assert series.end_time == datetime(2026, 5, 29, tzinfo=UTC)
    assert series.sync_status == MarketDataSyncStatus.SUCCESS


def test_persist_provider_sync_result_rejects_duplicate_timestamps(db_session) -> None:
    series = make_series(source=MarketDataSource.PROVIDER)
    db_session.add(series)
    db_session.flush()
    result = MarketDataSyncResult(
        sync_status=MarketDataSyncStatus.SUCCESS,
        freshness_status=MarketDataFreshnessStatus.FRESH,
        provider_name="alpha_vantage",
        candles=(
            provider_candle("2026-05-29", "100"),
            provider_candle("2026-05-29", "101"),
        ),
    )

    persist_provider_sync_result(db_session, series, result, datetime(2026, 5, 30, tzinfo=UTC))

    assert series.sync_status == MarketDataSyncStatus.FAILED
    assert series.freshness_status == MarketDataFreshnessStatus.FAILED
    assert series.sync_error_code == "duplicate_provider_candles"
    assert db_session.query(MarketDataCandle).count() == 0


def test_persist_provider_sync_result_marks_empty_success_partial_without_deleting_old_candles(
    db_session,
) -> None:
    series = make_series(source=MarketDataSource.PROVIDER)
    db_session.add(series)
    db_session.flush()
    db_session.add(
        MarketDataCandle(
            series_id=series.id,
            timestamp=datetime(2026, 5, 1, tzinfo=UTC),
            open=Decimal("1"),
            high=Decimal("1"),
            low=Decimal("1"),
            close=Decimal("1"),
            volume=Decimal("1"),
        )
    )
    db_session.flush()
    result = MarketDataSyncResult(
        sync_status=MarketDataSyncStatus.SUCCESS,
        freshness_status=MarketDataFreshnessStatus.FRESH,
        provider_name="alpha_vantage",
        candles=(),
    )

    persist_provider_sync_result(db_session, series, result, datetime(2026, 5, 30, tzinfo=UTC))

    assert series.sync_status == MarketDataSyncStatus.PARTIAL
    assert series.freshness_status == MarketDataFreshnessStatus.PARTIAL
    assert series.sync_error_code == "provider_empty_response"
    assert db_session.query(MarketDataCandle).count() == 1


def test_persist_provider_sync_result_does_not_mutate_csv_candles(db_session) -> None:
    series = make_series(source=MarketDataSource.TRADINGVIEW_CSV)
    db_session.add(series)
    db_session.flush()
    db_session.add(
        MarketDataCandle(
            series_id=series.id,
            timestamp=datetime(2026, 5, 1, tzinfo=UTC),
            open=Decimal("1"),
            high=Decimal("1"),
            low=Decimal("1"),
            close=Decimal("1"),
            volume=Decimal("1"),
        )
    )
    db_session.flush()
    result = MarketDataSyncResult(
        sync_status=MarketDataSyncStatus.SUCCESS,
        freshness_status=MarketDataFreshnessStatus.FRESH,
        provider_name="alpha_vantage",
        candles=(provider_candle("2026-05-29", "100"),),
    )

    persist_provider_sync_result(db_session, series, result, datetime(2026, 5, 30, tzinfo=UTC))

    assert series.source == MarketDataSource.TRADINGVIEW_CSV
    assert series.sync_status == MarketDataSyncStatus.FAILED
    assert series.sync_error_code == "provider_series_required"
    assert db_session.query(MarketDataCandle).count() == 1


def make_series(
    *,
    end_time: datetime | None = None,
    timeframe: Timeframe = Timeframe.ONE_DAY,
    source: MarketDataSource = MarketDataSource.TRADINGVIEW_CSV,
) -> MarketDataSeries:
    return MarketDataSeries(
        watchlist_item_id=1,
        source=source,
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


def twelve_data_payload(date_text: str) -> dict[str, object]:
    return {
        "meta": {"symbol": "AAPL", "interval": "1day"},
        "values": [
            {
                "datetime": date_text,
                "open": "100.00",
                "high": "110.00",
                "low": "95.00",
                "close": "105.00",
                "volume": "1234567",
            }
        ],
        "status": "ok",
    }


def provider_candle(date_text: str, close: str) -> ProviderCandle:
    value = Decimal(close)
    return ProviderCandle(
        timestamp=datetime.fromisoformat(date_text).replace(tzinfo=UTC),
        open=value,
        high=value,
        low=value,
        close=value,
        volume=Decimal("1000"),
    )

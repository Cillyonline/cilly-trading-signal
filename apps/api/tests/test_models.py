from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace

from sqlalchemy import JSON

from app.db.base import Base
from app.models import (
    Alert,
    AlertDeliveryStatus,
    AlertSource,
    AlertStatus,
    AlertType,
    IndicatorSnapshot,
    JournalEntry,
    MarketDataCandle,
    MarketDataFreshnessStatus,
    MarketDataSeries,
    NotificationLog,
    NotificationChannel,
    MarketDataSyncStatus,
    ScreenerImport,
    ScreenerImportSource,
    ScreenerImportStatus,
    ScreenerResult,
    ScreenerResultStatus,
    Settings,
    Signal,
    Timeframe,
    Trade,
    TradeEvent,
    User,
    WatchlistItem,
)
from app.schemas.alerts import AlertRead, NotificationLogRead
from app.schemas.screener import ScreenerImportRead, ScreenerResultRead


def test_mvp_model_tables_are_registered() -> None:
    expected_tables = {
        "users",
        "settings",
        "watchlist_items",
        "market_data_series",
        "market_data_candles",
        "indicator_snapshots",
        "signals",
        "alerts",
        "notification_logs",
        "screener_imports",
        "screener_results",
        "trades",
        "trade_events",
        "journal_entries",
    }

    assert expected_tables.issubset(Base.metadata.tables.keys())


def test_core_models_use_expected_table_names() -> None:
    assert User.__tablename__ == "users"
    assert Settings.__tablename__ == "settings"
    assert WatchlistItem.__tablename__ == "watchlist_items"
    assert MarketDataSeries.__tablename__ == "market_data_series"
    assert MarketDataCandle.__tablename__ == "market_data_candles"
    assert IndicatorSnapshot.__tablename__ == "indicator_snapshots"
    assert Signal.__tablename__ == "signals"
    assert Alert.__tablename__ == "alerts"
    assert NotificationLog.__tablename__ == "notification_logs"
    assert ScreenerImport.__tablename__ == "screener_imports"
    assert ScreenerResult.__tablename__ == "screener_results"
    assert Trade.__tablename__ == "trades"
    assert TradeEvent.__tablename__ == "trade_events"
    assert JournalEntry.__tablename__ == "journal_entries"


def test_market_data_candle_has_series_timestamp_unique_constraint() -> None:
    candle_table = Base.metadata.tables["market_data_candles"]

    constraints = {constraint.name for constraint in candle_table.constraints}

    assert "uq_candles_series_timestamp" in constraints


def test_market_data_series_has_source_freshness_metadata() -> None:
    series_table = Base.metadata.tables["market_data_series"]

    for column_name in (
        "provider_name",
        "provider_symbol",
        "provider_exchange",
        "provider_timeframe",
        "last_synced_at",
        "freshness_status",
        "sync_status",
        "sync_error_code",
        "sync_error_message",
    ):
        assert column_name in series_table.c


def test_market_data_freshness_and_sync_enums_support_safe_states() -> None:
    assert MarketDataFreshnessStatus.FRESH == "fresh"
    assert MarketDataFreshnessStatus.STALE == "stale"
    assert MarketDataFreshnessStatus.UNKNOWN == "unknown"
    assert MarketDataFreshnessStatus.FAILED == "failed"
    assert MarketDataFreshnessStatus.PARTIAL == "partial"
    assert MarketDataSyncStatus.NOT_APPLICABLE == "not_applicable"
    assert MarketDataSyncStatus.SUCCESS == "success"
    assert MarketDataSyncStatus.SKIPPED == "skipped"
    assert MarketDataSyncStatus.FAILED == "failed"
    assert MarketDataSyncStatus.PARTIAL == "partial"


def test_screener_enums_support_manual_review_states() -> None:
    assert ScreenerImportSource.TRADINGVIEW_SCREENER_CSV == "tradingview_screener_csv"
    assert ScreenerImportStatus.PENDING == "pending"
    assert ScreenerImportStatus.PARTIAL == "partial"
    assert ScreenerResultStatus.CANDIDATE == "candidate"
    assert ScreenerResultStatus.WATCHLIST_ADDED == "watchlist_added"
    assert ScreenerResultStatus.DUPLICATE == "duplicate"


def test_screener_models_do_not_contain_execution_fields() -> None:
    import_columns = set(Base.metadata.tables["screener_imports"].c.keys())
    result_columns = set(Base.metadata.tables["screener_results"].c.keys())

    forbidden_columns = {"order_id", "broker_order_id", "execution_id", "trade_id", "signal_id"}

    assert import_columns.isdisjoint(forbidden_columns)
    assert result_columns.isdisjoint(forbidden_columns)


def test_screener_result_has_import_symbol_exchange_unique_constraint() -> None:
    result_table = Base.metadata.tables["screener_results"]

    constraints = {constraint.name for constraint in result_table.constraints}

    assert "uq_screener_results_import_symbol_exchange" in constraints


def test_signal_reasoning_and_risk_flags_are_json_columns() -> None:
    signal_table = Base.metadata.tables["signals"]

    assert isinstance(signal_table.c.reasoning.type, JSON)
    assert isinstance(signal_table.c.risk_flags.type, JSON)
    assert isinstance(signal_table.c.no_trade_reasons.type, JSON)


def test_alert_payload_columns_are_json_columns() -> None:
    alert_table = Base.metadata.tables["alerts"]
    notification_table = Base.metadata.tables["notification_logs"]

    assert isinstance(alert_table.c.source_payload.type, JSON)
    assert isinstance(notification_table.c.provider_payload.type, JSON)


def test_alert_models_do_not_contain_execution_fields() -> None:
    alert_columns = set(Base.metadata.tables["alerts"].c.keys())
    notification_columns = set(Base.metadata.tables["notification_logs"].c.keys())

    forbidden_columns = {"order_id", "broker_order_id", "execution_id", "filled_quantity"}

    assert alert_columns.isdisjoint(forbidden_columns)
    assert notification_columns.isdisjoint(forbidden_columns)


def test_alert_read_schema_accepts_model_attributes() -> None:
    now = datetime(2026, 5, 16, tzinfo=UTC)
    alert = SimpleNamespace(
        id=1,
        user_id=1,
        signal_id=None,
        trade_id=None,
        watchlist_item_id=2,
        alert_type=AlertType.NEAR_TRIGGER,
        status=AlertStatus.ACTIVE,
        source=AlertSource.SYSTEM,
        priority="p2",
        trigger_level=Decimal("125.50"),
        timeframe=Timeframe.FOUR_HOURS,
        message="Review setup manually.",
        source_payload={"trigger": "near_trigger"},
        delivery_status=AlertDeliveryStatus.PENDING,
        delivery_error=None,
        last_triggered_at=None,
        created_at=now,
        updated_at=now,
    )

    result = AlertRead.model_validate(alert)

    assert result.alert_type == AlertType.NEAR_TRIGGER
    assert result.delivery_status == AlertDeliveryStatus.PENDING
    assert result.source_payload == {"trigger": "near_trigger"}


def test_notification_log_read_schema_accepts_model_attributes() -> None:
    now = datetime(2026, 5, 16, tzinfo=UTC)
    notification = SimpleNamespace(
        id=1,
        user_id=1,
        alert_id=3,
        channel=NotificationChannel.TELEGRAM,
        recipient="123456",
        message="Test notification",
        status=AlertDeliveryStatus.SENT,
        error_message=None,
        provider_payload={"message_id": 42},
        sent_at=now,
        created_at=now,
    )

    result = NotificationLogRead.model_validate(notification)

    assert result.channel == NotificationChannel.TELEGRAM
    assert result.status == AlertDeliveryStatus.SENT
    assert result.provider_payload == {"message_id": 42}


def test_screener_import_read_schema_accepts_model_attributes() -> None:
    now = datetime(2026, 5, 30, tzinfo=UTC)
    screener_import = SimpleNamespace(
        id=1,
        user_id=1,
        source=ScreenerImportSource.TRADINGVIEW_SCREENER_CSV,
        file_name="tradingview-screener.csv",
        asset_class="stock",
        screener_preset="US review candidates",
        snapshot_at=now,
        row_count=3,
        accepted_count=2,
        rejected_count=1,
        duplicate_count=0,
        status=ScreenerImportStatus.PARTIAL,
        validation_errors=[{"row": 3, "message": "Missing symbol."}],
        created_at=now,
    )

    result = ScreenerImportRead.model_validate(screener_import)

    assert result.source == ScreenerImportSource.TRADINGVIEW_SCREENER_CSV
    assert result.status == ScreenerImportStatus.PARTIAL
    assert result.accepted_count == 2


def test_screener_result_read_schema_accepts_model_attributes() -> None:
    now = datetime(2026, 5, 30, tzinfo=UTC)
    screener_result = SimpleNamespace(
        id=1,
        screener_import_id=2,
        user_id=1,
        watchlist_item_id=None,
        symbol="AAPL",
        name="Apple Inc.",
        asset_class="stock",
        exchange="NASDAQ",
        currency="USD",
        sector="Technology",
        industry="Consumer Electronics",
        price=Decimal("190.50"),
        change_percent=Decimal("1.25"),
        volume=Decimal("1000000"),
        relative_volume=Decimal("1.10"),
        market_cap=Decimal("2500000000000"),
        rsi14=Decimal("55.2"),
        ema20=Decimal("188.1"),
        ema50=Decimal("180.3"),
        ema200=Decimal("170.4"),
        rank=1,
        status=ScreenerResultStatus.CANDIDATE,
        duplicate_of_result_id=None,
        validation_errors=None,
        raw_metadata={"source_column": "value"},
        created_at=now,
        updated_at=now,
    )

    result = ScreenerResultRead.model_validate(screener_result)

    assert result.symbol == "AAPL"
    assert result.status == ScreenerResultStatus.CANDIDATE
    assert result.watchlist_item_id is None

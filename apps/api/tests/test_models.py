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
    Settings,
    Signal,
    Timeframe,
    Trade,
    TradeEvent,
    User,
    WatchlistItem,
)
from app.schemas.alerts import AlertRead, NotificationLogRead


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

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models import *  # noqa: F403
from app.models.alert import Alert, NotificationLog
from app.models.enums import AlertDeliveryStatus, AlertSource, AlertStatus, AlertType
from app.models.trade import Trade
from app.services.notifications import TelegramDeliveryError


@pytest.fixture()
def db_session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Iterator[TestClient]:
    def override_get_db() -> Iterator[Session]:
        yield db_session

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


def valid_payload(secret: str = "change-me") -> dict[str, object]:
    return {
        "secret": secret,
        "symbol": "AAPL",
        "exchange": "NASDAQ",
        "price": "125.50",
        "time": "2026-05-16T19:00:00Z",
        "timeframe": "4H",
        "trigger": "near_trigger",
        "setup_id": "setup-123",
    }


def test_tradingview_webhook_persists_valid_alert(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "telegram_alert_routing_enabled", False)

    response = client.post("/api/webhooks/tradingview", json=valid_payload())

    assert response.status_code == 202
    result = response.json()
    assert result["alert_id"] is not None
    assert result["status"] == "triggered"
    assert result["delivery_status"] == "skipped"

    alert = db_session.scalar(select(Alert).where(Alert.id == result["alert_id"]))
    assert alert is not None
    assert alert.alert_type == AlertType.NEAR_TRIGGER
    assert alert.status == AlertStatus.TRIGGERED
    assert alert.source == AlertSource.TRADINGVIEW_WEBHOOK
    assert alert.source_payload["symbol"] == "AAPL"
    assert "secret" not in alert.source_payload
    assert alert.delivery_status == AlertDeliveryStatus.SKIPPED
    assert alert.delivery_error == "Telegram alert routing is disabled."
    assert db_session.scalars(select(Trade)).all() == []
    assert db_session.scalars(select(NotificationLog)).all() == []


def test_tradingview_webhook_routes_allowed_alert_to_telegram(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "telegram_alert_routing_enabled", True)
    monkeypatch.setattr(settings, "telegram_bot_token", "test-token")
    monkeypatch.setattr(settings, "telegram_chat_id", "12345")
    messages: list[str] = []

    def fake_send(message: str) -> None:
        messages.append(message)

    monkeypatch.setattr("app.services.alerts.send_telegram_message", fake_send)

    response = client.post("/api/webhooks/tradingview", json=valid_payload())

    assert response.status_code == 202
    result = response.json()
    assert result["delivery_status"] == "sent"
    alert = db_session.scalar(select(Alert).where(Alert.id == result["alert_id"]))
    assert alert is not None
    assert alert.delivery_status == AlertDeliveryStatus.SENT
    assert alert.delivery_error is None
    notifications = db_session.scalars(select(NotificationLog)).all()
    assert len(notifications) == 1
    assert notifications[0].status == AlertDeliveryStatus.SENT
    assert notifications[0].recipient == "12345"
    assert notifications[0].provider_payload["dedup_key"] == "AAPL:near_trigger:4H"
    assert notifications[0].sent_at is not None
    assert messages == [notifications[0].message]
    assert "AAPL" in messages[0]
    assert "near_trigger" in messages[0]
    assert "Manual review required" in messages[0]
    assert "Keine automatische Order" in messages[0]
    assert "Keine Kauf- oder Verkaufsanweisung" in messages[0]
    assert "kaufen" not in messages[0].lower()
    assert "verkaufen" not in messages[0].lower()


@pytest.mark.parametrize(
    ("trigger", "expected_alert_type", "expected_priority"),
    [
        ("near_trigger", AlertType.NEAR_TRIGGER, "p2"),
        ("entry_trigger", AlertType.ENTRY_TRIGGER, "p1"),
        ("long_entry", AlertType.ENTRY_TRIGGER, "p1"),
        ("invalidation", AlertType.INVALIDATION, "p2"),
        ("exit_warning", AlertType.EXIT_WARNING, "p2"),
    ],
)
def test_tradingview_webhook_routes_all_policy_allowed_alert_types(
    trigger: str,
    expected_alert_type: AlertType,
    expected_priority: str,
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "telegram_alert_routing_enabled", True)
    monkeypatch.setattr(settings, "telegram_bot_token", "test-token")
    monkeypatch.setattr(settings, "telegram_chat_id", "12345")
    messages: list[str] = []

    def fake_send(message: str) -> None:
        messages.append(message)

    monkeypatch.setattr("app.services.alerts.send_telegram_message", fake_send)
    payload = valid_payload() | {"trigger": trigger}

    response = client.post("/api/webhooks/tradingview", json=payload)

    assert response.status_code == 202
    assert response.json()["delivery_status"] == "sent"
    alert = db_session.scalar(select(Alert).where(Alert.id == response.json()["alert_id"]))
    assert alert is not None
    assert alert.alert_type == expected_alert_type
    assert alert.priority == expected_priority
    notification = db_session.scalar(select(NotificationLog))
    assert notification is not None
    assert notification.status == AlertDeliveryStatus.SENT
    assert notification.provider_payload["dedup_key"] == (
        f"AAPL:{expected_alert_type.value}:4H"
    )
    assert messages == [notification.message]


def test_tradingview_webhook_skips_manual_only_alert_type(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "telegram_alert_routing_enabled", True)
    monkeypatch.setattr(settings, "telegram_bot_token", "test-token")
    monkeypatch.setattr(settings, "telegram_chat_id", "12345")
    sent_messages: list[str] = []

    def fake_send(message: str) -> None:
        sent_messages.append(message)

    monkeypatch.setattr("app.services.alerts.send_telegram_message", fake_send)
    payload = valid_payload()
    payload["trigger"] = "watchlist"

    response = client.post("/api/webhooks/tradingview", json=payload)

    assert response.status_code == 202
    result = response.json()
    assert result["delivery_status"] == "skipped"
    alert = db_session.scalar(select(Alert).where(Alert.id == result["alert_id"]))
    assert alert is not None
    assert alert.alert_type == AlertType.WATCHLIST
    assert alert.delivery_status == AlertDeliveryStatus.SKIPPED
    assert alert.delivery_error == "Alert type is manual-review only."
    assert sent_messages == []
    assert db_session.scalars(select(NotificationLog)).all() == []


@pytest.mark.parametrize(
    ("trigger", "expected_alert_type"),
    [
        ("info", AlertType.INFO),
        ("watchlist", AlertType.WATCHLIST),
        ("armed", AlertType.ARMED),
        ("management", AlertType.MANAGEMENT),
        ("exit_signal", AlertType.EXIT_SIGNAL),
    ],
)
def test_tradingview_webhook_skips_all_policy_manual_only_alert_types(
    trigger: str,
    expected_alert_type: AlertType,
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "telegram_alert_routing_enabled", True)
    monkeypatch.setattr(settings, "telegram_bot_token", "test-token")
    monkeypatch.setattr(settings, "telegram_chat_id", "12345")
    sent_messages: list[str] = []

    def fake_send(message: str) -> None:
        sent_messages.append(message)

    monkeypatch.setattr("app.services.alerts.send_telegram_message", fake_send)
    payload = valid_payload() | {"trigger": trigger}

    response = client.post("/api/webhooks/tradingview", json=payload)

    assert response.status_code == 202
    assert response.json()["delivery_status"] == "skipped"
    alert = db_session.scalar(select(Alert).where(Alert.id == response.json()["alert_id"]))
    assert alert is not None
    assert alert.alert_type == expected_alert_type
    assert alert.delivery_status == AlertDeliveryStatus.SKIPPED
    assert alert.delivery_error == "Alert type is manual-review only."
    assert sent_messages == []
    assert db_session.scalars(select(NotificationLog)).all() == []


def test_tradingview_webhook_records_delivery_failure_without_rejecting_webhook(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "telegram_alert_routing_enabled", True)
    monkeypatch.setattr(settings, "telegram_bot_token", "test-token")
    monkeypatch.setattr(settings, "telegram_chat_id", "12345")

    def fake_send(message: str) -> None:
        raise TelegramDeliveryError

    monkeypatch.setattr("app.services.alerts.send_telegram_message", fake_send)

    response = client.post("/api/webhooks/tradingview", json=valid_payload())

    assert response.status_code == 202
    result = response.json()
    assert result["delivery_status"] == "failed"
    alert = db_session.scalar(select(Alert).where(Alert.id == result["alert_id"]))
    assert alert is not None
    assert alert.delivery_status == AlertDeliveryStatus.FAILED
    assert alert.delivery_error == "TelegramDeliveryError"
    notifications = db_session.scalars(select(NotificationLog)).all()
    assert len(notifications) == 1
    assert notifications[0].status == AlertDeliveryStatus.FAILED
    assert notifications[0].error_message == "TelegramDeliveryError"


def test_tradingview_webhook_records_missing_telegram_config_without_rejecting_webhook(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "telegram_alert_routing_enabled", True)
    monkeypatch.setattr(settings, "telegram_bot_token", None)
    monkeypatch.setattr(settings, "telegram_chat_id", None)

    response = client.post("/api/webhooks/tradingview", json=valid_payload())

    assert response.status_code == 202
    result = response.json()
    assert result["delivery_status"] == "failed"
    alert = db_session.scalar(select(Alert).where(Alert.id == result["alert_id"]))
    assert alert is not None
    assert alert.delivery_status == AlertDeliveryStatus.FAILED
    assert alert.delivery_error == "TelegramConfigurationError"
    notifications = db_session.scalars(select(NotificationLog)).all()
    assert len(notifications) == 1
    assert notifications[0].status == AlertDeliveryStatus.FAILED
    assert notifications[0].error_message == "TelegramConfigurationError"


def test_tradingview_webhook_deduplicates_repeated_payload_within_window(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "telegram_alert_routing_enabled", True)
    monkeypatch.setattr(settings, "telegram_bot_token", "test-token")
    monkeypatch.setattr(settings, "telegram_chat_id", "12345")
    messages: list[str] = []

    def fake_send(message: str) -> None:
        messages.append(message)

    monkeypatch.setattr("app.services.alerts.send_telegram_message", fake_send)

    first_response = client.post("/api/webhooks/tradingview", json=valid_payload())
    duplicate_response = client.post("/api/webhooks/tradingview", json=valid_payload())

    assert first_response.status_code == 202
    assert duplicate_response.status_code == 202
    assert first_response.json()["delivery_status"] == "sent"
    assert duplicate_response.json()["delivery_status"] == "skipped"
    duplicate_alert = db_session.scalar(
        select(Alert).where(Alert.id == duplicate_response.json()["alert_id"])
    )
    assert duplicate_alert is not None
    assert duplicate_alert.delivery_status == AlertDeliveryStatus.SKIPPED
    assert duplicate_alert.delivery_error == "Telegram alert deduplicated within 30 minutes."
    assert len(messages) == 1
    assert len(db_session.scalars(select(Alert)).all()) == 2
    assert len(db_session.scalars(select(NotificationLog)).all()) == 1


def test_tradingview_webhook_allows_same_key_after_dedup_window(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "telegram_alert_routing_enabled", True)
    monkeypatch.setattr(settings, "telegram_bot_token", "test-token")
    monkeypatch.setattr(settings, "telegram_chat_id", "12345")
    messages: list[str] = []
    current_time = datetime.now(UTC)

    def fake_send(message: str) -> None:
        messages.append(message)

    monkeypatch.setattr("app.services.alerts.send_telegram_message", fake_send)
    monkeypatch.setattr("app.services.alerts.utc_now", lambda: current_time)

    first_response = client.post("/api/webhooks/tradingview", json=valid_payload())
    current_time = current_time + timedelta(minutes=31)
    second_response = client.post("/api/webhooks/tradingview", json=valid_payload())

    assert first_response.status_code == 202
    assert second_response.status_code == 202
    assert first_response.json()["delivery_status"] == "sent"
    assert second_response.json()["delivery_status"] == "sent"
    assert len(messages) == 2
    assert len(db_session.scalars(select(NotificationLog)).all()) == 2


def test_tradingview_webhook_dedup_key_separates_symbol_timeframe_and_alert_type(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "telegram_alert_routing_enabled", True)
    monkeypatch.setattr(settings, "telegram_bot_token", "test-token")
    monkeypatch.setattr(settings, "telegram_chat_id", "12345")
    messages: list[str] = []

    def fake_send(message: str) -> None:
        messages.append(message)

    monkeypatch.setattr("app.services.alerts.send_telegram_message", fake_send)
    payloads = [
        valid_payload(),
        valid_payload() | {"symbol": "MSFT"},
        valid_payload() | {"timeframe": "1D"},
        valid_payload() | {"trigger": "invalidation"},
    ]

    responses = [client.post("/api/webhooks/tradingview", json=payload) for payload in payloads]

    assert [response.status_code for response in responses] == [202, 202, 202, 202]
    assert [response.json()["delivery_status"] for response in responses] == [
        "sent",
        "sent",
        "sent",
        "sent",
    ]
    assert len(messages) == 4
    dedup_keys = {
        log.provider_payload["dedup_key"]
        for log in db_session.scalars(select(NotificationLog)).all()
    }
    assert dedup_keys == {
        "AAPL:near_trigger:4H",
        "MSFT:near_trigger:4H",
        "AAPL:near_trigger:1D",
        "AAPL:invalidation:4H",
    }


def test_tradingview_webhook_rate_limits_burst_events(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "telegram_alert_routing_enabled", True)
    monkeypatch.setattr(settings, "telegram_bot_token", "test-token")
    monkeypatch.setattr(settings, "telegram_chat_id", "12345")
    messages: list[str] = []

    def fake_send(message: str) -> None:
        messages.append(message)

    monkeypatch.setattr("app.services.alerts.send_telegram_message", fake_send)

    responses = []
    for index in range(11):
        payload = valid_payload() | {"symbol": f"SYM{index}"}
        responses.append(client.post("/api/webhooks/tradingview", json=payload))

    assert [response.status_code for response in responses] == [202] * 11
    assert [response.json()["delivery_status"] for response in responses[:10]] == ["sent"] * 10
    assert responses[10].json()["delivery_status"] == "skipped"
    rate_limited_alert = db_session.scalar(
        select(Alert).where(Alert.id == responses[10].json()["alert_id"])
    )
    assert rate_limited_alert is not None
    assert rate_limited_alert.delivery_error == "Telegram alert rate limit reached."
    assert len(messages) == 10
    assert len(db_session.scalars(select(NotificationLog)).all()) == 10


def test_tradingview_webhook_rejects_invalid_secret(
    client: TestClient, db_session: Session
) -> None:
    response = client.post("/api/webhooks/tradingview", json=valid_payload(secret="wrong"))

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid webhook secret."
    assert db_session.scalars(select(Alert)).all() == []


def test_tradingview_webhook_rejects_missing_required_payload_fields(
    client: TestClient, db_session: Session
) -> None:
    payload = valid_payload()
    del payload["symbol"]

    response = client.post("/api/webhooks/tradingview", json=payload)

    assert response.status_code == 422
    assert db_session.scalars(select(Alert)).all() == []


def test_tradingview_webhook_rejects_unsupported_trigger(
    client: TestClient, db_session: Session
) -> None:
    payload = valid_payload()
    payload["trigger"] = "broker_order"

    response = client.post("/api/webhooks/tradingview", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"] == "Unsupported TradingView trigger."
    assert db_session.scalars(select(Alert)).all() == []

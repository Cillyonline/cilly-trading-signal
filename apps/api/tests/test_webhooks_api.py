from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models import *  # noqa: F403
from app.core.config import settings
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
    assert notifications[0].sent_at is not None
    assert messages == [notifications[0].message]
    assert "AAPL" in messages[0]
    assert "near_trigger" in messages[0]
    assert "Manual review required" in messages[0]
    assert "Keine automatische Order" in messages[0]
    assert "Keine Kauf- oder Verkaufsanweisung" in messages[0]
    assert "kaufen" not in messages[0].lower()
    assert "verkaufen" not in messages[0].lower()


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

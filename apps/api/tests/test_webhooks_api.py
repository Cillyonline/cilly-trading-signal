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
from app.models.alert import Alert
from app.models.enums import AlertSource, AlertStatus, AlertType
from app.models.trade import Trade


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
    client: TestClient, db_session: Session
) -> None:
    response = client.post("/api/webhooks/tradingview", json=valid_payload())

    assert response.status_code == 202
    result = response.json()
    assert result["alert_id"] is not None
    assert result["status"] == "triggered"
    assert result["delivery_status"] == "pending"

    alert = db_session.scalar(select(Alert).where(Alert.id == result["alert_id"]))
    assert alert is not None
    assert alert.alert_type == AlertType.NEAR_TRIGGER
    assert alert.status == AlertStatus.TRIGGERED
    assert alert.source == AlertSource.TRADINGVIEW_WEBHOOK
    assert alert.source_payload["symbol"] == "AAPL"
    assert "secret" not in alert.source_payload
    assert db_session.scalars(select(Trade)).all() == []


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

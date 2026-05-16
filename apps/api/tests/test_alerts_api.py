from collections.abc import Iterator
from typing import Any

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
from app.models.alert import Alert


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


def login(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "change-this-password"},
    )
    assert response.status_code == 200


def test_telegram_test_endpoint_requires_authentication(client: TestClient) -> None:
    response = client.post("/api/alerts/test-telegram")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required."


def test_telegram_test_endpoint_requires_configuration(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    login(client)
    monkeypatch.setattr(settings, "telegram_bot_token", None)
    monkeypatch.setattr(settings, "telegram_chat_id", None)

    response = client.post("/api/alerts/test-telegram")

    assert response.status_code == 503
    assert response.json()["detail"] == "Telegram is not configured."


def test_telegram_test_endpoint_sends_explicit_test_message(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    login(client)
    monkeypatch.setattr(settings, "telegram_bot_token", "test-token")
    monkeypatch.setattr(settings, "telegram_chat_id", "12345")
    calls: list[tuple[str, dict[str, object]]] = []

    def fake_post(url: str, payload: dict[str, object]) -> dict[str, Any]:
        calls.append((url, payload))
        return {"ok": True, "result": {"message_id": 1}}

    monkeypatch.setattr("app.services.notifications._post_telegram_json", fake_post)

    response = client.post("/api/alerts/test-telegram")

    assert response.status_code == 200
    assert response.json() == {
        "status": "sent",
        "message": "Telegram test message sent.",
    }
    assert calls == [
        (
            "https://api.telegram.org/bottest-token/sendMessage",
            {
                "chat_id": "12345",
                "text": "Cilly Trading Signal Telegram test message.",
                "disable_web_page_preview": True,
            },
        )
    ]
    assert db_session.scalars(select(Alert)).all() == []


def test_telegram_test_endpoint_reports_delivery_failure(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    login(client)
    monkeypatch.setattr(settings, "telegram_bot_token", "test-token")
    monkeypatch.setattr(settings, "telegram_chat_id", "12345")

    def fake_post(url: str, payload: dict[str, object]) -> dict[str, Any]:
        return {"ok": False, "description": "chat not found"}

    monkeypatch.setattr("app.services.notifications._post_telegram_json", fake_post)

    response = client.post("/api/alerts/test-telegram")

    assert response.status_code == 502
    assert response.json()["detail"] == "Telegram test message could not be delivered."

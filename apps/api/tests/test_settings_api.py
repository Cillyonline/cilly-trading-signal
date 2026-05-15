from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models import *  # noqa: F403


@pytest.fixture()
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Iterator[Session]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app)
    login(test_client)

    yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def login(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "change-this-password"},
    )
    assert response.status_code == 200


def test_get_settings_creates_defaults(client: TestClient) -> None:
    response = client.get("/api/settings")

    assert response.status_code == 200
    assert response.json() == {
        "account_size": None,
        "default_risk_percent": "1.00",
        "max_risk_percent": "1.00",
        "min_risk_reward": "2.00",
        "max_open_trades": 5,
        "base_currency": "EUR",
    }


def test_patch_settings_updates_risk_fields(client: TestClient) -> None:
    response = client.patch(
        "/api/settings",
        json={
            "account_size": "25000.00",
            "default_risk_percent": "0.75",
            "max_risk_percent": "1.25",
            "min_risk_reward": "2.50",
            "max_open_trades": 3,
            "base_currency": "usd",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["account_size"] == "25000.00"
    assert body["default_risk_percent"] == "0.75"
    assert body["max_risk_percent"] == "1.25"
    assert body["min_risk_reward"] == "2.50"
    assert body["max_open_trades"] == 3
    assert body["base_currency"] == "USD"


def test_patch_settings_rejects_invalid_values(client: TestClient) -> None:
    response = client.patch("/api/settings", json={"max_open_trades": 0})

    assert response.status_code == 422


def test_patch_settings_allows_clearing_account_size_only(client: TestClient) -> None:
    set_response = client.patch("/api/settings", json={"account_size": "10000.00"})
    clear_response = client.patch(
        "/api/settings",
        json={"account_size": None, "max_open_trades": None},
    )

    assert set_response.status_code == 200
    assert clear_response.status_code == 200
    assert clear_response.json()["account_size"] is None
    assert clear_response.json()["max_open_trades"] == 5

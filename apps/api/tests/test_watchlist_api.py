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

    yield TestClient(app)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_create_and_list_watchlist_items(client: TestClient) -> None:
    response = client.post(
        "/api/watchlist",
        json={
            "symbol": " aapl ",
            "name": "Apple",
            "asset_class": "stock",
            "exchange": "nasdaq",
            "currency": "usd",
            "notes": "Mega cap",
        },
    )

    assert response.status_code == 201
    created = response.json()
    assert created["symbol"] == "AAPL"
    assert created["exchange"] == "NASDAQ"
    assert created["currency"] == "USD"
    assert created["is_active"] is True

    list_response = client.get("/api/watchlist")

    assert list_response.status_code == 200
    assert [item["symbol"] for item in list_response.json()] == ["AAPL"]


def test_create_watchlist_item_rejects_duplicate_symbol(client: TestClient) -> None:
    payload = {"symbol": "BTCUSDT", "asset_class": "crypto"}

    first_response = client.post("/api/watchlist", json=payload)
    duplicate_response = client.post("/api/watchlist", json=payload)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409


def test_update_and_deactivate_watchlist_item(client: TestClient) -> None:
    created = client.post(
        "/api/watchlist", json={"symbol": "MSFT", "asset_class": "stock"}
    ).json()

    update_response = client.patch(
        f"/api/watchlist/{created['id']}",
        json={"notes": "Updated note", "is_active": True},
    )

    assert update_response.status_code == 200
    assert update_response.json()["notes"] == "Updated note"

    delete_response = client.delete(f"/api/watchlist/{created['id']}")

    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False


def test_get_unknown_watchlist_item_returns_404(client: TestClient) -> None:
    response = client.get("/api/watchlist/999")

    assert response.status_code == 404

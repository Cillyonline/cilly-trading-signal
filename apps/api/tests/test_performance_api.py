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


def test_performance_summary_returns_empty_state(client: TestClient) -> None:
    response = client.get("/api/performance/summary")

    assert response.status_code == 200
    assert response.json() == {
        "closed_trade_count": 0,
        "total_r": "0.0000",
        "average_r": None,
        "win_rate": None,
        "best_r": None,
        "worst_r": None,
    }


def test_performance_summary_uses_closed_trades_only(client: TestClient) -> None:
    create_open_trade(client, "AAPL")
    close_trade(client, create_open_trade(client, "MSFT"), "115.00")

    response = client.get("/api/performance/summary")

    assert response.status_code == 200
    summary = response.json()
    assert summary["closed_trade_count"] == 1
    assert summary["total_r"] == "3.0000"
    assert summary["average_r"] == "3.0000"


def test_performance_summary_calculates_winners_and_losers(client: TestClient) -> None:
    close_trade(client, create_open_trade(client, "AAPL"), "115.00")
    close_trade(client, create_open_trade(client, "MSFT"), "90.00")

    response = client.get("/api/performance/summary")

    assert response.status_code == 200
    summary = response.json()
    assert summary["closed_trade_count"] == 2
    assert summary["total_r"] == "1.0000"
    assert summary["average_r"] == "0.5000"
    assert summary["win_rate"] == "50.00"
    assert summary["best_r"] == "3.0000"
    assert summary["worst_r"] == "-2.0000"


def test_performance_summary_calculates_average_r(client: TestClient) -> None:
    close_trade(client, create_open_trade(client, "AAPL"), "110.00")
    close_trade(client, create_open_trade(client, "MSFT"), "105.00")
    close_trade(client, create_open_trade(client, "NVDA"), "95.00")

    response = client.get("/api/performance/summary")

    assert response.status_code == 200
    summary = response.json()
    assert summary["total_r"] == "2.0000"
    assert summary["average_r"] == "0.6667"


def create_watchlist_item(client: TestClient, symbol: str) -> int:
    response = client.post(
        "/api/watchlist",
        json={"symbol": symbol, "asset_class": "stock", "exchange": "NASDAQ"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_open_trade(client: TestClient, symbol: str) -> dict:
    watchlist_item_id = create_watchlist_item(client, symbol)
    response = client.post(
        "/api/trades",
        json={
            "watchlist_item_id": watchlist_item_id,
            "strategy_type": "trend_pullback_long",
            "entry_price": "100.00",
            "stop_loss": "95.00",
            "target_1": "112.50",
            "target_2": "120.00",
            "position_size": "10",
            "opened_at": "2024-01-05T10:00:00Z",
        },
    )
    assert response.status_code == 201
    return response.json()


def close_trade(client: TestClient, trade: dict, exit_price: str) -> dict:
    response = client.post(
        f"/api/trades/{trade['id']}/close",
        json={
            "exit_price": exit_price,
            "exit_reason": "manual_exit",
            "closed_at": "2024-01-07T10:00:00Z",
        },
    )
    assert response.status_code == 200
    return response.json()

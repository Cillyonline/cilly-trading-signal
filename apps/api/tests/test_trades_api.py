from collections.abc import Iterator
from datetime import date, timedelta

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


def create_watchlist_item(client: TestClient) -> int:
    response = client.post(
        "/api/watchlist",
        json={"symbol": "AAPL", "asset_class": "stock", "exchange": "NASDAQ"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_trade_from_watchlist_calculates_initial_risk(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)

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
            "fees": "1.50",
            "opened_at": "2024-01-05T10:00:00Z",
            "notes": "Manual paper trade log.",
        },
    )

    assert response.status_code == 201
    trade = response.json()
    assert trade["status"] == "open"
    assert trade["symbol"] == "AAPL"
    assert trade["asset_class"] == "stock"
    assert trade["entry_price"] == "100.00000000"
    assert trade["stop_loss"] == "95.00000000"
    assert trade["risk_per_unit"] == "5.00000000"
    assert trade["initial_risk_amount"] == "50.00"
    assert trade["initial_risk_reward"] == "2.50"
    assert trade["target_1_potential_r"] == "2.50"
    assert trade["target_2_potential_r"] == "4.00"
    assert trade["result_r"] is None

    list_response = client.get("/api/trades")

    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == trade["id"]


def test_list_trades_returns_empty_list(client: TestClient) -> None:
    response = client.get("/api/trades")

    assert response.status_code == 200
    assert response.json() == []


def test_create_trade_rejects_invalid_long_risk(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)

    response = client.post(
        "/api/trades",
        json={
            "watchlist_item_id": watchlist_item_id,
            "strategy_type": "trend_pullback_long",
            "entry_price": "95.00",
            "stop_loss": "100.00",
            "position_size": "10",
            "opened_at": "2024-01-05T10:00:00Z",
        },
    )

    assert response.status_code == 422


def test_create_trade_requires_strategy_without_signal(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)

    response = client.post(
        "/api/trades",
        json={
            "watchlist_item_id": watchlist_item_id,
            "entry_price": "100.00",
            "stop_loss": "95.00",
            "position_size": "10",
            "opened_at": "2024-01-05T10:00:00Z",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "strategy_type is required when no signal_id is provided."


def test_create_trade_from_signal_uses_signal_context(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)
    import_response = client.post(
        "/api/imports/csv",
        data={"watchlist_item_id": str(watchlist_item_id), "timeframe": "1D"},
        files={"file": ("data.csv", sequential_csv(), "text/csv")},
    )
    assert import_response.status_code == 200
    analyze_response = client.post(f"/api/imports/{import_response.json()['series_id']}/analyze")
    assert analyze_response.status_code == 200
    signal = client.get("/api/signals").json()[0]

    response = client.post(
        "/api/trades",
        json={
            "signal_id": signal["id"],
            "entry_price": "200.00",
            "stop_loss": "190.00",
            "target_1": "230.00",
            "position_size": "3",
            "opened_at": "2024-01-05T10:00:00Z",
        },
    )

    assert response.status_code == 201
    trade = response.json()
    assert trade["signal_id"] == signal["id"]
    assert trade["watchlist_item_id"] == watchlist_item_id
    assert trade["strategy_type"] == signal["strategy_type"]
    assert trade["initial_risk_amount"] == "30.00"
    assert trade["initial_risk_reward"] == "3.00"


def sequential_csv(row_count: int = 201) -> str:
    rows = ["time,open,high,low,close,volume"]
    start = date(2024, 1, 1)
    for index in range(row_count):
        current_date = start + timedelta(days=index)
        close = 100 + index
        rows.append(f"{current_date.isoformat()},{close - 1},{close + 2},{close - 2},{close},1000")
    return "\n".join(rows)

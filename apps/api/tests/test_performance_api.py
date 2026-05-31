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
        "by_strategy": [],
        "by_asset_class": [],
        "open_portfolio_risk": {
            "open_trade_count": 0,
            "complete_risk_count": 0,
            "incomplete_risk_count": 0,
            "documented_initial_risk_amount": "0.00",
            "documented_initial_risk_percent": "0.0000",
            "max_risk_percent": "1.00",
            "warning_status": "ok",
            "warnings": [],
            "by_strategy": [],
            "by_asset_class": [],
            "review_only_notice": (
                "Open portfolio risk is based only on manually documented trades. It is "
                "review-only, not broker/account sync, automatic position sizing, an order "
                "recommendation, or trading advice."
            ),
        },
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
    assert summary["by_strategy"] == [
        {
            "strategy_type": "trend_pullback_long",
            "closed_trade_count": 1,
            "total_r": "3.0000",
            "average_r": "3.0000",
            "win_rate": "100.00",
        }
    ]
    assert summary["by_asset_class"] == [
        {
            "asset_class": "stock",
            "closed_trade_count": 1,
            "total_r": "3.0000",
            "average_r": "3.0000",
            "win_rate": "100.00",
        }
    ]


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


def test_performance_summary_groups_closed_trades_by_strategy(client: TestClient) -> None:
    close_trade(
        client,
        create_open_trade(client, "AAPL", strategy_type="trend_pullback_long"),
        "115.00",
    )
    close_trade(
        client,
        create_open_trade(client, "MSFT", strategy_type="trend_pullback_long"),
        "90.00",
    )
    close_trade(
        client,
        create_open_trade(client, "NVDA", strategy_type="base_breakout_long"),
        "110.00",
    )

    response = client.get("/api/performance/summary")

    assert response.status_code == 200
    assert response.json()["by_strategy"] == [
        {
            "strategy_type": "base_breakout_long",
            "closed_trade_count": 1,
            "total_r": "2.0000",
            "average_r": "2.0000",
            "win_rate": "100.00",
        },
        {
            "strategy_type": "trend_pullback_long",
            "closed_trade_count": 2,
            "total_r": "1.0000",
            "average_r": "0.5000",
            "win_rate": "50.00",
        },
    ]


def test_performance_summary_groups_closed_trades_by_asset_class(client: TestClient) -> None:
    close_trade(
        client,
        create_open_trade(client, "AAPL", asset_class="stock"),
        "115.00",
    )
    close_trade(
        client,
        create_open_trade(client, "MSFT", asset_class="stock"),
        "90.00",
    )
    close_trade(
        client,
        create_open_trade(client, "BTCUSD", asset_class="crypto"),
        "110.00",
    )

    response = client.get("/api/performance/summary")

    assert response.status_code == 200
    assert response.json()["by_asset_class"] == [
        {
            "asset_class": "crypto",
            "closed_trade_count": 1,
            "total_r": "2.0000",
            "average_r": "2.0000",
            "win_rate": "100.00",
        },
        {
            "asset_class": "stock",
            "closed_trade_count": 2,
            "total_r": "1.0000",
            "average_r": "0.5000",
            "win_rate": "50.00",
        },
    ]


def test_performance_summary_includes_open_portfolio_risk(client: TestClient) -> None:
    incomplete = create_open_trade(client, "MSFT", strategy_type="trend_pullback_long")
    update_account_size(client, "5000.00")
    create_open_trade(client, "AAPL", strategy_type="trend_pullback_long", asset_class="stock")
    create_open_trade(client, "BTCUSD", strategy_type="base_breakout_long", asset_class="crypto")
    close_trade(client, create_open_trade(client, "NVDA"), "110.00")

    response = client.get("/api/performance/summary")

    assert response.status_code == 200
    risk = response.json()["open_portfolio_risk"]
    assert risk["open_trade_count"] == 3
    assert risk["complete_risk_count"] == 2
    assert risk["incomplete_risk_count"] == 1
    assert risk["documented_initial_risk_amount"] == "100.00"
    assert risk["documented_initial_risk_percent"] == "2.0000"
    assert risk["max_risk_percent"] == "1.00"
    assert risk["warning_status"] == "warning"
    assert risk["warnings"] == [
        "Documented open risk percent exceeds the configured max risk percent.",
        "Some open trades are missing complete documented risk data.",
    ]
    assert "trading advice" in risk["review_only_notice"]
    assert risk["by_strategy"] == [
        {
            "group": "base_breakout_long",
            "open_trade_count": 1,
            "documented_initial_risk_amount": "50.00",
            "documented_initial_risk_percent": "1.0000",
            "incomplete_risk_count": 0,
        },
        {
            "group": "trend_pullback_long",
            "open_trade_count": 2,
            "documented_initial_risk_amount": "50.00",
            "documented_initial_risk_percent": "1.0000",
            "incomplete_risk_count": 1,
        },
    ]
    assert risk["by_asset_class"] == [
        {
            "group": "crypto",
            "open_trade_count": 1,
            "documented_initial_risk_amount": "50.00",
            "documented_initial_risk_percent": "1.0000",
            "incomplete_risk_count": 0,
        },
        {
            "group": "stock",
            "open_trade_count": 2,
            "documented_initial_risk_amount": "50.00",
            "documented_initial_risk_percent": "1.0000",
            "incomplete_risk_count": 1,
        },
    ]
    assert incomplete["status"] == "open"


def test_performance_summary_marks_missing_open_risk_as_unknown(client: TestClient) -> None:
    create_open_trade(client, "MSFT", strategy_type="trend_pullback_long")

    response = client.get("/api/performance/summary")

    assert response.status_code == 200
    risk = response.json()["open_portfolio_risk"]
    assert risk["open_trade_count"] == 1
    assert risk["complete_risk_count"] == 0
    assert risk["incomplete_risk_count"] == 1
    assert risk["documented_initial_risk_percent"] == "0.0000"
    assert risk["warning_status"] == "unknown"
    assert risk["warnings"] == ["Some open trades are missing complete documented risk data."]


def test_performance_summary_keeps_open_risk_ok_below_threshold(client: TestClient) -> None:
    update_account_size(client, "10000.00")
    create_open_trade(client, "AAPL", strategy_type="trend_pullback_long", asset_class="stock")

    response = client.get("/api/performance/summary")

    assert response.status_code == 200
    risk = response.json()["open_portfolio_risk"]
    assert risk["documented_initial_risk_percent"] == "0.5000"
    assert risk["max_risk_percent"] == "1.00"
    assert risk["warning_status"] == "ok"
    assert risk["warnings"] == []


def create_watchlist_item(client: TestClient, symbol: str, asset_class: str = "stock") -> int:
    response = client.post(
        "/api/watchlist",
        json={"symbol": symbol, "asset_class": asset_class, "exchange": "NASDAQ"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_open_trade(
    client: TestClient,
    symbol: str,
    strategy_type: str = "trend_pullback_long",
    asset_class: str = "stock",
    position_size: str = "10",
) -> dict:
    watchlist_item_id = create_watchlist_item(client, symbol, asset_class)
    response = client.post(
        "/api/trades",
        json={
            "watchlist_item_id": watchlist_item_id,
            "strategy_type": strategy_type,
            "entry_price": "100.00",
            "stop_loss": "95.00",
            "target_1": "112.50",
            "target_2": "120.00",
            "position_size": position_size,
            "opened_at": "2024-01-05T10:00:00Z",
        },
    )
    assert response.status_code == 201
    return response.json()


def update_account_size(client: TestClient, account_size: str) -> dict:
    response = client.patch("/api/settings", json={"account_size": account_size})
    assert response.status_code == 200
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

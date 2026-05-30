from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

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
    listed = list_response.json()
    assert [item["symbol"] for item in listed] == ["AAPL"]
    assert listed[0]["latest_market_data"] is None


def test_list_watchlist_items_includes_latest_market_data(client: TestClient) -> None:
    created = client.post("/api/watchlist", json={"symbol": "AAPL", "asset_class": "stock"}).json()

    import_response = client.post(
        "/api/imports/csv",
        data={"watchlist_item_id": str(created["id"]), "timeframe": "1D"},
        files={
            "file": (
                "recent.csv",
                recent_daily_csv(),
                "text/csv",
            )
        },
    )
    assert import_response.status_code == 200

    response = client.get("/api/watchlist")

    assert response.status_code == 200
    item = response.json()[0]
    summary = item["latest_market_data"]
    assert summary["series_id"] == import_response.json()["series_id"]
    assert summary["source"] == "tradingview_csv"
    assert summary["freshness_status"] == "fresh"
    assert summary["sync_status"] == "not_applicable"
    assert summary["timeframe"] == "1D"
    assert summary["end_time"] is not None
    assert summary["provider_name"] is None


def test_benchmark_context_reports_missing_required_symbols(client: TestClient) -> None:
    response = client.get("/api/watchlist/benchmark-context")

    assert response.status_code == 200
    contexts = response.json()
    stock_context = next(context for context in contexts if context["asset_class"] == "stock")
    crypto_context = next(context for context in contexts if context["asset_class"] == "crypto")
    assert [requirement["status"] for requirement in stock_context["requirements"]] == [
        "missing_symbol",
        "missing_symbol",
    ]
    assert {requirement["key"] for requirement in crypto_context["requirements"]} == {"BTC", "ETH"}
    assert "no live data" in stock_context["guidance"].lower()


def test_benchmark_context_reports_daily_data_readiness(client: TestClient) -> None:
    spy = client.post("/api/watchlist", json={"symbol": "SPY", "asset_class": "stock"}).json()
    client.post("/api/watchlist", json={"symbol": "QQQ", "asset_class": "stock"})
    import_response = client.post(
        "/api/imports/csv",
        data={"watchlist_item_id": str(spy["id"]), "timeframe": "1D"},
        files={"file": ("spy.csv", recent_daily_csv(), "text/csv")},
    )
    assert import_response.status_code == 200

    response = client.get("/api/watchlist/benchmark-context")

    assert response.status_code == 200
    stock_context = next(
        context for context in response.json() if context["asset_class"] == "stock"
    )
    spy_requirement = next(
        requirement for requirement in stock_context["requirements"] if requirement["key"] == "SPY"
    )
    qqq_requirement = next(
        requirement for requirement in stock_context["requirements"] if requirement["key"] == "QQQ"
    )
    assert spy_requirement["status"] == "ready"
    assert spy_requirement["present_symbol"] == "SPY"
    assert spy_requirement["latest_daily_freshness"] == "fresh"
    assert qqq_requirement["status"] == "missing_daily_data"
    assert qqq_requirement["present_symbol"] == "QQQ"


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


def recent_daily_csv() -> str:
    rows = ["time,open,high,low,close,volume"]
    start = (datetime.now(UTC) - timedelta(days=19)).date()
    for index in range(20):
        current_date = start + timedelta(days=index)
        rows.append(f"{current_date.isoformat()},100,110,90,105,1000")
    return "\n".join(rows)

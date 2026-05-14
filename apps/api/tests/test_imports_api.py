from collections.abc import Iterator
from datetime import date, timedelta
from decimal import Decimal

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


def valid_csv(row_count: int = 20) -> str:
    rows = ["time,open,high,low,close,volume"]
    for day in range(1, row_count + 1):
        rows.append(f"2024-01-{day:02d},100,110,90,105,1000")
    return "\n".join(rows)


def sequential_csv(row_count: int = 201) -> str:
    rows = ["time,open,high,low,close,volume"]
    start = date(2024, 1, 1)
    for index in range(row_count):
        current_date = start + timedelta(days=index)
        close = Decimal("100") + Decimal(index)
        rows.append(f"{current_date.isoformat()},{close - 1},{close + 2},{close - 2},{close},1000")
    return "\n".join(rows)


def create_watchlist_item(client: TestClient) -> int:
    response = client.post("/api/watchlist", json={"symbol": "AAPL", "asset_class": "stock"})
    assert response.status_code == 201
    return response.json()["id"]


def post_csv_import(
    client: TestClient,
    watchlist_item_id: int,
    csv_content: str,
    file_name: str = "tradingview.csv",
) -> object:
    return client.post(
        "/api/imports/csv",
        data={"watchlist_item_id": str(watchlist_item_id), "timeframe": "1D"},
        files={"file": (file_name, csv_content, "text/csv")},
    )


def test_import_csv_persists_valid_candles(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)

    response = post_csv_import(client, watchlist_item_id, valid_csv())

    assert response.status_code == 200
    result = response.json()
    assert result["series_id"] is not None
    assert result["watchlist_item_id"] == watchlist_item_id
    assert result["timeframe"] == "1D"
    assert result["status"] == "validated"
    assert result["candle_count"] == 20
    assert result["start_time"].startswith("2024-01-01")
    assert result["end_time"].startswith("2024-01-20")
    assert result["errors"] == []


def test_import_csv_rejects_missing_required_column(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)
    csv_content = "time,open,high,low,close\n2024-01-01,100,110,90,105"

    response = post_csv_import(client, watchlist_item_id, csv_content)

    assert response.status_code == 422
    assert {error["field"] for error in response.json()["detail"]} >= {"volume"}


def test_import_csv_rejects_invalid_numeric_value(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)
    rows = [
        "time,open,high,low,close,volume",
        "2024-01-01,not-a-number,110,90,105,1000",
    ]
    rows.extend(f"2024-01-{day:02d},100,110,90,105,1000" for day in range(2, 21))

    response = post_csv_import(client, watchlist_item_id, "\n".join(rows))

    assert response.status_code == 422
    assert {
        (error["row"], error["field"], error["message"])
        for error in response.json()["detail"]
    } >= {(2, "open", "Invalid number.")}


def test_import_csv_rejects_missing_row_value(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)
    rows = ["time,open,high,low,close,volume", "2024-01-01,100,110,90,105"]
    rows.extend(f"2024-01-{day:02d},100,110,90,105,1000" for day in range(2, 21))

    response = post_csv_import(client, watchlist_item_id, "\n".join(rows))

    assert response.status_code == 422
    assert {
        (error["row"], error["field"], error["message"])
        for error in response.json()["detail"]
    } >= {(2, "volume", "Value is required.")}


def test_import_csv_accepts_mixed_timestamp_formats(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)
    rows = [
        "time,open,high,low,close,volume",
        "2024-01-01T00:00:00Z,100,110,90,105,1000",
    ]
    rows.extend(f"2024-01-{day:02d},100,110,90,105,1000" for day in range(2, 21))

    response = post_csv_import(client, watchlist_item_id, "\n".join(rows))

    assert response.status_code == 200
    assert response.json()["candle_count"] == 20


def test_import_csv_rejects_insufficient_valid_candles(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)

    response = post_csv_import(client, watchlist_item_id, valid_csv(row_count=19))

    assert response.status_code == 422
    assert any(
        error["message"] == "CSV must contain at least 20 valid candles."
        for error in response.json()["detail"]
    )


def test_import_csv_rejects_duplicate_timestamp(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)
    rows = ["time,open,high,low,close,volume"]
    rows.extend(f"2024-01-{day:02d},100,110,90,105,1000" for day in range(1, 21))
    rows.append("2024-01-20,100,110,90,105,1000")

    response = post_csv_import(client, watchlist_item_id, "\n".join(rows))

    assert response.status_code == 422
    assert any(
        error["field"] == "time" and error["message"] == "Duplicate timestamp in CSV."
        for error in response.json()["detail"]
    )


def test_import_csv_returns_404_for_unknown_watchlist_item(client: TestClient) -> None:
    response = post_csv_import(client, 999, valid_csv())

    assert response.status_code == 404
    assert response.json()["detail"] == "Watchlist item not found."


def test_analyze_import_creates_indicator_snapshots(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)
    imported = post_csv_import(client, watchlist_item_id, sequential_csv()).json()

    response = client.post(f"/api/imports/{imported['series_id']}/analyze")

    assert response.status_code == 200
    result = response.json()
    assert result["series_id"] == imported["series_id"]
    assert result["status"] == "analyzed"
    assert result["candle_count"] == 201
    assert result["indicator_snapshot_count"] == 201
    assert result["signal"]["strategy_type"] == "trend_pullback_long"
    assert result["signal"]["status"] in {"watchlist", "armed", "no_setup"}
    assert result["signal"]["reasoning"]
    assert "trade" not in result["signal"]

    signals_response = client.get("/api/signals")

    assert signals_response.status_code == 200
    signals = signals_response.json()
    assert len(signals) == 1
    assert signals[0]["watchlist_item_id"] == watchlist_item_id
    assert signals[0]["symbol"] == "AAPL"
    assert signals[0]["asset_class"] == "stock"
    assert signals[0]["strategy_type"] == result["signal"]["strategy_type"]
    assert signals[0]["reasoning"]

    detail_response = client.get(f"/api/signals/{signals[0]['id']}")

    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == signals[0]["id"]
    assert detail_response.json()["symbol"] == "AAPL"


def test_analyze_import_replaces_existing_strategy_signal(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)
    imported = post_csv_import(client, watchlist_item_id, sequential_csv()).json()

    first_response = client.post(f"/api/imports/{imported['series_id']}/analyze")
    second_response = client.post(f"/api/imports/{imported['series_id']}/analyze")
    signals_response = client.get("/api/signals")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert signals_response.status_code == 200
    assert len(signals_response.json()) == 1


def test_analyze_import_returns_no_setup_for_insufficient_history(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)
    imported = post_csv_import(client, watchlist_item_id, valid_csv()).json()

    response = client.post(f"/api/imports/{imported['series_id']}/analyze")

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "failed"
    assert result["indicator_snapshot_count"] == 20
    assert result["signal"]["status"] == "no_setup"
    assert "insufficient_candle_history" in result["signal"]["risk_flags"]


def test_get_unknown_signal_returns_404(client: TestClient) -> None:
    response = client.get("/api/signals/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Signal not found."

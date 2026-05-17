import csv
import io
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
from app.services.export import PERFORMANCE_CSV_HEADERS, TRADES_CSV_HEADERS


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


def create_watchlist_item(
    client: TestClient, symbol: str = "AAPL", asset_class: str = "stock"
) -> int:
    response = client.post(
        "/api/watchlist",
        json={"symbol": symbol, "asset_class": asset_class, "exchange": "NASDAQ"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_open_trade(
    client: TestClient,
    symbol: str = "AAPL",
    strategy_type: str = "trend_pullback_long",
    asset_class: str = "stock",
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
            "position_size": "10",
            "opened_at": "2024-01-05T10:00:00Z",
        },
    )
    assert response.status_code == 201
    return response.json()


def close_trade(client: TestClient, trade: dict, exit_price: str = "115.00") -> dict:
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


def add_journal_entry(client: TestClient, trade_id: int) -> None:
    response = client.post(
        f"/api/trades/{trade_id}/journal",
        json={
            "setup_rule_followed": True,
            "entry_quality_score": 4,
            "stop_quality_score": 4,
            "exit_quality_score": 4,
            "discipline_score": 5,
            "market_context": "Strong uptrend.",
            "emotional_notes": "Calm.",
            "what_went_well": "Followed the plan.",
            "what_went_wrong": "Nothing major.",
            "lesson_learned": "Stay patient.",
            "reviewed_at": "2024-01-08T10:00:00Z",
        },
    )
    assert response.status_code == 201


def parse_csv(text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


# ─── Trades export ───────────────────────────────────────────────────────────


def test_trades_export_requires_auth() -> None:
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
    unauthenticated = TestClient(app, raise_server_exceptions=True)

    response = unauthenticated.get("/api/export/trades")
    assert response.status_code == 401


def test_trades_export_returns_csv_content_type(client: TestClient) -> None:
    response = client.get("/api/export/trades")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


def test_trades_export_has_stable_headers(client: TestClient) -> None:
    response = client.get("/api/export/trades")
    rows = parse_csv(response.text)
    if rows:
        assert list(rows[0].keys()) == TRADES_CSV_HEADERS
    else:
        first_line = response.text.splitlines()[0]
        assert first_line == ",".join(TRADES_CSV_HEADERS)


def test_trades_export_empty_when_no_trades(client: TestClient) -> None:
    response = client.get("/api/export/trades")
    assert response.status_code == 200
    rows = parse_csv(response.text)
    assert rows == []


def test_trades_export_includes_open_and_closed_trades(client: TestClient) -> None:
    create_open_trade(client, "AAPL")
    trade = create_open_trade(client, "MSFT")
    close_trade(client, trade)

    response = client.get("/api/export/trades")
    rows = parse_csv(response.text)
    assert len(rows) == 2
    symbols = {row["symbol"] for row in rows}
    assert symbols == {"AAPL", "MSFT"}


def test_trades_export_row_contains_performance_fields(client: TestClient) -> None:
    trade = create_open_trade(client, "AAPL")
    close_trade(client, trade, exit_price="115.00")

    response = client.get("/api/export/trades")
    rows = parse_csv(response.text)
    assert len(rows) == 1
    row = rows[0]

    assert row["symbol"] == "AAPL"
    assert row["strategy_type"] == "trend_pullback_long"
    assert row["asset_class"] == "stock"
    assert row["status"] == "closed"
    assert row["entry_price"] == "100.00"
    assert row["stop_loss"] == "95.00"
    assert row["exit_price"] == "115.00"
    assert row["exit_reason"] == "manual_exit"
    assert row["result_r"] != ""
    assert row["initial_risk_amount"] != ""


def test_trades_export_review_complete_reflects_journal(client: TestClient) -> None:
    create_open_trade(client, "AAPL")
    reviewed_trade = create_open_trade(client, "MSFT")
    close_trade(client, reviewed_trade)
    add_journal_entry(client, reviewed_trade["id"])

    response = client.get("/api/export/trades")
    rows = parse_csv(response.text)
    rows_by_symbol = {row["symbol"]: row for row in rows}

    assert rows_by_symbol["AAPL"]["review_complete"] == "no"
    assert rows_by_symbol["MSFT"]["review_complete"] == "yes"


def test_trades_export_content_disposition_header(client: TestClient) -> None:
    response = client.get("/api/export/trades")
    assert "attachment" in response.headers.get("content-disposition", "")
    assert "trades.csv" in response.headers.get("content-disposition", "")


# ─── Performance export ───────────────────────────────────────────────────────


def test_performance_export_requires_auth() -> None:
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
    unauthenticated = TestClient(app, raise_server_exceptions=True)

    response = unauthenticated.get("/api/export/performance")
    assert response.status_code == 401


def test_performance_export_returns_csv_content_type(client: TestClient) -> None:
    response = client.get("/api/export/performance")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


def test_performance_export_has_stable_headers(client: TestClient) -> None:
    response = client.get("/api/export/performance")
    first_line = response.text.splitlines()[0]
    assert first_line == ",".join(PERFORMANCE_CSV_HEADERS)


def test_performance_export_empty_state_has_overall_row(client: TestClient) -> None:
    response = client.get("/api/export/performance")
    rows = parse_csv(response.text)
    assert len(rows) == 1
    assert rows[0]["section"] == "overall"
    assert rows[0]["closed_trade_count"] == "0"
    assert rows[0]["total_r"] == "0.0000"


def test_performance_export_includes_strategy_and_asset_class_rows(client: TestClient) -> None:
    trade = create_open_trade(
        client, "AAPL", strategy_type="trend_pullback_long", asset_class="stock"
    )
    close_trade(client, trade)

    response = client.get("/api/export/performance")
    rows = parse_csv(response.text)

    sections = [row["section"] for row in rows]
    assert "overall" in sections
    assert "by_strategy" in sections
    assert "by_asset_class" in sections


def test_performance_export_overall_row_values(client: TestClient) -> None:
    trade = create_open_trade(client, "AAPL")
    close_trade(client, trade, exit_price="115.00")

    response = client.get("/api/export/performance")
    rows = parse_csv(response.text)
    overall = next(r for r in rows if r["section"] == "overall")

    assert overall["closed_trade_count"] == "1"
    assert overall["total_r"] == "3.0000"
    assert overall["best_r"] == "3.0000"
    assert overall["worst_r"] == "3.0000"


def test_performance_export_content_disposition_header(client: TestClient) -> None:
    response = client.get("/api/export/performance")
    assert "attachment" in response.headers.get("content-disposition", "")
    assert "performance.csv" in response.headers.get("content-disposition", "")

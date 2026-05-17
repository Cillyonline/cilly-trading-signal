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
    assert trade["is_review_complete"] is False
    assert trade["review_status"] == "not_ready"

    list_response = client.get("/api/trades")

    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == trade["id"]

    detail_response = client.get(f"/api/trades/{trade['id']}")

    assert detail_response.status_code == 200
    assert detail_response.json()["events"] == []


def test_create_trade_calculates_initial_risk_percent(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)
    settings_response = client.patch(
        "/api/settings",
        json={"account_size": "10000.00", "max_risk_percent": "2.00"},
    )
    assert settings_response.status_code == 200

    response = client.post(
        "/api/trades",
        json={
            "watchlist_item_id": watchlist_item_id,
            "strategy_type": "trend_pullback_long",
            "entry_price": "100.00",
            "stop_loss": "95.00",
            "target_1": "112.50",
            "position_size": "10",
            "opened_at": "2024-01-05T10:00:00Z",
        },
    )

    assert response.status_code == 201
    assert response.json()["initial_risk_amount"] == "50.00"
    assert response.json()["initial_risk_percent"] == "0.5000"


def test_create_trade_rejects_below_min_risk_reward(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)
    settings_response = client.patch("/api/settings", json={"min_risk_reward": "3.00"})
    assert settings_response.status_code == 200

    response = client.post(
        "/api/trades",
        json={
            "watchlist_item_id": watchlist_item_id,
            "strategy_type": "trend_pullback_long",
            "entry_price": "100.00",
            "stop_loss": "95.00",
            "target_1": "112.50",
            "position_size": "10",
            "opened_at": "2024-01-05T10:00:00Z",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Initial risk/reward is below configured minimum."


def test_create_trade_rejects_above_max_risk_percent(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)
    settings_response = client.patch(
        "/api/settings",
        json={"account_size": "10000.00", "max_risk_percent": "0.25"},
    )
    assert settings_response.status_code == 200

    response = client.post(
        "/api/trades",
        json={
            "watchlist_item_id": watchlist_item_id,
            "strategy_type": "trend_pullback_long",
            "entry_price": "100.00",
            "stop_loss": "95.00",
            "target_1": "112.50",
            "position_size": "10",
            "opened_at": "2024-01-05T10:00:00Z",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Initial risk percent exceeds configured maximum."


def test_create_trade_rejects_when_max_open_trades_reached(client: TestClient) -> None:
    watchlist_item_id = create_watchlist_item(client)
    settings_response = client.patch("/api/settings", json={"max_open_trades": 1})
    assert settings_response.status_code == 200

    first_response = client.post(
        "/api/trades",
        json={
            "watchlist_item_id": watchlist_item_id,
            "strategy_type": "trend_pullback_long",
            "entry_price": "100.00",
            "stop_loss": "95.00",
            "target_1": "112.50",
            "position_size": "10",
            "opened_at": "2024-01-05T10:00:00Z",
        },
    )
    second_response = client.post(
        "/api/trades",
        json={
            "watchlist_item_id": watchlist_item_id,
            "strategy_type": "trend_pullback_long",
            "entry_price": "110.00",
            "stop_loss": "105.00",
            "target_1": "122.50",
            "position_size": "10",
            "opened_at": "2024-01-06T10:00:00Z",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Maximum open trades reached."


def test_list_trades_returns_empty_list(client: TestClient) -> None:
    response = client.get("/api/trades")

    assert response.status_code == 200
    assert response.json() == []


def test_list_trades_filters_by_opened_date_strategy_and_asset_class(client: TestClient) -> None:
    stock_item_id = create_watchlist_item(client, "AAPL", "stock")
    crypto_item_id = create_watchlist_item(client, "BTCUSD", "crypto")
    create_manual_trade(
        client,
        watchlist_item_id=stock_item_id,
        opened_at="2024-01-05T10:00:00Z",
        strategy_type="trend_pullback_long",
    )
    matching_trade = create_manual_trade(
        client,
        watchlist_item_id=crypto_item_id,
        opened_at="2024-02-05T10:00:00Z",
        strategy_type="base_breakout_long",
    )

    response = client.get(
        "/api/trades",
        params={
            "opened_from": "2024-02-01T00:00:00Z",
            "opened_to": "2024-02-28T23:59:59Z",
            "strategy_type": "base_breakout_long",
            "asset_class": "crypto",
        },
    )

    assert response.status_code == 200
    assert [trade["id"] for trade in response.json()] == [matching_trade["id"]]


def test_list_trades_filters_by_review_and_rule_adherence(client: TestClient) -> None:
    reviewed_trade = close_manual_trade(client)
    unreviewed_trade = close_manual_trade(
        client,
        watchlist_item_id=create_watchlist_item(client, "MSFT", "stock"),
    )
    review_response = client.post(
        f"/api/trades/{reviewed_trade['id']}/journal",
        json={"reviewed_at": "2024-01-08T10:00:00Z", "setup_rule_followed": True},
    )
    assert review_response.status_code == 201

    reviewed_response = client.get(
        "/api/trades",
        params={"reviewed": "true", "setup_rule_followed": "true"},
    )
    unreviewed_response = client.get("/api/trades", params={"reviewed": "false"})

    assert reviewed_response.status_code == 200
    assert [trade["id"] for trade in reviewed_response.json()] == [reviewed_trade["id"]]
    assert unreviewed_response.status_code == 200
    assert [trade["id"] for trade in unreviewed_response.json()] == [unreviewed_trade["id"]]


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


def test_create_trade_event_logs_note(client: TestClient) -> None:
    trade = create_manual_trade(client)

    response = client.post(
        f"/api/trades/{trade['id']}/events",
        json={
            "event_type": "note",
            "event_time": "2024-01-06T10:00:00Z",
            "notes": "Reviewed position manually.",
        },
    )

    assert response.status_code == 201
    event = response.json()
    assert event["event_type"] == "note"
    assert event["notes"] == "Reviewed position manually."

    detail_response = client.get(f"/api/trades/{trade['id']}")

    assert detail_response.status_code == 200
    assert detail_response.json()["events"][0]["id"] == event["id"]


def test_create_trade_event_updates_stop_loss(client: TestClient) -> None:
    trade = create_manual_trade(client)

    response = client.post(
        f"/api/trades/{trade['id']}/events",
        json={
            "event_type": "stop_updated",
            "event_time": "2024-01-06T10:00:00Z",
            "price": "98.00",
            "notes": "Manual stop adjustment.",
        },
    )

    assert response.status_code == 201
    event = response.json()
    assert event["old_value"] == "95.00000000"
    assert event["new_value"] == "98.00"

    detail_response = client.get(f"/api/trades/{trade['id']}")

    assert detail_response.status_code == 200
    assert detail_response.json()["stop_loss"] == "98.00000000"


def test_create_trade_event_updates_target(client: TestClient) -> None:
    trade = create_manual_trade(client)

    response = client.post(
        f"/api/trades/{trade['id']}/events",
        json={
            "event_type": "target_updated",
            "event_time": "2024-01-06T10:00:00Z",
            "price": "118.00",
            "reason": "target_1",
        },
    )

    assert response.status_code == 201
    event = response.json()
    assert event["old_value"] == "112.50000000"
    assert event["new_value"] == "118.00"
    assert event["reason"] == "target_1"

    detail_response = client.get(f"/api/trades/{trade['id']}")

    assert detail_response.status_code == 200
    assert detail_response.json()["target_1"] == "118.00000000"


def test_create_trade_event_returns_404_for_unknown_trade(client: TestClient) -> None:
    response = client.post(
        "/api/trades/999/events",
        json={
            "event_type": "note",
            "event_time": "2024-01-06T10:00:00Z",
            "notes": "Missing trade.",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Trade not found."


def test_close_trade_calculates_result_r(client: TestClient) -> None:
    trade = create_manual_trade(client)

    response = client.post(
        f"/api/trades/{trade['id']}/close",
        json={
            "exit_price": "115.00",
            "exit_reason": "target_1",
            "closed_at": "2024-01-07T10:00:00Z",
            "notes": "Manual full close.",
        },
    )

    assert response.status_code == 200
    closed = response.json()
    assert closed["status"] == "closed"
    assert closed["exit_price"] == "115.00000000"
    assert closed["exit_reason"] == "target_1"
    assert closed["result_amount"] == "150.00"
    assert closed["result_r"] == "3.0000"
    assert closed["is_review_complete"] is False
    assert closed["review_status"] == "needs_review"
    assert closed["events"][-1]["event_type"] == "closed"
    assert closed["events"][-1]["notes"] == "Manual full close."


def test_close_trade_rejects_unknown_trade(client: TestClient) -> None:
    response = client.post(
        "/api/trades/999/close",
        json={
            "exit_price": "115.00",
            "exit_reason": "target_1",
            "closed_at": "2024-01-07T10:00:00Z",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Trade not found."


def test_close_trade_rejects_duplicate_close(client: TestClient) -> None:
    trade = create_manual_trade(client)
    payload = {
        "exit_price": "115.00",
        "exit_reason": "target_1",
        "closed_at": "2024-01-07T10:00:00Z",
    }

    first_response = client.post(f"/api/trades/{trade['id']}/close", json=payload)
    second_response = client.post(f"/api/trades/{trade['id']}/close", json=payload)

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Trade is already closed."


def test_close_trade_rejects_close_before_open(client: TestClient) -> None:
    trade = create_manual_trade(client)

    response = client.post(
        f"/api/trades/{trade['id']}/close",
        json={
            "exit_price": "115.00",
            "exit_reason": "target_1",
            "closed_at": "2024-01-04T10:00:00Z",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "closed_at must be after opened_at."


def test_create_journal_entry_for_closed_trade(client: TestClient) -> None:
    trade = close_manual_trade(client)

    response = client.post(
        f"/api/trades/{trade['id']}/journal",
        json={
            "setup_rule_followed": True,
            "entry_quality_score": 4,
            "stop_quality_score": 5,
            "exit_quality_score": 3,
            "discipline_score": 4,
            "market_context": "Trend intact, broader market constructive.",
            "emotional_notes": "Stayed calm during pullback.",
            "what_went_well": "Waited for planned entry and respected risk.",
            "what_went_wrong": "Exit was slightly early.",
            "lesson_learned": "Review exit trigger before market open.",
            "reviewed_at": "2024-01-08T10:00:00Z",
        },
    )

    assert response.status_code == 201
    journal_entry = response.json()
    assert journal_entry["trade_id"] == trade["id"]
    assert journal_entry["setup_rule_followed"] is True
    assert journal_entry["discipline_score"] == 4
    assert journal_entry["lesson_learned"] == "Review exit trigger before market open."

    detail_response = client.get(f"/api/trades/{trade['id']}")

    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["journal_entry"]["id"] == journal_entry["id"]
    assert detail["is_review_complete"] is True
    assert detail["review_status"] == "reviewed"


def test_create_journal_entry_rejects_unknown_trade(client: TestClient) -> None:
    response = client.post(
        "/api/trades/999/journal",
        json={"reviewed_at": "2024-01-08T10:00:00Z"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Trade not found."


def test_create_journal_entry_rejects_open_trade(client: TestClient) -> None:
    trade = create_manual_trade(client)

    response = client.post(
        f"/api/trades/{trade['id']}/journal",
        json={"reviewed_at": "2024-01-08T10:00:00Z"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Trade must be closed before review."


def test_create_journal_entry_rejects_duplicate_review(client: TestClient) -> None:
    trade = close_manual_trade(client)
    payload = {"reviewed_at": "2024-01-08T10:00:00Z", "discipline_score": 4}

    first_response = client.post(f"/api/trades/{trade['id']}/journal", json=payload)
    second_response = client.post(f"/api/trades/{trade['id']}/journal", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Trade already has a journal review."


def sequential_csv(row_count: int = 201) -> str:
    rows = ["time,open,high,low,close,volume"]
    start = date(2024, 1, 1)
    for index in range(row_count):
        current_date = start + timedelta(days=index)
        close = 100 + index
        rows.append(f"{current_date.isoformat()},{close - 1},{close + 2},{close - 2},{close},1000")
    return "\n".join(rows)


def create_manual_trade(
    client: TestClient,
    watchlist_item_id: int | None = None,
    opened_at: str = "2024-01-05T10:00:00Z",
    strategy_type: str = "trend_pullback_long",
) -> dict:
    watchlist_item_id = watchlist_item_id or create_watchlist_item(client)
    response = client.post(
        "/api/trades",
        json={
            "watchlist_item_id": watchlist_item_id,
            "strategy_type": strategy_type,
            "entry_price": "100.00",
            "stop_loss": "95.00",
            "target_1": "112.50",
            "target_2": "120.00",
            "position_size": "10",
            "opened_at": opened_at,
        },
    )
    assert response.status_code == 201
    return response.json()


def close_manual_trade(client: TestClient, watchlist_item_id: int | None = None) -> dict:
    trade = create_manual_trade(client, watchlist_item_id=watchlist_item_id)
    response = client.post(
        f"/api/trades/{trade['id']}/close",
        json={
            "exit_price": "115.00",
            "exit_reason": "target_1",
            "closed_at": "2024-01-07T10:00:00Z",
        },
    )
    assert response.status_code == 200
    return response.json()

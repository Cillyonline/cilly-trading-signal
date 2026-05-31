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
        "journal_analytics": {
            "closed_trade_count": 0,
            "reviewed_trade_count": 0,
            "missing_review_count": 0,
            "setup_rule_followed_count": 0,
            "setup_rule_broken_count": 0,
            "setup_rule_unknown_count": 0,
            "average_entry_quality_score": None,
            "average_stop_quality_score": None,
            "average_exit_quality_score": None,
            "average_discipline_score": None,
            "min_strategy_sample_size": 3,
            "by_strategy": [],
            "small_sample_notice": (
                "Journal analytics are process quality summaries from manually reviewed closed "
                "trades. Small samples are directional review prompts only, not prediction, edge "
                "validation, or profit validation."
            ),
        },
        "open_portfolio_risk": {
            "open_trade_count": 0,
            "complete_risk_count": 0,
            "incomplete_risk_count": 0,
            "documented_initial_risk_amount": "0.00",
            "documented_initial_risk_percent": "0.0000",
            "max_risk_percent": "1.00",
            "warning_status": "ok",
            "warnings": [],
            "asset_concentration": {
                "warning_status": "ok",
                "warning_threshold_percent": "50.00",
                "warnings": [],
                "by_asset_class": [],
                "by_symbol": [],
                "by_sector": [],
                "by_industry": [],
                "review_only_notice": (
                    "Concentration warnings use only documented active trades and available local "
                    "metadata. They are process review prompts, not a true correlation engine or "
                    "trade recommendation."
                ),
            },
            "correlation_proxies": {
                "warning_status": "ok",
                "warnings": [],
                "review_only_notice": (
                    "Correlation proxy warnings use simple documented exposure buckets only. "
                    "They are not a statistical correlation matrix, live market data, or trade "
                    "instruction."
                ),
            },
            "by_strategy": [],
            "by_asset_class": [],
            "review_only_notice": (
                "Active portfolio risk is based only on manually documented non-closed trades. "
                "It is review-only, not broker/account sync, automatic position sizing, an "
                "order recommendation, or trading advice."
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
        "Documented active risk percent exceeds the configured max risk percent.",
        "Some active trades are missing complete documented risk data.",
    ]
    assert risk["asset_concentration"]["warning_status"] == "warning"
    assert risk["correlation_proxies"]["warning_status"] == "unknown"
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


def test_performance_summary_treats_managed_trade_statuses_as_active(
    client: TestClient,
) -> None:
    update_account_size(client, "10000.00")
    managed_trade = create_open_trade(client, "AAPL", asset_class="stock")
    closed_trade = close_trade(
        client,
        create_open_trade(client, "MSFT", asset_class="stock"),
        "110.00",
    )

    set_trade_status(client, managed_trade["id"], "partial_profit")
    set_trade_status(client, closed_trade["id"], "reviewed")

    response = client.get("/api/performance/summary")

    assert response.status_code == 200
    risk = response.json()["open_portfolio_risk"]
    assert risk["open_trade_count"] == 1
    assert risk["complete_risk_count"] == 1
    assert risk["documented_initial_risk_amount"] == "50.00"
    assert risk["asset_concentration"]["by_symbol"] == [
        {"group": "AAPL", "open_trade_count": 1, "open_trade_percent": "100.00", "warning": False}
    ]


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
    assert risk["warnings"] == ["Some active trades are missing complete documented risk data."]


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


def test_performance_summary_includes_asset_concentration_warnings(client: TestClient) -> None:
    update_account_size(client, "10000.00")
    create_open_trade(client, "AAPL", strategy_type="trend_pullback_long", asset_class="stock")
    create_open_trade(client, "MSFT", strategy_type="base_breakout_long", asset_class="stock")
    create_open_trade(client, "BTCUSD", strategy_type="trend_pullback_long", asset_class="crypto")

    response = client.get("/api/performance/summary")

    assert response.status_code == 200
    concentration = response.json()["open_portfolio_risk"]["asset_concentration"]
    assert concentration["warning_status"] == "warning"
    assert concentration["warning_threshold_percent"] == "50.00"
    assert "stock represents 66.67% of active trades." in concentration["warnings"]
    assert "unknown_sector represents 100.00% of active trades." in concentration["warnings"]
    assert "true correlation engine" in concentration["review_only_notice"]
    assert concentration["by_asset_class"] == [
        {"group": "crypto", "open_trade_count": 1, "open_trade_percent": "33.33", "warning": False},
        {"group": "stock", "open_trade_count": 2, "open_trade_percent": "66.67", "warning": True},
    ]
    assert concentration["by_symbol"] == [
        {"group": "AAPL", "open_trade_count": 1, "open_trade_percent": "33.33", "warning": False},
        {"group": "BTCUSD", "open_trade_count": 1, "open_trade_percent": "33.33", "warning": False},
        {"group": "MSFT", "open_trade_count": 1, "open_trade_percent": "33.33", "warning": False},
    ]
    assert concentration["by_sector"] == [
        {
            "group": "unknown_sector",
            "open_trade_count": 3,
            "open_trade_percent": "100.00",
            "warning": True,
        }
    ]
    assert concentration["by_industry"] == [
        {
            "group": "unknown_industry",
            "open_trade_count": 3,
            "open_trade_percent": "100.00",
            "warning": True,
        }
    ]


def test_performance_summary_includes_correlation_proxy_warnings(client: TestClient) -> None:
    update_account_size(client, "10000.00")
    create_open_trade(client, "BTCUSD", strategy_type="trend_pullback_long", asset_class="crypto")
    create_open_trade(client, "ETHUSD", strategy_type="base_breakout_long", asset_class="crypto")
    create_open_trade(client, "AAPL", strategy_type="trend_pullback_long", asset_class="stock")

    response = client.get("/api/performance/summary")

    assert response.status_code == 200
    proxies = response.json()["open_portfolio_risk"]["correlation_proxies"]
    assert proxies["warning_status"] == "warning"
    assert "statistical correlation matrix" in proxies["review_only_notice"]
    assert proxies["warnings"] == [
        {
            "key": "crypto_btc_beta_heavy",
            "label": "Crypto BTC-beta-heavy proxy",
            "status": "warning",
            "open_trade_count": 2,
            "symbols": ["BTCUSD", "ETHUSD"],
            "message": "Multiple active crypto exposures match a BTC-beta-heavy symbol proxy.",
        },
        {
            "key": "stock_sector_heavy",
            "label": "Stock sector-heavy proxy",
            "status": "unknown",
            "open_trade_count": 1,
            "symbols": ["AAPL"],
            "message": (
                "Stock sector proxy is unknown because active trades do not store sector metadata."
            ),
        },
    ]


def test_performance_summary_includes_journal_analytics(client: TestClient) -> None:
    trades = [
        close_trade(
            client,
            create_open_trade(client, "AAPL", strategy_type="trend_pullback_long"),
            "115.00",
        ),
        close_trade(
            client,
            create_open_trade(client, "MSFT", strategy_type="trend_pullback_long"),
            "110.00",
        ),
        close_trade(
            client,
            create_open_trade(client, "NVDA", strategy_type="trend_pullback_long"),
            "95.00",
        ),
        close_trade(
            client,
            create_open_trade(client, "BTCUSD", strategy_type="base_breakout_long"),
            "110.00",
        ),
    ]
    create_journal_entry(
        client,
        trades[0]["id"],
        setup_rule_followed=True,
        entry_quality_score=5,
        stop_quality_score=4,
        exit_quality_score=3,
        discipline_score=5,
    )
    create_journal_entry(
        client,
        trades[1]["id"],
        setup_rule_followed=False,
        entry_quality_score=3,
        stop_quality_score=3,
        exit_quality_score=2,
        discipline_score=2,
    )
    create_journal_entry(
        client,
        trades[2]["id"],
        setup_rule_followed=None,
        entry_quality_score=4,
        stop_quality_score=5,
        exit_quality_score=None,
        discipline_score=4,
    )

    response = client.get("/api/performance/summary")

    assert response.status_code == 200
    analytics = response.json()["journal_analytics"]
    assert analytics["closed_trade_count"] == 4
    assert analytics["reviewed_trade_count"] == 3
    assert analytics["missing_review_count"] == 1
    assert analytics["setup_rule_followed_count"] == 1
    assert analytics["setup_rule_broken_count"] == 1
    assert analytics["setup_rule_unknown_count"] == 1
    assert analytics["average_entry_quality_score"] == "4.00"
    assert analytics["average_stop_quality_score"] == "4.00"
    assert analytics["average_exit_quality_score"] == "2.50"
    assert analytics["average_discipline_score"] == "3.67"
    assert "not prediction" in analytics["small_sample_notice"]
    assert analytics["by_strategy"] == [
        {
            "strategy_type": "trend_pullback_long",
            "reviewed_trade_count": 3,
            "setup_rule_followed_count": 1,
            "setup_rule_broken_count": 1,
            "setup_rule_unknown_count": 1,
            "average_entry_quality_score": "4.00",
            "average_stop_quality_score": "4.00",
            "average_exit_quality_score": "2.50",
            "average_discipline_score": "3.67",
        }
    ]


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


def set_trade_status(client: TestClient, trade_id: int, status: str) -> None:
    from app.models import Trade, TradeStatus

    db_override = client.app.dependency_overrides[get_db]
    db_generator = db_override()
    db = next(db_generator)
    try:
        trade = db.get(Trade, trade_id)
        assert trade is not None
        trade.status = TradeStatus(status)
        db.commit()
    finally:
        db_generator.close()


def create_journal_entry(
    client: TestClient,
    trade_id: int,
    setup_rule_followed: bool | None,
    entry_quality_score: int | None,
    stop_quality_score: int | None,
    exit_quality_score: int | None,
    discipline_score: int | None,
) -> dict:
    response = client.post(
        f"/api/trades/{trade_id}/journal",
        json={
            "setup_rule_followed": setup_rule_followed,
            "entry_quality_score": entry_quality_score,
            "stop_quality_score": stop_quality_score,
            "exit_quality_score": exit_quality_score,
            "discipline_score": discipline_score,
            "reviewed_at": "2024-01-08T10:00:00Z",
        },
    )
    assert response.status_code == 201
    return response.json()

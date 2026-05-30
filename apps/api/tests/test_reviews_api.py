from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models import *  # noqa: F403
from app.models.enums import AssetClass, SignalStatus, StrategyType, UserRole
from app.models.review import ReviewEntry
from app.models.signal import Signal
from app.models.user import User
from app.models.watchlist import WatchlistItem
from app.services.auth import get_or_create_admin_user


@pytest.fixture()
def db_session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Iterator[TestClient]:
    def override_get_db() -> Iterator[Session]:
        yield db_session

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


def login(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "change-this-password"},
    )
    assert response.status_code == 200


def create_signal(db: Session) -> Signal:
    user = get_or_create_admin_user(db)
    watchlist_item = WatchlistItem(
        user_id=user.id,
        symbol="AAPL",
        asset_class=AssetClass.STOCK,
        exchange="NASDAQ",
    )
    db.add(watchlist_item)
    db.flush()
    signal = Signal(
        user_id=user.id,
        watchlist_item_id=watchlist_item.id,
        strategy_type=StrategyType.TREND_PULLBACK_LONG,
        status=SignalStatus.ARMED,
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal


def test_review_batches_require_authentication(client: TestClient) -> None:
    response = client.get("/api/reviews/batches")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required."


def test_create_review_batch_records_evidence_only_summary(client: TestClient) -> None:
    login(client)

    response = client.post(
        "/api/reviews/batches",
        json={
            "name": "Q1 paper review",
            "review_type": "paper",
            "asset_class": "stock",
            "strategy_type": "trend_pullback_long",
            "review_window_start": "2026-01-01",
            "review_window_end": "2026-03-31",
            "data_source": "stored csv",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Q1 paper review"
    assert body["entries"] == []
    assert body["summary"]["reviewed_count"] == 0
    assert "not backtests" in body["summary"]["evidence_only_notice"]


def test_review_entries_surface_repeated_calibration_followups(
    client: TestClient, db_session: Session
) -> None:
    signal = create_signal(db_session)
    login(client)
    batch_id = client.post(
        "/api/reviews/batches",
        json={"name": "Historical sample", "review_type": "historical"},
    ).json()["id"]

    payload = {
        "signal_id": signal.id,
        "symbol": "aapl",
        "asset_class": "stock",
        "strategy_type": "trend_pullback_long",
        "stored_data_start": "2026-01-01",
        "stored_data_end": "2026-01-31",
        "benchmark_context": "present",
        "signal_status": "armed",
        "score_class": "b_setup",
        "quality_blockers": [{"key": "market_regime"}],
        "manual_review_label": "too_permissive",
        "notes": "Sanitized process note only.",
    }

    first = client.post(f"/api/reviews/batches/{batch_id}/entries", json=payload)
    second = client.post(
        f"/api/reviews/batches/{batch_id}/entries", json={**payload, "signal_id": None}
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["symbol"] == "AAPL"
    assert first.json()["follow_up_needed"] is True
    assert db_session.scalars(select(ReviewEntry)).all()
    body = client.get(f"/api/reviews/batches/{batch_id}").json()
    assert body["summary"]["label_counts"] == {"too_permissive": 2}
    assert body["summary"]["follow_up_needed_count"] == 2
    assert body["summary"]["repeated_attention_labels"] == ["too_permissive"]
    assert body["summary"]["repeated_blocker_patterns"] == ["market_regime"]


def test_review_batch_csv_export_contains_evidence_only_fields(client: TestClient) -> None:
    login(client)
    batch_id = client.post(
        "/api/reviews/batches",
        json={"name": "CSV sample", "review_type": "paper"},
    ).json()["id"]
    client.post(
        f"/api/reviews/batches/{batch_id}/entries",
        json={
            "symbol": "BTCUSD",
            "asset_class": "crypto",
            "strategy_type": "base_breakout_long",
            "signal_status": "watchlist",
            "score_class": "watchlist",
            "benchmark_context": "present",
            "quality_blockers": [{"key": "market_regime"}],
            "manual_review_label": "unclear",
            "follow_up_issue_url": "https://github.com/Cillyonline/cilly-trading-signal/issues/1",
            "notes": "Review note only.",
        },
    )

    response = client.get(f"/api/reviews/batches/{batch_id}/export")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "review-batch-" in response.headers["content-disposition"]
    body = response.text
    assert "evidence_only_notice" in body
    assert "not backtests" in body
    assert "BTCUSD" in body
    assert "unclear" in body
    assert "market_regime" in body
    assert "admin@example.com" not in body


def test_review_entry_requires_outcome_measurement_rule(client: TestClient) -> None:
    login(client)
    batch_id = client.post(
        "/api/reviews/batches",
        json={"name": "Paper review", "review_type": "paper"},
    ).json()["id"]

    response = client.post(
        f"/api/reviews/batches/{batch_id}/entries",
        json={
            "symbol": "BTCUSD",
            "asset_class": "crypto",
            "strategy_type": "base_breakout_long",
            "signal_status": "watchlist",
            "manual_review_label": "useful",
            "outcome_r": "1.2",
        },
    )

    assert response.status_code == 422


def test_review_entry_rejects_other_user_signal(client: TestClient, db_session: Session) -> None:
    other_user = User(
        email="other@example.com",
        password_hash="unused",
        display_name="Other",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(other_user)
    db_session.flush()
    watchlist_item = WatchlistItem(
        user_id=other_user.id, symbol="MSFT", asset_class=AssetClass.STOCK
    )
    db_session.add(watchlist_item)
    db_session.flush()
    signal = Signal(
        user_id=other_user.id,
        watchlist_item_id=watchlist_item.id,
        strategy_type=StrategyType.TREND_PULLBACK_LONG,
    )
    db_session.add(signal)
    db_session.commit()
    login(client)
    batch_id = client.post(
        "/api/reviews/batches",
        json={"name": "Historical sample", "review_type": "historical"},
    ).json()["id"]

    response = client.post(
        f"/api/reviews/batches/{batch_id}/entries",
        json={
            "signal_id": signal.id,
            "symbol": "MSFT",
            "asset_class": "stock",
            "strategy_type": "trend_pullback_long",
            "signal_status": "watchlist",
            "manual_review_label": "unclear",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Signal not found."

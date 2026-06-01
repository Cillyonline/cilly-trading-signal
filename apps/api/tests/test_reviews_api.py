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
from app.models.review import ReviewBatch, ReviewEntry, ReviewEntryRevision
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
    assert body["summary"]["repeated_false_positive_patterns"] == [
        "market_regime",
        "market_regime_too_loose",
    ]


def test_review_repeated_findings_require_two_matching_entries(client: TestClient) -> None:
    login(client)
    batch_id = client.post(
        "/api/reviews/batches",
        json={"name": "Threshold sample", "review_type": "historical"},
    ).json()["id"]
    base_payload = {
        "symbol": "AAPL",
        "asset_class": "stock",
        "strategy_type": "trend_pullback_long",
        "signal_status": "watchlist",
        "quality_blockers": [{"key": "market_regime"}],
        "manual_review_label": "unclear",
    }

    client.post(f"/api/reviews/batches/{batch_id}/entries", json=base_payload)
    first_summary = client.get(f"/api/reviews/batches/{batch_id}").json()["summary"]
    client.post(
        f"/api/reviews/batches/{batch_id}/entries",
        json={**base_payload, "symbol": "MSFT"},
    )
    second_summary = client.get(f"/api/reviews/batches/{batch_id}").json()["summary"]

    assert first_summary["repeated_attention_labels"] == []
    assert first_summary["repeated_blocker_patterns"] == []
    assert first_summary["repeated_false_positive_patterns"] == []
    assert second_summary["repeated_attention_labels"] == ["unclear"]
    assert second_summary["repeated_blocker_patterns"] == ["market_regime"]
    assert second_summary["repeated_false_positive_patterns"] == []


def test_review_summary_surfaces_repeated_false_positive_patterns(client: TestClient) -> None:
    login(client)
    batch_id = client.post(
        "/api/reviews/batches",
        json={"name": "False positive sample", "review_type": "paper"},
    ).json()["id"]
    for symbol in ["AAPL", "MSFT"]:
        response = client.post(
            f"/api/reviews/batches/{batch_id}/entries",
            json={
                "symbol": symbol,
                "asset_class": "stock",
                "strategy_type": "base_breakout_long",
                "signal_status": "armed",
                "score_class": "b_setup",
                "quality_blockers": [{"key": "trigger"}],
                "risk_flags": ["breakout_close_not_near_high"],
                "manual_review_label": "too_permissive",
                "notes": "Breakout looked reviewable despite weak close quality.",
            },
        )
        assert response.status_code == 201

    summary = client.get(f"/api/reviews/batches/{batch_id}").json()["summary"]

    assert summary["repeated_false_positive_patterns"] == [
        "breakout_close_not_near_high",
        "trigger",
        "trigger_too_strict",
    ]


def test_review_summary_classifies_repeated_finding_categories(client: TestClient) -> None:
    login(client)
    batch_id = client.post(
        "/api/reviews/batches",
        json={"name": "Category sample", "review_type": "historical"},
    ).json()["id"]
    for symbol in ["AAPL", "MSFT"]:
        client.post(
            f"/api/reviews/batches/{batch_id}/entries",
            json={
                "symbol": symbol,
                "asset_class": "stock",
                "strategy_type": "trend_pullback_long",
                "signal_status": "watchlist",
                "quality_blockers": [{"key": "market_regime"}],
                "manual_review_label": "too_permissive",
            },
        )
    client.post(
        f"/api/reviews/batches/{batch_id}/entries",
        json={
            "symbol": "BTCUSD",
            "asset_class": "crypto",
            "strategy_type": "base_breakout_long",
            "signal_status": "watchlist",
            "manual_review_label": "unclear",
        },
    )

    summary = client.get(f"/api/reviews/batches/{batch_id}").json()["summary"]

    assert summary["finding_category_counts"] == {
        "market_regime_too_loose": 2,
        "unknown": 1,
    }
    assert summary["repeated_finding_categories"] == ["market_regime_too_loose"]


def test_review_entry_finding_category_source_is_auditable(client: TestClient) -> None:
    login(client)
    batch_id = client.post(
        "/api/reviews/batches",
        json={"name": "Auditable category sample", "review_type": "historical"},
    ).json()["id"]

    derived = client.post(
        f"/api/reviews/batches/{batch_id}/entries",
        json={
            "symbol": "AAPL",
            "asset_class": "stock",
            "strategy_type": "trend_pullback_long",
            "signal_status": "watchlist",
            "quality_blockers": [{"key": "market_regime"}],
            "manual_review_label": "too_permissive",
        },
    )
    manual = client.post(
        f"/api/reviews/batches/{batch_id}/entries",
        json={
            "symbol": "MSFT",
            "asset_class": "stock",
            "strategy_type": "trend_pullback_long",
            "signal_status": "watchlist",
            "manual_review_label": "unclear",
            "finding_category": "Risk Plan Unclear",
            "finding_category_source": "manual",
        },
    )

    assert derived.status_code == 201
    assert derived.json()["finding_category"] == "market_regime_too_loose"
    assert derived.json()["finding_category_source"] == "derived"
    assert manual.status_code == 201
    assert manual.json()["finding_category"] == "risk_plan_unclear"
    assert manual.json()["finding_category_source"] == "manual"

    summary = client.get(f"/api/reviews/batches/{batch_id}").json()["summary"]
    assert summary["finding_category_counts"] == {
        "market_regime_too_loose": 1,
        "risk_plan_unclear": 1,
    }


def test_review_entry_edit_audits_category_correction(client: TestClient) -> None:
    login(client)
    batch_id = client.post(
        "/api/reviews/batches",
        json={"name": "Category correction sample", "review_type": "paper"},
    ).json()["id"]
    entry = client.post(
        f"/api/reviews/batches/{batch_id}/entries",
        json={
            "symbol": "AAPL",
            "asset_class": "stock",
            "strategy_type": "trend_pullback_long",
            "signal_status": "watchlist",
            "quality_blockers": [{"key": "market_regime"}],
            "manual_review_label": "too_permissive",
        },
    ).json()

    response = client.patch(
        f"/api/reviews/batches/{batch_id}/entries/{entry['id']}",
        json={
            "symbol": "AAPL",
            "asset_class": "stock",
            "strategy_type": "trend_pullback_long",
            "signal_status": "watchlist",
            "manual_review_label": "too_permissive",
            "finding_category": "risk_plan_unclear",
            "finding_category_source": "manual",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["finding_category"] == "risk_plan_unclear"
    assert body["finding_category_source"] == "manual"
    assert body["revisions"][0]["previous_values"]["finding_category"] == "market_regime_too_loose"
    assert body["revisions"][0]["previous_values"]["finding_category_source"] == "derived"


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
    assert "finding_category" in body
    assert "finding_category_source" in body
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


def test_review_entry_edit_updates_summary_and_preserves_created_at(client: TestClient) -> None:
    login(client)
    batch_id = client.post(
        "/api/reviews/batches",
        json={"name": "Edit sample", "review_type": "paper"},
    ).json()["id"]
    first = client.post(
        f"/api/reviews/batches/{batch_id}/entries",
        json={
            "symbol": "aapl",
            "asset_class": "stock",
            "strategy_type": "trend_pullback_long",
            "signal_status": "watchlist",
            "quality_blockers": ["market_regime"],
            "manual_review_label": "unclear",
        },
    ).json()

    response = client.patch(
        f"/api/reviews/batches/{batch_id}/entries/{first['id']}",
        json={
            "symbol": "msft",
            "asset_class": "stock",
            "strategy_type": "base_breakout_long",
            "signal_status": "armed",
            "quality_blockers": ["liquidity"],
            "manual_review_label": "too_strict",
            "outcome_r": "0.5",
            "outcome_measurement_rule": "Measured at close.",
            "notes": "Corrected review entry.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == first["id"]
    assert body["created_at"] == first["created_at"]
    assert body["updated_at"] >= first["updated_at"]
    assert body["symbol"] == "MSFT"
    assert body["manual_review_label"] == "too_strict"
    batch = client.get(f"/api/reviews/batches/{batch_id}").json()
    assert batch["summary"]["label_counts"] == {"too_strict": 1}
    assert batch["summary"]["follow_up_needed_count"] == 1


def test_review_entry_edit_records_append_only_revision_history(client: TestClient) -> None:
    login(client)
    batch_id = client.post(
        "/api/reviews/batches",
        json={"name": "Revision sample", "review_type": "paper"},
    ).json()["id"]
    first = client.post(
        f"/api/reviews/batches/{batch_id}/entries",
        json={
            "symbol": "aapl",
            "asset_class": "stock",
            "strategy_type": "trend_pullback_long",
            "signal_status": "watchlist",
            "score_class": "watchlist",
            "quality_blockers": ["market_regime"],
            "manual_review_label": "unclear",
            "notes": "Original sanitized note.",
        },
    ).json()

    first_update = client.patch(
        f"/api/reviews/batches/{batch_id}/entries/{first['id']}",
        json={
            "symbol": "msft",
            "asset_class": "stock",
            "strategy_type": "trend_pullback_long",
            "signal_status": "armed",
            "score_class": "b_setup",
            "quality_blockers": ["liquidity"],
            "manual_review_label": "too_strict",
            "notes": "First correction.",
        },
    )
    second_update = client.patch(
        f"/api/reviews/batches/{batch_id}/entries/{first['id']}",
        json={
            "symbol": "nvda",
            "asset_class": "stock",
            "strategy_type": "base_breakout_long",
            "signal_status": "triggered",
            "score_class": "a_setup",
            "quality_blockers": ["trigger"],
            "manual_review_label": "useful",
            "notes": "Second correction.",
        },
    )

    assert first_update.status_code == 200
    assert second_update.status_code == 200
    body = second_update.json()
    assert body["symbol"] == "NVDA"
    assert [revision["revision_number"] for revision in body["revisions"]] == [1, 2]
    assert body["revisions"][0]["previous_values"]["symbol"] == "AAPL"
    assert body["revisions"][0]["previous_values"]["manual_review_label"] == "unclear"
    assert body["revisions"][0]["previous_values"]["notes"] == "Original sanitized note."
    assert body["revisions"][1]["previous_values"]["symbol"] == "MSFT"
    assert body["revisions"][1]["previous_values"]["manual_review_label"] == "too_strict"

    batch = client.get(f"/api/reviews/batches/{batch_id}").json()
    entry = batch["entries"][0]
    assert entry["symbol"] == "NVDA"
    assert len(entry["revisions"]) == 2
    assert entry["revisions"][0]["previous_values"]["symbol"] == "AAPL"


def test_review_entry_edit_enforces_validation(client: TestClient) -> None:
    login(client)
    batch_id = client.post(
        "/api/reviews/batches",
        json={"name": "Validation sample", "review_type": "paper"},
    ).json()["id"]
    entry_id = client.post(
        f"/api/reviews/batches/{batch_id}/entries",
        json={
            "symbol": "BTCUSD",
            "asset_class": "crypto",
            "strategy_type": "base_breakout_long",
            "signal_status": "watchlist",
            "manual_review_label": "useful",
        },
    ).json()["id"]

    response = client.patch(
        f"/api/reviews/batches/{batch_id}/entries/{entry_id}",
        json={
            "symbol": "BTCUSD",
            "asset_class": "crypto",
            "strategy_type": "base_breakout_long",
            "signal_status": "watchlist",
            "manual_review_label": "useful",
            "outcome_r": "1.1",
        },
    )

    assert response.status_code == 422


def test_review_entry_edit_rejects_other_user_entry(
    client: TestClient, db_session: Session
) -> None:
    other_user = User(
        email="owner@example.com",
        password_hash="unused",
        display_name="Owner",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(other_user)
    db_session.flush()
    other_batch = ReviewBatch(
        user_id=other_user.id,
        name="Other batch",
        review_type="paper",
    )
    db_session.add(other_batch)
    db_session.flush()
    entry = ReviewEntry(
        batch_id=other_batch.id,
        user_id=other_user.id,
        symbol="MSFT",
        asset_class=AssetClass.STOCK,
        strategy_type=StrategyType.TREND_PULLBACK_LONG,
        signal_status=SignalStatus.WATCHLIST,
        manual_review_label="unclear",
    )
    db_session.add(entry)
    db_session.commit()
    login(client)
    batch_id = client.post(
        "/api/reviews/batches",
        json={"name": "Own batch", "review_type": "paper"},
    ).json()["id"]

    response = client.patch(
        f"/api/reviews/batches/{batch_id}/entries/{entry.id}",
        json={
            "symbol": "MSFT",
            "asset_class": "stock",
            "strategy_type": "trend_pullback_long",
            "signal_status": "watchlist",
            "manual_review_label": "unclear",
        },
    )

    assert response.status_code == 404
    assert db_session.scalars(select(ReviewEntryRevision)).all() == []


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

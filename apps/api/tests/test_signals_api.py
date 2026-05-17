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
from app.models.enums import AssetClass, SignalStatus, StrategyType
from app.models.signal import Signal
from app.models.trade import Trade
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


def create_signal(db: Session, status: SignalStatus = SignalStatus.WATCHLIST) -> Signal:
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
        status=status,
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal


def test_update_signal_status_requires_authentication(
    client: TestClient, db_session: Session
) -> None:
    signal = create_signal(db_session)

    response = client.patch(f"/api/signals/{signal.id}/status", json={"status": "armed"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required."


def test_update_signal_status_allows_manual_review_transition(
    client: TestClient, db_session: Session
) -> None:
    signal = create_signal(db_session)
    login(client)

    response = client.patch(f"/api/signals/{signal.id}/status", json={"status": "armed"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "armed"
    assert body["symbol"] == "AAPL"
    assert db_session.scalars(select(Trade)).all() == []


def test_update_signal_status_rejects_invalid_manual_transition(
    client: TestClient, db_session: Session
) -> None:
    signal = create_signal(db_session, status=SignalStatus.INVALIDATED)
    login(client)

    response = client.patch(f"/api/signals/{signal.id}/status", json={"status": "armed"})

    assert response.status_code == 422
    assert response.json()["detail"] == "Signal status transition is not allowed."


def test_update_signal_status_returns_404_for_unknown_signal(client: TestClient) -> None:
    login(client)

    response = client.patch("/api/signals/999/status", json={"status": "armed"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Signal not found."


def test_update_signal_review_note_persists_manual_context(
    client: TestClient, db_session: Session
) -> None:
    signal = create_signal(db_session)
    original_status = signal.status
    original_score = signal.score
    login(client)

    response = client.patch(
        f"/api/signals/{signal.id}/review-note",
        json={"review_note": "Armed only if volume confirms. No execution from app."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["review_note"] == "Armed only if volume confirms. No execution from app."
    assert body["status"] == original_status
    assert body["score"] == original_score


def test_update_signal_review_note_can_clear_note(
    client: TestClient, db_session: Session
) -> None:
    signal = create_signal(db_session)
    signal.review_note = "Old note"
    db_session.commit()
    login(client)

    response = client.patch(
        f"/api/signals/{signal.id}/review-note",
        json={"review_note": "  "},
    )

    assert response.status_code == 200
    assert response.json()["review_note"] is None


def test_update_signal_review_note_returns_404_for_unknown_signal(
    client: TestClient,
) -> None:
    login(client)

    response = client.patch(
        "/api/signals/999/review-note",
        json={"review_note": "Review note"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Signal not found."

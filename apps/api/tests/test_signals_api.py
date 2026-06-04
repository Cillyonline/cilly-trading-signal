from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models import *  # noqa: F403
from app.models.enums import (
    AssetClass,
    MarketDataSource,
    MarketDataStatus,
    SignalStatus,
    StrategyType,
    Timeframe,
    UserRole,
)
from app.models.market_data import MarketDataCandle, MarketDataSeries
from app.models.signal import Signal, SignalReviewEvent
from app.models.trade import Trade
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
    assert body["review_events"][0]["event_type"] == "status_change"
    assert body["review_events"][0]["previous_status"] == "watchlist"
    assert body["review_events"][0]["new_status"] == "armed"
    assert db_session.scalars(select(Trade)).all() == []
    event = db_session.scalar(select(SignalReviewEvent))
    assert event is not None
    assert event.signal_id == signal.id


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
    assert body["review_events"][0]["event_type"] == "review_note"
    assert body["review_events"][0]["note"] == body["review_note"]


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


def test_signal_detail_does_not_expose_other_users_review_history(
    client: TestClient, db_session: Session
) -> None:
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
        user_id=other_user.id,
        symbol="MSFT",
        asset_class=AssetClass.STOCK,
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

    response = client.get(f"/api/signals/{signal.id}")

    assert response.status_code == 404


def test_signal_detail_marks_old_active_review_signal_as_stale(
    client: TestClient, db_session: Session
) -> None:
    signal = create_signal(db_session, status=SignalStatus.ARMED)
    signal.updated_at = datetime.now(UTC) - timedelta(days=8)
    db_session.commit()
    login(client)

    response = client.get(f"/api/signals/{signal.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["is_stale"] is True
    assert body["stale_after_days"] == 7
    assert "Refresh with new CSV data" in body["stale_reason"]


def test_signal_detail_does_not_mark_terminal_old_signal_as_stale(
    client: TestClient, db_session: Session
) -> None:
    signal = create_signal(db_session, status=SignalStatus.INVALIDATED)
    signal.updated_at = datetime.now(UTC) - timedelta(days=30)
    db_session.commit()
    login(client)

    response = client.get(f"/api/signals/{signal.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["is_stale"] is False
    assert body["stale_reason"] is None


def test_signal_reads_include_trigger_proximity_from_stored_candle(
    client: TestClient, db_session: Session
) -> None:
    signal = create_signal(db_session, status=SignalStatus.ARMED)
    signal.trigger_level = Decimal("100")
    signal.timeframe_trigger = Timeframe.FOUR_HOURS
    create_trigger_candle(db_session, signal.watchlist_item_id, close="99.50", high="99.75")
    db_session.commit()
    login(client)

    list_response = client.get("/api/signals")
    detail_response = client.get(f"/api/signals/{signal.id}")

    assert list_response.status_code == 200
    assert list_response.json()[0]["trigger_proximity_state"] == "near_trigger"
    assert detail_response.status_code == 200
    assert detail_response.json()["trigger_proximity_state"] == "near_trigger"


def test_no_setup_signal_read_keeps_trigger_proximity_not_available(
    client: TestClient, db_session: Session
) -> None:
    signal = create_signal(db_session, status=SignalStatus.NO_SETUP)
    signal.trigger_level = Decimal("100")
    signal.timeframe_trigger = Timeframe.FOUR_HOURS
    signal.no_trade_reasons = ["required_timeframe_data_missing"]
    create_trigger_candle(db_session, signal.watchlist_item_id, close="101", high="102")
    db_session.commit()
    login(client)

    response = client.get(f"/api/signals/{signal.id}")

    assert response.status_code == 200
    assert response.json()["trigger_proximity_state"] == "not_available"


def create_trigger_candle(
    db: Session,
    watchlist_item_id: int,
    close: str,
    high: str,
) -> None:
    series = MarketDataSeries(
        watchlist_item_id=watchlist_item_id,
        source=MarketDataSource.TRADINGVIEW_CSV,
        timeframe=Timeframe.FOUR_HOURS,
        candle_count=1,
        status=MarketDataStatus.ANALYZED,
    )
    db.add(series)
    db.flush()
    db.add(
        MarketDataCandle(
            series_id=series.id,
            timestamp=datetime.now(UTC),
            open=Decimal(close),
            high=Decimal(high),
            low=Decimal("98"),
            close=Decimal(close),
            volume=Decimal("1000"),
        )
    )

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.enums import MarketDataStatus, ScoreClass, SignalStatus
from app.models.market_data import MarketDataCandle, MarketDataSeries
from app.models.signal import Signal, SignalReviewEvent
from app.strategies.contracts import SignalEvaluationResult

MANUAL_SIGNAL_STATUS_TRANSITIONS: dict[SignalStatus, set[SignalStatus]] = {
    SignalStatus.WATCHLIST: {
        SignalStatus.ARMED,
        SignalStatus.INVALIDATED,
        SignalStatus.EXPIRED,
    },
    SignalStatus.ARMED: {
        SignalStatus.INVALIDATED,
        SignalStatus.MISSED,
        SignalStatus.EXPIRED,
    },
    SignalStatus.TRIGGERED: {
        SignalStatus.INVALIDATED,
        SignalStatus.MISSED,
        SignalStatus.EXPIRED,
    },
}
STALE_SIGNAL_AFTER_DAYS = 7
STALE_SIGNAL_STATUSES = {
    SignalStatus.WATCHLIST,
    SignalStatus.ARMED,
    SignalStatus.TRIGGERED,
}
TERMINAL_SIGNAL_STATUSES = {
    SignalStatus.INVALIDATED,
    SignalStatus.MISSED,
    SignalStatus.EXPIRED,
}
NEAR_TRIGGER_DISTANCE_PCT = Decimal("0.01")


class InvalidSignalStatusTransitionError(Exception):
    pass


def is_signal_stale(signal: Signal, now: datetime | None = None) -> bool:
    if signal.status not in STALE_SIGNAL_STATUSES:
        return False

    reference = signal.updated_at or signal.created_at
    if reference is None:
        return False

    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=UTC)

    return (now or datetime.now(UTC)) - reference >= timedelta(days=STALE_SIGNAL_AFTER_DAYS)


def stale_signal_reason(signal: Signal) -> str | None:
    if not is_signal_stale(signal):
        return None
    return (
        "Signal is older than 7 days based on the last saved update. "
        "Refresh with new CSV data before treating it as current."
    )


def signal_trigger_proximity_state(db: Session, signal: Signal) -> str:
    if (
        signal.status == SignalStatus.NO_SETUP
        or signal.status in TERMINAL_SIGNAL_STATUSES
        or signal.score_class == ScoreClass.NO_TRADE
        or signal.no_trade_reasons
        or is_signal_stale(signal)
        or signal.trigger_level is None
        or signal.timeframe_trigger is None
    ):
        return "not_available"

    latest_candle = latest_trigger_candle(db, signal)
    if latest_candle is None:
        return "not_available"

    if latest_candle.close >= signal.trigger_level:
        return "at_trigger"
    if latest_candle.high >= signal.trigger_level:
        return "near_trigger"
    if signal.trigger_level <= 0:
        return "not_available"

    trigger_distance = (signal.trigger_level - latest_candle.close) / signal.trigger_level
    if Decimal("0") <= trigger_distance <= NEAR_TRIGGER_DISTANCE_PCT:
        return "near_trigger"
    return "far_from_trigger"


def latest_trigger_candle(db: Session, signal: Signal) -> MarketDataCandle | None:
    series = db.scalar(
        select(MarketDataSeries)
        .where(MarketDataSeries.watchlist_item_id == signal.watchlist_item_id)
        .where(MarketDataSeries.timeframe == signal.timeframe_trigger)
        .where(
            MarketDataSeries.status.in_(
                (MarketDataStatus.ANALYZED, MarketDataStatus.VALIDATED)
            )
        )
        .order_by(
            MarketDataSeries.end_time.desc(),
            MarketDataSeries.imported_at.desc(),
            MarketDataSeries.id.desc(),
        )
    )
    if series is None:
        return None

    return db.scalar(
        select(MarketDataCandle)
        .where(MarketDataCandle.series_id == series.id)
        .order_by(MarketDataCandle.timestamp.desc(), MarketDataCandle.id.desc())
    )


def list_signals(db: Session, user_id: int) -> list[Signal]:
    return list(
        db.scalars(
            select(Signal)
            .options(joinedload(Signal.watchlist_item))
            .options(selectinload(Signal.review_events))
            .where(Signal.user_id == user_id)
            .order_by(Signal.updated_at.desc(), Signal.id.desc())
        )
    )


def get_signal(db: Session, user_id: int, signal_id: int) -> Signal | None:
    signal = db.scalar(
        select(Signal)
        .options(joinedload(Signal.watchlist_item))
        .options(selectinload(Signal.review_events))
        .where(Signal.id == signal_id)
    )
    if signal is None or signal.user_id != user_id:
        return None
    return signal


def update_signal_status(
    db: Session,
    user_id: int,
    signal_id: int,
    target_status: SignalStatus,
) -> Signal | None:
    signal = get_signal(db, user_id, signal_id)
    if signal is None:
        return None

    allowed_targets = MANUAL_SIGNAL_STATUS_TRANSITIONS.get(signal.status, set())
    if target_status not in allowed_targets:
        raise InvalidSignalStatusTransitionError

    previous_status = signal.status
    signal.status = target_status
    if target_status == SignalStatus.INVALIDATED:
        signal.invalidated_at = datetime.now(UTC)
    db.add(
        SignalReviewEvent(
            signal_id=signal.id,
            user_id=user_id,
            event_type="status_change",
            previous_status=previous_status,
            new_status=target_status,
            note=None,
        )
    )
    db.commit()
    db.refresh(signal)
    return signal


def update_signal_review_note(
    db: Session,
    user_id: int,
    signal_id: int,
    review_note: str | None,
) -> Signal | None:
    signal = get_signal(db, user_id, signal_id)
    if signal is None:
        return None

    note = review_note.strip() if review_note is not None else ""
    signal.review_note = note or None
    db.add(
        SignalReviewEvent(
            signal_id=signal.id,
            user_id=user_id,
            event_type="review_note",
            previous_status=signal.status,
            new_status=signal.status,
            note=signal.review_note,
        )
    )
    db.commit()
    db.refresh(signal)
    return signal


def upsert_signal_from_analysis(
    db: Session,
    user_id: int,
    watchlist_item_id: int,
    result: SignalEvaluationResult,
) -> Signal:
    signal = db.scalar(
        select(Signal).where(
            Signal.user_id == user_id,
            Signal.watchlist_item_id == watchlist_item_id,
            Signal.strategy_type == result.strategy_type,
        )
    )
    if signal is None:
        signal = Signal(
            user_id=user_id,
            watchlist_item_id=watchlist_item_id,
            strategy_type=result.strategy_type,
        )
        db.add(signal)

    signal.status = result.status
    signal.bias = result.bias
    signal.score = result.score
    signal.score_class = result.score_class
    signal.timeframe_context = result.timeframe_context
    signal.timeframe_setup = result.timeframe_setup
    signal.timeframe_trigger = result.timeframe_trigger
    signal.entry_low = result.entry_low
    signal.entry_high = result.entry_high
    signal.trigger_level = result.trigger_level
    signal.stop_loss = result.stop_loss
    signal.target_1 = result.target_1
    signal.target_2 = result.target_2
    signal.risk_reward = result.risk_reward
    signal.invalidation_reason = result.invalidation_reason
    signal.reasoning = result.reasoning
    signal.risk_flags = result.risk_flags
    signal.no_trade_reasons = result.no_trade_reasons
    signal.next_action = result.next_action
    return signal

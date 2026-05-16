from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.signal import Signal
from app.strategies.contracts import SignalEvaluationResult


def list_signals(db: Session, user_id: int) -> list[Signal]:
    return list(
        db.scalars(
            select(Signal)
            .options(joinedload(Signal.watchlist_item))
            .where(Signal.user_id == user_id)
            .order_by(Signal.updated_at.desc(), Signal.id.desc())
        )
    )


def get_signal(db: Session, user_id: int, signal_id: int) -> Signal | None:
    signal = db.scalar(
        select(Signal)
        .options(joinedload(Signal.watchlist_item))
        .where(Signal.id == signal_id)
    )
    if signal is None or signal.user_id != user_id:
        return None
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

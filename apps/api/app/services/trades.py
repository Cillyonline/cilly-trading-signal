from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.enums import TradeEventType, TradeStatus
from app.models.signal import Signal
from app.models.trade import Trade, TradeEvent
from app.models.watchlist import WatchlistItem
from app.schemas.trades import TradeCreate, TradeEventCreate

TWO_PLACES = Decimal("0.01")
FOUR_PLACES = Decimal("0.0001")


class TradeCreationError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def create_trade(db: Session, user_id: int, payload: TradeCreate) -> Trade:
    signal = _get_signal(db, user_id, payload.signal_id) if payload.signal_id is not None else None
    if payload.signal_id is not None and signal is None:
        raise TradeCreationError("Signal not found.")

    watchlist_item_id = payload.watchlist_item_id
    if watchlist_item_id is None and signal is not None:
        watchlist_item_id = signal.watchlist_item_id
    if watchlist_item_id is None:
        raise TradeCreationError("watchlist_item_id or signal_id is required.")

    watchlist_item = db.scalar(
        select(WatchlistItem).where(
            WatchlistItem.id == watchlist_item_id,
            WatchlistItem.user_id == user_id,
        )
    )
    if watchlist_item is None:
        raise TradeCreationError("Watchlist item not found.")

    if signal is not None and signal.watchlist_item_id != watchlist_item.id:
        raise TradeCreationError("Signal does not belong to watchlist item.")

    strategy_type = payload.strategy_type
    if strategy_type is None and signal is not None:
        strategy_type = signal.strategy_type
    if strategy_type is None:
        raise TradeCreationError("strategy_type is required when no signal_id is provided.")

    risk_per_unit = payload.entry_price - payload.stop_loss
    initial_risk_amount = risk_per_unit * payload.position_size
    initial_risk_reward = None
    if payload.target_1 is not None:
        initial_risk_reward = (payload.target_1 - payload.entry_price) / risk_per_unit

    trade = Trade(
        user_id=user_id,
        signal_id=signal.id if signal else None,
        watchlist_item_id=watchlist_item.id,
        status=TradeStatus.OPEN,
        strategy_type=strategy_type,
        asset_class=watchlist_item.asset_class,
        symbol=watchlist_item.symbol,
        entry_price=payload.entry_price,
        stop_loss=payload.stop_loss,
        target_1=payload.target_1,
        target_2=payload.target_2,
        position_size=payload.position_size,
        fees=payload.fees,
        opened_at=payload.opened_at,
        initial_risk_amount=_quantize(initial_risk_amount, TWO_PLACES),
        initial_risk_percent=None,
        initial_risk_reward=_quantize(initial_risk_reward, TWO_PLACES),
        notes=payload.notes,
    )
    db.add(trade)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise TradeCreationError("Trade already exists for signal.") from error

    db.refresh(trade)
    return trade


def list_trades(db: Session, user_id: int) -> list[Trade]:
    return list(
        db.scalars(
            select(Trade)
            .where(Trade.user_id == user_id)
            .order_by(Trade.opened_at.desc(), Trade.id.desc())
        )
    )


def get_trade(db: Session, user_id: int, trade_id: int) -> Trade | None:
    trade = db.scalar(
        select(Trade)
        .options(selectinload(Trade.events))
        .where(Trade.id == trade_id, Trade.user_id == user_id)
    )
    if trade is not None:
        trade.events.sort(key=lambda event: (event.event_time, event.id))
    return trade


def create_trade_event(
    db: Session,
    user_id: int,
    trade_id: int,
    payload: TradeEventCreate,
) -> TradeEvent:
    trade = get_trade(db, user_id, trade_id)
    if trade is None:
        raise TradeCreationError("Trade not found.")

    old_value = None
    new_value = None
    if payload.event_type == TradeEventType.STOP_UPDATED:
        old_value = str(trade.stop_loss)
        new_value = str(payload.price)
        trade.stop_loss = payload.price
    elif payload.event_type == TradeEventType.TARGET_UPDATED:
        target_field = payload.reason
        old_target = getattr(trade, target_field)
        old_value = str(old_target) if old_target is not None else None
        new_value = str(payload.price)
        setattr(trade, target_field, payload.price)

    event = TradeEvent(
        trade_id=trade.id,
        event_type=payload.event_type,
        event_time=payload.event_time,
        price=payload.price,
        quantity=None,
        old_value=old_value,
        new_value=new_value,
        reason=payload.reason,
        notes=payload.notes,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def _get_signal(db: Session, user_id: int, signal_id: int) -> Signal | None:
    return db.scalar(
        select(Signal)
        .options(joinedload(Signal.watchlist_item))
        .where(Signal.id == signal_id, Signal.user_id == user_id)
    )


def _quantize(value: Decimal | None, exponent: Decimal) -> Decimal | None:
    if value is None:
        return None
    return value.quantize(exponent, rounding=ROUND_HALF_UP)

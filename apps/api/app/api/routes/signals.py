from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.signals import SignalRead, SignalStatusUpdate
from app.services.signals import (
    InvalidSignalStatusTransitionError,
    get_signal,
    list_signals,
    update_signal_status,
)

router = APIRouter(prefix="/signals", tags=["signals"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=list[SignalRead])
def list_items(db: DbSession, user: CurrentUser) -> list[SignalRead]:
    return [to_signal_read(signal) for signal in list_signals(db, user.id)]


@router.get("/{signal_id}", response_model=SignalRead)
def get_item(signal_id: int, db: DbSession, user: CurrentUser) -> SignalRead:
    signal = get_signal(db, user.id, signal_id)
    if signal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signal not found.",
        )
    return to_signal_read(signal)


@router.patch("/{signal_id}/status", response_model=SignalRead)
def update_item_status(
    signal_id: int, payload: SignalStatusUpdate, db: DbSession, user: CurrentUser
) -> SignalRead:
    try:
        signal = update_signal_status(db, user.id, signal_id, payload.status)
    except InvalidSignalStatusTransitionError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Signal status transition is not allowed.",
        ) from error

    if signal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signal not found.",
        )
    return to_signal_read(signal)


def to_signal_read(signal) -> SignalRead:
    return SignalRead.model_validate(
        {
            **signal.__dict__,
            "symbol": signal.watchlist_item.symbol,
            "asset_class": signal.watchlist_item.asset_class,
            "exchange": signal.watchlist_item.exchange,
        }
    )

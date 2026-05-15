from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.trades import (
    TradeClose,
    TradeCreate,
    TradeDetailRead,
    TradeEventCreate,
    TradeEventRead,
    TradeRead,
)
from app.services.trades import (
    TradeCloseError,
    TradeCreationError,
    close_trade,
    create_trade,
    create_trade_event,
    get_trade,
    list_trades,
)
from app.services.watchlist import get_or_create_default_user

router = APIRouter(prefix="/trades", tags=["trades"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[TradeRead])
def list_items(db: DbSession) -> list[TradeRead]:
    user = get_or_create_default_user(db)
    return list_trades(db, user.id)


@router.get("/{trade_id}", response_model=TradeDetailRead)
def get_item(trade_id: int, db: DbSession) -> TradeDetailRead:
    user = get_or_create_default_user(db)
    trade = get_trade(db, user.id, trade_id)
    if trade is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found.",
        )
    return trade


@router.post("", response_model=TradeRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: TradeCreate, db: DbSession) -> TradeRead:
    user = get_or_create_default_user(db)
    try:
        return create_trade(db, user.id, payload)
    except TradeCreationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.message,
        ) from error


@router.post(
    "/{trade_id}/events",
    response_model=TradeEventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_event(trade_id: int, payload: TradeEventCreate, db: DbSession) -> TradeEventRead:
    user = get_or_create_default_user(db)
    try:
        return create_trade_event(db, user.id, trade_id, payload)
    except TradeCreationError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.message,
        ) from error


@router.post("/{trade_id}/close", response_model=TradeDetailRead)
def close_item(trade_id: int, payload: TradeClose, db: DbSession) -> TradeDetailRead:
    user = get_or_create_default_user(db)
    try:
        return close_trade(db, user.id, trade_id, payload)
    except TradeCloseError as error:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if error.message == "Trade not found."
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(
            status_code=status_code,
            detail=error.message,
        ) from error

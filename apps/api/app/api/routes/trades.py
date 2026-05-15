from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.trades import (
    JournalEntryCreate,
    JournalEntryRead,
    TradeClose,
    TradeCreate,
    TradeDetailRead,
    TradeEventCreate,
    TradeEventRead,
    TradeRead,
)
from app.services.trades import (
    JournalEntryError,
    TradeCloseError,
    TradeCreationError,
    close_trade,
    create_journal_entry,
    create_trade,
    create_trade_event,
    get_trade,
    list_trades,
)

router = APIRouter(prefix="/trades", tags=["trades"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=list[TradeRead])
def list_items(db: DbSession, user: CurrentUser) -> list[TradeRead]:
    return list_trades(db, user.id)


@router.get("/{trade_id}", response_model=TradeDetailRead)
def get_item(trade_id: int, db: DbSession, user: CurrentUser) -> TradeDetailRead:
    trade = get_trade(db, user.id, trade_id)
    if trade is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found.",
        )
    return trade


@router.post("", response_model=TradeRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: TradeCreate, db: DbSession, user: CurrentUser) -> TradeRead:
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
def create_event(
    trade_id: int,
    payload: TradeEventCreate,
    db: DbSession,
    user: CurrentUser,
) -> TradeEventRead:
    try:
        return create_trade_event(db, user.id, trade_id, payload)
    except TradeCreationError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.message,
        ) from error


@router.post("/{trade_id}/close", response_model=TradeDetailRead)
def close_item(
    trade_id: int,
    payload: TradeClose,
    db: DbSession,
    user: CurrentUser,
) -> TradeDetailRead:
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


@router.post(
    "/{trade_id}/journal",
    response_model=JournalEntryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_journal(
    trade_id: int,
    payload: JournalEntryCreate,
    db: DbSession,
    user: CurrentUser,
) -> JournalEntryRead:
    try:
        return create_journal_entry(db, user.id, trade_id, payload)
    except JournalEntryError as error:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if error.message == "Trade not found."
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(
            status_code=status_code,
            detail=error.message,
        ) from error

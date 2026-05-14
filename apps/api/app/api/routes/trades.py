from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.trades import TradeCreate, TradeRead
from app.services.trades import TradeCreationError, create_trade, list_trades
from app.services.watchlist import get_or_create_default_user

router = APIRouter(prefix="/trades", tags=["trades"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[TradeRead])
def list_items(db: DbSession) -> list[TradeRead]:
    user = get_or_create_default_user(db)
    return list_trades(db, user.id)


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

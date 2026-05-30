from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.watchlist import (
    BenchmarkContextStatusRead,
    WatchlistItemCreate,
    WatchlistItemRead,
    WatchlistItemUpdate,
)
from app.services.market_context import benchmark_context_status
from app.services.watchlist import (
    DuplicateWatchlistSymbolError,
    create_watchlist_item,
    get_watchlist_item,
    list_watchlist_items,
    update_watchlist_item,
)

router = APIRouter(prefix="/watchlist", tags=["watchlist"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=list[WatchlistItemRead])
def list_items(db: DbSession, user: CurrentUser) -> list[WatchlistItemRead]:
    return [WatchlistItemRead.model_validate(item) for item in list_watchlist_items(db, user.id)]


@router.get("/benchmark-context", response_model=list[BenchmarkContextStatusRead])
def get_benchmark_context(db: DbSession, user: CurrentUser) -> list[BenchmarkContextStatusRead]:
    return [
        BenchmarkContextStatusRead.model_validate(status)
        for status in benchmark_context_status(db, user.id)
    ]


@router.post("", response_model=WatchlistItemRead, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: WatchlistItemCreate, db: DbSession, user: CurrentUser
) -> WatchlistItemRead:
    try:
        return WatchlistItemRead.model_validate(create_watchlist_item(db, user.id, payload))
    except DuplicateWatchlistSymbolError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Symbol already exists in watchlist.",
        ) from error


@router.get("/{item_id}", response_model=WatchlistItemRead)
def get_item(item_id: int, db: DbSession, user: CurrentUser) -> WatchlistItemRead:
    item = get_watchlist_item(db, user.id, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist item not found.",
        )
    return WatchlistItemRead.model_validate(item)


@router.patch("/{item_id}", response_model=WatchlistItemRead)
def update_item(
    item_id: int, payload: WatchlistItemUpdate, db: DbSession, user: CurrentUser
) -> WatchlistItemRead:
    item = get_watchlist_item(db, user.id, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist item not found.",
        )

    try:
        return WatchlistItemRead.model_validate(update_watchlist_item(db, item, payload))
    except DuplicateWatchlistSymbolError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Symbol already exists in watchlist.",
        ) from error


@router.delete("/{item_id}", response_model=WatchlistItemRead)
def deactivate_item(item_id: int, db: DbSession, user: CurrentUser) -> WatchlistItemRead:
    item = get_watchlist_item(db, user.id, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist item not found.",
        )

    return WatchlistItemRead.model_validate(
        update_watchlist_item(db, item, WatchlistItemUpdate(is_active=False))
    )

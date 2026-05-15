from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.enums import UserRole
from app.models.user import User
from app.models.watchlist import WatchlistItem
from app.schemas.watchlist import WatchlistItemCreate, WatchlistItemUpdate

DEFAULT_USER_EMAIL = "local-admin@example.com"


class DuplicateWatchlistSymbolError(Exception):
    pass


def get_or_create_default_user(db: Session) -> User:
    if settings.environment not in {"development", "test"}:
        raise RuntimeError("Default local user bridge is disabled outside development/test.")

    user = db.scalar(select(User).where(User.email == DEFAULT_USER_EMAIL))
    if user is not None:
        return user

    user = User(
        email=DEFAULT_USER_EMAIL,
        password_hash="not-used-before-auth",
        display_name="Local Admin",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_watchlist_items(db: Session, user_id: int) -> list[WatchlistItem]:
    return list(
        db.scalars(
            select(WatchlistItem)
            .where(WatchlistItem.user_id == user_id)
            .order_by(WatchlistItem.symbol)
        )
    )


def get_watchlist_item(db: Session, user_id: int, item_id: int) -> WatchlistItem | None:
    return db.scalar(
        select(WatchlistItem).where(
            WatchlistItem.id == item_id,
            WatchlistItem.user_id == user_id,
        )
    )


def create_watchlist_item(
    db: Session, user_id: int, payload: WatchlistItemCreate
) -> WatchlistItem:
    item = WatchlistItem(user_id=user_id, **payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise DuplicateWatchlistSymbolError from error
    db.refresh(item)
    return item


def update_watchlist_item(
    db: Session, item: WatchlistItem, payload: WatchlistItemUpdate
) -> WatchlistItem:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise DuplicateWatchlistSymbolError from error
    db.refresh(item)
    return item

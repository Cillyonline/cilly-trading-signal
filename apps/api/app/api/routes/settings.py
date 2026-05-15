from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.settings import SettingsRead, SettingsUpdate
from app.services.settings import get_or_create_settings, update_settings

router = APIRouter(prefix="/settings", tags=["settings"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=SettingsRead)
def get_item(db: DbSession, user: CurrentUser) -> SettingsRead:
    return get_or_create_settings(db, user.id)


@router.patch("", response_model=SettingsRead)
def update_item(payload: SettingsUpdate, db: DbSession, user: CurrentUser) -> SettingsRead:
    return update_settings(db, user.id, payload)

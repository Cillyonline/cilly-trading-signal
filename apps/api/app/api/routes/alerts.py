from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.alert import Alert
from app.models.user import User
from app.schemas.alerts import AlertRead, TelegramTestMessageResult
from app.services.notifications import (
    TelegramConfigurationError,
    TelegramDeliveryError,
    send_telegram_test_message,
)

router = APIRouter(prefix="/alerts", tags=["alerts"])
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[AlertRead])
def list_alerts(current_user: CurrentUser, db: DbSession) -> list[Alert]:
    return list(
        db.scalars(
            select(Alert)
            .where(Alert.user_id == current_user.id)
            .order_by(desc(Alert.created_at), desc(Alert.id))
            .limit(100)
        )
    )


@router.post("/test-telegram", response_model=TelegramTestMessageResult)
def test_telegram(current_user: CurrentUser) -> TelegramTestMessageResult:
    try:
        send_telegram_test_message()
    except TelegramConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram is not configured.",
        ) from error
    except TelegramDeliveryError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Telegram test message could not be delivered.",
        ) from error

    return TelegramTestMessageResult(
        status="sent",
        message="Telegram test message sent.",
    )

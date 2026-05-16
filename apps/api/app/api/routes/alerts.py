from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.alerts import TelegramTestMessageResult
from app.services.notifications import (
    TelegramConfigurationError,
    TelegramDeliveryError,
    send_telegram_test_message,
)

router = APIRouter(prefix="/alerts", tags=["alerts"])
CurrentUser = Annotated[User, Depends(get_current_user)]


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

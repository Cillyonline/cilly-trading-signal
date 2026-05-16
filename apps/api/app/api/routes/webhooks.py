from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.alerts import TradingViewWebhookPayload, TradingViewWebhookResult
from app.services.alerts import (
    InvalidWebhookSecretError,
    UnsupportedWebhookTriggerError,
    ingest_tradingview_webhook,
)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/tradingview",
    response_model=TradingViewWebhookResult,
    status_code=status.HTTP_202_ACCEPTED,
)
def tradingview_webhook(
    payload: TradingViewWebhookPayload, db: DbSession
) -> TradingViewWebhookResult:
    try:
        alert = ingest_tradingview_webhook(db, payload)
    except InvalidWebhookSecretError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret.",
        ) from error
    except UnsupportedWebhookTriggerError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported TradingView trigger.",
        ) from error

    return TradingViewWebhookResult(
        alert_id=alert.id,
        status=alert.status,
        delivery_status=alert.delivery_status,
        message="TradingView webhook accepted for manual review.",
    )

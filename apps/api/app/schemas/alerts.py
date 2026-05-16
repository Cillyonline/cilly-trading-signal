from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.enums import (
    AlertDeliveryStatus,
    AlertSource,
    AlertStatus,
    AlertType,
    NotificationChannel,
    Timeframe,
)


class AlertRead(BaseModel):
    id: int
    user_id: int
    signal_id: int | None
    trade_id: int | None
    watchlist_item_id: int | None
    alert_type: AlertType
    status: AlertStatus
    source: AlertSource
    priority: str
    trigger_level: Decimal | None
    timeframe: Timeframe | None
    message: str | None
    source_payload: dict | list | None
    delivery_status: AlertDeliveryStatus
    delivery_error: str | None
    last_triggered_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NotificationLogRead(BaseModel):
    id: int
    user_id: int
    alert_id: int | None
    channel: NotificationChannel
    recipient: str | None
    message: str
    status: AlertDeliveryStatus
    error_message: str | None
    provider_payload: dict | list | None
    sent_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}

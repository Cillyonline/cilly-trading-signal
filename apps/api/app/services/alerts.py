from secrets import compare_digest

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.alert import Alert
from app.models.enums import AlertDeliveryStatus, AlertSource, AlertStatus, AlertType
from app.schemas.alerts import TradingViewWebhookPayload
from app.services.auth import get_or_create_admin_user

TRADINGVIEW_TRIGGER_TYPES = {
    "info": AlertType.INFO,
    "watchlist": AlertType.WATCHLIST,
    "armed": AlertType.ARMED,
    "near_trigger": AlertType.NEAR_TRIGGER,
    "entry_trigger": AlertType.ENTRY_TRIGGER,
    "long_entry": AlertType.ENTRY_TRIGGER,
    "management": AlertType.MANAGEMENT,
    "exit_warning": AlertType.EXIT_WARNING,
    "exit_signal": AlertType.EXIT_SIGNAL,
    "invalidation": AlertType.INVALIDATION,
}


class InvalidWebhookSecretError(Exception):
    pass


class UnsupportedWebhookTriggerError(Exception):
    pass


def ingest_tradingview_webhook(db: Session, payload: TradingViewWebhookPayload) -> Alert:
    if not compare_digest(payload.secret, settings.tradingview_webhook_secret):
        raise InvalidWebhookSecretError

    alert_type = TRADINGVIEW_TRIGGER_TYPES.get(payload.trigger.strip().lower())
    if alert_type is None:
        raise UnsupportedWebhookTriggerError

    user = get_or_create_admin_user(db)
    source_payload = payload.model_dump(mode="json", exclude={"secret"})
    alert = Alert(
        user_id=user.id,
        alert_type=alert_type,
        status=AlertStatus.TRIGGERED,
        source=AlertSource.TRADINGVIEW_WEBHOOK,
        priority="p1" if alert_type == AlertType.ENTRY_TRIGGER else "p2",
        trigger_level=payload.price,
        timeframe=payload.timeframe,
        message=f"TradingView webhook received for {payload.symbol}: {payload.trigger}",
        source_payload=source_payload,
        delivery_status=AlertDeliveryStatus.PENDING,
        last_triggered_at=payload.time,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert

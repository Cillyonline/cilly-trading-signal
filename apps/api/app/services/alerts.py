from datetime import UTC, datetime
from secrets import compare_digest

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.alert import Alert, NotificationLog
from app.models.enums import (
    AlertDeliveryStatus,
    AlertSource,
    AlertStatus,
    AlertType,
    NotificationChannel,
)
from app.schemas.alerts import TradingViewWebhookPayload
from app.services.auth import get_or_create_admin_user
from app.services.notifications import (
    TelegramConfigurationError,
    TelegramDeliveryError,
    send_telegram_message,
)

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

TELEGRAM_ROUTED_ALERT_TYPES = {
    AlertType.NEAR_TRIGGER,
    AlertType.ENTRY_TRIGGER,
    AlertType.INVALIDATION,
    AlertType.EXIT_WARNING,
}

TELEGRAM_MANUAL_REVIEW_NOTICE = (
    "Manual review required. Keine automatische Order. "
    "Keine Kauf- oder Verkaufsanweisung."
)


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
    route_telegram_delivery_for_alert(db, alert, payload)
    db.refresh(alert)
    return alert


def route_telegram_delivery_for_alert(
    db: Session,
    alert: Alert,
    payload: TradingViewWebhookPayload,
) -> None:
    if not settings.telegram_alert_routing_enabled:
        _mark_alert_delivery_skipped(db, alert, "Telegram alert routing is disabled.")
        return

    if alert.alert_type not in TELEGRAM_ROUTED_ALERT_TYPES:
        _mark_alert_delivery_skipped(db, alert, "Alert type is manual-review only.")
        return

    message = build_telegram_alert_message(alert, payload)
    notification = NotificationLog(
        user_id=alert.user_id,
        alert_id=alert.id,
        channel=NotificationChannel.TELEGRAM,
        recipient=settings.telegram_chat_id,
        message=message,
        status=AlertDeliveryStatus.PENDING,
        provider_payload={"source": "tradingview_webhook", "policy": "v1.3"},
    )
    db.add(notification)
    db.flush()

    try:
        send_telegram_message(message)
    except (TelegramConfigurationError, TelegramDeliveryError) as error:
        error_message = error.__class__.__name__
        alert.delivery_status = AlertDeliveryStatus.FAILED
        alert.delivery_error = error_message
        notification.status = AlertDeliveryStatus.FAILED
        notification.error_message = error_message
    else:
        alert.delivery_status = AlertDeliveryStatus.SENT
        alert.delivery_error = None
        notification.status = AlertDeliveryStatus.SENT
        notification.sent_at = datetime.now(UTC)

    db.commit()


def build_telegram_alert_message(alert: Alert, payload: TradingViewWebhookPayload) -> str:
    return "\n".join(
        [
            f"{alert.priority.upper()} / {alert.alert_type.value} / {payload.symbol}",
            f"Timeframe: {payload.timeframe.value}",
            f"Trigger price: {payload.price}",
            f"Triggered at: {payload.time.isoformat()}",
            "Next step: setup, risk, context and execution plan manually reviewen.",
            TELEGRAM_MANUAL_REVIEW_NOTICE,
        ]
    )


def _mark_alert_delivery_skipped(db: Session, alert: Alert, reason: str) -> None:
    alert.delivery_status = AlertDeliveryStatus.SKIPPED
    alert.delivery_error = reason
    db.commit()

from datetime import UTC, datetime, timedelta
from secrets import compare_digest

from sqlalchemy import desc, select
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
TELEGRAM_DEDUP_WINDOW = timedelta(minutes=30)
TELEGRAM_BURST_WINDOW = timedelta(minutes=5)
TELEGRAM_BURST_LIMIT = 10
TELEGRAM_DELIVERY_BLOCKING_STATUSES = {
    AlertDeliveryStatus.PENDING,
    AlertDeliveryStatus.SENT,
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

    now = utc_now()
    dedup_key = build_telegram_dedup_key(alert, payload)
    if has_recent_telegram_delivery(db, alert.user_id, dedup_key, now):
        _mark_alert_delivery_skipped(
            db,
            alert,
            "Telegram alert deduplicated within 30 minutes.",
        )
        return
    if has_recent_telegram_burst(db, alert.user_id, now):
        _mark_alert_delivery_skipped(
            db,
            alert,
            "Telegram alert rate limit reached.",
        )
        return

    message = build_telegram_alert_message(alert, payload)
    notification = NotificationLog(
        user_id=alert.user_id,
        alert_id=alert.id,
        channel=NotificationChannel.TELEGRAM,
        recipient=settings.telegram_chat_id,
        message=message,
        status=AlertDeliveryStatus.PENDING,
        provider_payload={
            "source": "tradingview_webhook",
            "policy": "v1.3",
            "dedup_key": dedup_key,
        },
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
        notification.sent_at = now

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


def build_telegram_dedup_key(alert: Alert, payload: TradingViewWebhookPayload) -> str:
    return ":".join(
        [
            payload.symbol.strip().upper(),
            alert.alert_type.value,
            payload.timeframe.value,
        ]
    )


def has_recent_telegram_delivery(
    db: Session,
    user_id: int,
    dedup_key: str,
    now: datetime,
) -> bool:
    cutoff = now - TELEGRAM_DEDUP_WINDOW
    recent_logs = _recent_telegram_logs(db, user_id, cutoff)
    return any(
        log.status in TELEGRAM_DELIVERY_BLOCKING_STATUSES
        and isinstance(log.provider_payload, dict)
        and log.provider_payload.get("dedup_key") == dedup_key
        for log in recent_logs
    )


def has_recent_telegram_burst(db: Session, user_id: int, now: datetime) -> bool:
    cutoff = now - TELEGRAM_BURST_WINDOW
    recent_logs = _recent_telegram_logs(db, user_id, cutoff)
    sent_or_pending_count = sum(
        1 for log in recent_logs if log.status in TELEGRAM_DELIVERY_BLOCKING_STATUSES
    )
    return sent_or_pending_count >= TELEGRAM_BURST_LIMIT


def _recent_telegram_logs(
    db: Session,
    user_id: int,
    cutoff: datetime,
) -> list[NotificationLog]:
    return list(
        db.scalars(
            select(NotificationLog)
            .where(
                NotificationLog.user_id == user_id,
                NotificationLog.channel == NotificationChannel.TELEGRAM,
                NotificationLog.created_at >= cutoff,
            )
            .order_by(desc(NotificationLog.created_at), desc(NotificationLog.id))
            .limit(100)
        )
    )


def utc_now() -> datetime:
    return datetime.now(UTC)


def _mark_alert_delivery_skipped(db: Session, alert: Alert, reason: str) -> None:
    alert.delivery_status = AlertDeliveryStatus.SKIPPED
    alert.delivery_error = reason
    db.commit()

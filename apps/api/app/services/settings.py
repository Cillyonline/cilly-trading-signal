from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.settings import Settings
from app.schemas.settings import SettingsUpdate


DEFAULT_RISK_PERCENT = Decimal("1.00")
DEFAULT_MAX_RISK_PERCENT = Decimal("1.00")
DEFAULT_MIN_RISK_REWARD = Decimal("2.00")
DEFAULT_MAX_OPEN_TRADES = 5
DEFAULT_BASE_CURRENCY = "EUR"


def get_or_create_settings(db: Session, user_id: int) -> Settings:
    settings = db.scalar(select(Settings).where(Settings.user_id == user_id))
    if settings is not None:
        return settings

    settings = Settings(
        user_id=user_id,
        account_size=None,
        default_risk_percent=DEFAULT_RISK_PERCENT,
        max_risk_percent=DEFAULT_MAX_RISK_PERCENT,
        min_risk_reward=DEFAULT_MIN_RISK_REWARD,
        max_open_trades=DEFAULT_MAX_OPEN_TRADES,
        base_currency=DEFAULT_BASE_CURRENCY,
        telegram_enabled=False,
        telegram_chat_id=None,
        tradingview_webhook_secret=None,
    )
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def update_settings(db: Session, user_id: int, payload: SettingsUpdate) -> Settings:
    settings = get_or_create_settings(db, user_id)
    update_data = payload.model_dump(exclude_unset=True)
    for field_name in [
        "default_risk_percent",
        "max_risk_percent",
        "min_risk_reward",
        "max_open_trades",
        "base_currency",
    ]:
        if update_data.get(field_name) is None:
            update_data.pop(field_name, None)
    if "base_currency" in update_data and update_data["base_currency"] is not None:
        update_data["base_currency"] = update_data["base_currency"].upper()
    for field_name, value in update_data.items():
        setattr(settings, field_name, value)
    db.commit()
    db.refresh(settings)
    return settings

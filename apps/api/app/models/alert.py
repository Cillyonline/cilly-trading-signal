from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, JSON, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import (
    AlertDeliveryStatus,
    AlertSource,
    AlertStatus,
    AlertType,
    NotificationChannel,
    Timeframe,
)
from app.models.types import enum_values

if TYPE_CHECKING:
    from app.models.signal import Signal
    from app.models.trade import Trade
    from app.models.user import User
    from app.models.watchlist import WatchlistItem


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    signal_id: Mapped[int | None] = mapped_column(ForeignKey("signals.id"), index=True)
    trade_id: Mapped[int | None] = mapped_column(ForeignKey("trades.id"), index=True)
    watchlist_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("watchlist_items.id"), index=True
    )
    alert_type: Mapped[AlertType] = mapped_column(enum_values(AlertType))
    status: Mapped[AlertStatus] = mapped_column(
        enum_values(AlertStatus), default=AlertStatus.ACTIVE
    )
    source: Mapped[AlertSource] = mapped_column(
        enum_values(AlertSource), default=AlertSource.SYSTEM
    )
    priority: Mapped[str] = mapped_column(String(16), default="p2")
    trigger_level: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    timeframe: Mapped[Timeframe | None] = mapped_column(enum_values(Timeframe))
    message: Mapped[str | None] = mapped_column(Text)
    source_payload: Mapped[dict | list | None] = mapped_column(JSON)
    delivery_status: Mapped[AlertDeliveryStatus] = mapped_column(
        enum_values(AlertDeliveryStatus), default=AlertDeliveryStatus.PENDING
    )
    delivery_error: Mapped[str | None] = mapped_column(Text)
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="alerts")
    signal: Mapped["Signal | None"] = relationship(back_populates="alerts")
    trade: Mapped["Trade | None"] = relationship(back_populates="alerts")
    watchlist_item: Mapped["WatchlistItem | None"] = relationship(back_populates="alerts")
    notifications: Mapped[list["NotificationLog"]] = relationship(back_populates="alert")


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    alert_id: Mapped[int | None] = mapped_column(ForeignKey("alerts.id"), index=True)
    channel: Mapped[NotificationChannel] = mapped_column(enum_values(NotificationChannel))
    recipient: Mapped[str | None] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[AlertDeliveryStatus] = mapped_column(enum_values(AlertDeliveryStatus))
    error_message: Mapped[str | None] = mapped_column(Text)
    provider_payload: Mapped[dict | list | None] = mapped_column(JSON)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="notification_logs")
    alert: Mapped["Alert | None"] = relationship(back_populates="notifications")

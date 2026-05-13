from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    account_size: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    default_risk_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("1.00"))
    max_risk_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("1.00"))
    min_risk_reward: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=Decimal("2.00"))
    max_open_trades: Mapped[int] = mapped_column(default=5)
    base_currency: Mapped[str] = mapped_column(String(3), default="EUR")
    telegram_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(255))
    tradingview_webhook_secret: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="settings")

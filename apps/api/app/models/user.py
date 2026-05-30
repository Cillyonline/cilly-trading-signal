from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import UserRole
from app.models.types import enum_values

if TYPE_CHECKING:
    from app.models.alert import Alert, NotificationLog
    from app.models.screener import ScreenerImport, ScreenerResult
    from app.models.settings import Settings
    from app.models.signal import Signal, SignalReviewEvent
    from app.models.trade import JournalEntry, Trade
    from app.models.watchlist import WatchlistItem


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(enum_values(UserRole), default=UserRole.ADMIN)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    settings: Mapped["Settings"] = relationship(back_populates="user")
    watchlist_items: Mapped[list["WatchlistItem"]] = relationship(back_populates="user")
    signals: Mapped[list["Signal"]] = relationship(back_populates="user")
    signal_review_events: Mapped[list["SignalReviewEvent"]] = relationship(back_populates="user")
    trades: Mapped[list["Trade"]] = relationship(back_populates="user")
    journal_entries: Mapped[list["JournalEntry"]] = relationship(back_populates="user")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="user")
    notification_logs: Mapped[list["NotificationLog"]] = relationship(back_populates="user")
    screener_imports: Mapped[list["ScreenerImport"]] = relationship(back_populates="user")
    screener_results: Mapped[list["ScreenerResult"]] = relationship(back_populates="user")

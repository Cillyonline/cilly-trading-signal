from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AssetClass, ExitReason, StrategyType, TradeEventType, TradeStatus
from app.models.types import enum_values

if TYPE_CHECKING:
    from app.models.signal import Signal
    from app.models.user import User
    from app.models.watchlist import WatchlistItem


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    signal_id: Mapped[int | None] = mapped_column(ForeignKey("signals.id"), unique=True)
    watchlist_item_id: Mapped[int] = mapped_column(ForeignKey("watchlist_items.id"), index=True)
    status: Mapped[TradeStatus] = mapped_column(enum_values(TradeStatus), default=TradeStatus.OPEN)
    strategy_type: Mapped[StrategyType] = mapped_column(enum_values(StrategyType))
    asset_class: Mapped[AssetClass] = mapped_column(enum_values(AssetClass))
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    entry_price: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    stop_loss: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    target_1: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    target_2: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    position_size: Mapped[Decimal] = mapped_column(Numeric(24, 8))
    fees: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    exit_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    exit_reason: Mapped[ExitReason | None] = mapped_column(enum_values(ExitReason))
    initial_risk_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    initial_risk_percent: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    initial_risk_reward: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    result_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    result_r: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="trades")
    signal: Mapped["Signal | None"] = relationship(back_populates="trade")
    watchlist_item: Mapped["WatchlistItem"] = relationship(back_populates="trades")
    events: Mapped[list["TradeEvent"]] = relationship(back_populates="trade")
    journal_entry: Mapped["JournalEntry"] = relationship(back_populates="trade")


class TradeEvent(Base):
    __tablename__ = "trade_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    trade_id: Mapped[int] = mapped_column(ForeignKey("trades.id"), index=True)
    event_type: Mapped[TradeEventType] = mapped_column(enum_values(TradeEventType))
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    price: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(24, 8))
    old_value: Mapped[str | None] = mapped_column(String(255))
    new_value: Mapped[str | None] = mapped_column(String(255))
    reason: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    trade: Mapped[Trade] = relationship(back_populates="events")


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    trade_id: Mapped[int] = mapped_column(ForeignKey("trades.id"), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    setup_rule_followed: Mapped[bool | None] = mapped_column(Boolean)
    entry_quality_score: Mapped[int | None] = mapped_column(Integer)
    stop_quality_score: Mapped[int | None] = mapped_column(Integer)
    exit_quality_score: Mapped[int | None] = mapped_column(Integer)
    discipline_score: Mapped[int | None] = mapped_column(Integer)
    market_context: Mapped[str | None] = mapped_column(Text)
    emotional_notes: Mapped[str | None] = mapped_column(Text)
    what_went_well: Mapped[str | None] = mapped_column(Text)
    what_went_wrong: Mapped[str | None] = mapped_column(Text)
    lesson_learned: Mapped[str | None] = mapped_column(Text)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    trade: Mapped[Trade] = relationship(back_populates="journal_entry")
    user: Mapped["User"] = relationship(back_populates="journal_entries")

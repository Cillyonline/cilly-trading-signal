from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import Bias, ScoreClass, SignalStatus, StrategyType, Timeframe
from app.models.types import enum_values

if TYPE_CHECKING:
    from app.models.trade import Trade
    from app.models.user import User
    from app.models.watchlist import WatchlistItem


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    watchlist_item_id: Mapped[int] = mapped_column(ForeignKey("watchlist_items.id"), index=True)
    strategy_type: Mapped[StrategyType] = mapped_column(enum_values(StrategyType))
    status: Mapped[SignalStatus] = mapped_column(
        enum_values(SignalStatus), default=SignalStatus.WATCHLIST
    )
    bias: Mapped[Bias] = mapped_column(enum_values(Bias), default=Bias.NEUTRAL)
    score: Mapped[int | None] = mapped_column(Integer)
    score_class: Mapped[ScoreClass | None] = mapped_column(enum_values(ScoreClass))
    timeframe_context: Mapped[Timeframe | None] = mapped_column(enum_values(Timeframe))
    timeframe_setup: Mapped[Timeframe | None] = mapped_column(enum_values(Timeframe))
    timeframe_trigger: Mapped[Timeframe | None] = mapped_column(enum_values(Timeframe))
    entry_low: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    entry_high: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    trigger_level: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    stop_loss: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    target_1: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    target_2: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    risk_reward: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    invalidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    invalidation_reason: Mapped[str | None] = mapped_column(Text)
    reasoning: Mapped[dict | list | None] = mapped_column(JSON)
    risk_flags: Mapped[dict | list | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="signals")
    watchlist_item: Mapped["WatchlistItem"] = relationship(back_populates="signals")
    trade: Mapped["Trade"] = relationship(back_populates="signal")

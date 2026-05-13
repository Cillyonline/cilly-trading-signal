from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AssetClass
from app.models.types import enum_values

if TYPE_CHECKING:
    from app.models.market_data import MarketDataSeries
    from app.models.signal import Signal
    from app.models.trade import Trade
    from app.models.user import User


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    __table_args__ = (UniqueConstraint("user_id", "symbol", name="uq_watchlist_items_user_symbol"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    asset_class: Mapped[AssetClass] = mapped_column(enum_values(AssetClass))
    exchange: Mapped[str | None] = mapped_column(String(64))
    currency: Mapped[str | None] = mapped_column(String(16))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="watchlist_items")
    market_data_series: Mapped[list["MarketDataSeries"]] = relationship(
        back_populates="watchlist_item"
    )
    signals: Mapped[list["Signal"]] = relationship(back_populates="watchlist_item")
    trades: Mapped[list["Trade"]] = relationship(back_populates="watchlist_item")

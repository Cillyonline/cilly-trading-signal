from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import (
    MarketDataSource,
    MarketDataStatus,
    StructureState,
    Timeframe,
    TrendState,
)
from app.models.types import enum_values

if TYPE_CHECKING:
    from app.models.watchlist import WatchlistItem


class MarketDataSeries(Base):
    __tablename__ = "market_data_series"

    id: Mapped[int] = mapped_column(primary_key=True)
    watchlist_item_id: Mapped[int] = mapped_column(ForeignKey("watchlist_items.id"), index=True)
    source: Mapped[MarketDataSource] = mapped_column(enum_values(MarketDataSource))
    timeframe: Mapped[Timeframe] = mapped_column(enum_values(Timeframe))
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    candle_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[MarketDataStatus] = mapped_column(
        enum_values(MarketDataStatus), default=MarketDataStatus.IMPORTED
    )
    validation_errors: Mapped[dict | list | None] = mapped_column(JSON)
    file_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    watchlist_item: Mapped["WatchlistItem"] = relationship(back_populates="market_data_series")
    candles: Mapped[list["MarketDataCandle"]] = relationship(back_populates="series")
    indicator_snapshots: Mapped[list["IndicatorSnapshot"]] = relationship(back_populates="series")


class MarketDataCandle(Base):
    __tablename__ = "market_data_candles"
    __table_args__ = (
        UniqueConstraint("series_id", "timestamp", name="uq_candles_series_timestamp"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    series_id: Mapped[int] = mapped_column(ForeignKey("market_data_series.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    open: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    high: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    low: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    close: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    volume: Mapped[Decimal] = mapped_column(Numeric(24, 8))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    series: Mapped[MarketDataSeries] = relationship(back_populates="candles")


class IndicatorSnapshot(Base):
    __tablename__ = "indicator_snapshots"
    __table_args__ = (
        UniqueConstraint("series_id", "timestamp", name="uq_indicators_series_timestamp"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    series_id: Mapped[int] = mapped_column(ForeignKey("market_data_series.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ema20: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    ema50: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    ema200: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    rsi14: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    atr14: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    volume_avg20: Mapped[Decimal | None] = mapped_column(Numeric(24, 8))
    relative_volume: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    swing_high: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    swing_low: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    trend_state: Mapped[TrendState | None] = mapped_column(enum_values(TrendState))
    structure_state: Mapped[StructureState | None] = mapped_column(enum_values(StructureState))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    series: Mapped[MarketDataSeries] = relationship(back_populates="indicator_snapshots")

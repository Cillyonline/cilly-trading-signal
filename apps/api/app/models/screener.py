from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import (
    AssetClass,
    ScreenerImportSource,
    ScreenerImportStatus,
    ScreenerResultStatus,
)
from app.models.types import enum_values

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.watchlist import WatchlistItem


class ScreenerImport(Base):
    __tablename__ = "screener_imports"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    source: Mapped[ScreenerImportSource] = mapped_column(
        enum_values(ScreenerImportSource), default=ScreenerImportSource.TRADINGVIEW_SCREENER_CSV
    )
    file_name: Mapped[str | None] = mapped_column(String(255))
    asset_class: Mapped[AssetClass] = mapped_column(enum_values(AssetClass))
    screener_preset: Mapped[str | None] = mapped_column(String(120))
    snapshot_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    accepted_count: Mapped[int] = mapped_column(Integer, default=0)
    rejected_count: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[ScreenerImportStatus] = mapped_column(
        enum_values(ScreenerImportStatus), default=ScreenerImportStatus.PENDING
    )
    validation_errors: Mapped[dict | list | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="screener_imports")
    results: Mapped[list["ScreenerResult"]] = relationship(back_populates="screener_import")


class ScreenerResult(Base):
    __tablename__ = "screener_results"
    __table_args__ = (
        UniqueConstraint(
            "screener_import_id",
            "asset_class",
            "symbol",
            "exchange",
            name="uq_screener_results_import_symbol_exchange",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    screener_import_id: Mapped[int] = mapped_column(
        ForeignKey("screener_imports.id"), index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    watchlist_item_id: Mapped[int | None] = mapped_column(ForeignKey("watchlist_items.id"))
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    asset_class: Mapped[AssetClass] = mapped_column(enum_values(AssetClass))
    exchange: Mapped[str | None] = mapped_column(String(64))
    currency: Mapped[str | None] = mapped_column(String(16))
    sector: Mapped[str | None] = mapped_column(String(120))
    industry: Mapped[str | None] = mapped_column(String(120))
    price: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    change_percent: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    volume: Mapped[Decimal | None] = mapped_column(Numeric(24, 8))
    relative_volume: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    market_cap: Mapped[Decimal | None] = mapped_column(Numeric(24, 2))
    rsi14: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    ema20: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    ema50: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    ema200: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    rank: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[ScreenerResultStatus] = mapped_column(
        enum_values(ScreenerResultStatus), default=ScreenerResultStatus.CANDIDATE
    )
    duplicate_of_result_id: Mapped[int | None] = mapped_column(
        ForeignKey("screener_results.id")
    )
    validation_errors: Mapped[dict | list | None] = mapped_column(JSON)
    raw_metadata: Mapped[dict | list | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    screener_import: Mapped[ScreenerImport] = relationship(back_populates="results")
    user: Mapped["User"] = relationship(back_populates="screener_results")
    watchlist_item: Mapped["WatchlistItem | None"] = relationship(
        back_populates="screener_results"
    )
    duplicate_of: Mapped["ScreenerResult | None"] = relationship(remote_side=[id])

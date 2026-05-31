from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    JSON,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import (
    AssetClass,
    ManualReviewLabel,
    ReviewBatchType,
    ReviewFindingCategorySource,
    ScoreClass,
    SignalStatus,
    StrategyType,
)
from app.models.types import enum_values

if TYPE_CHECKING:
    from app.models.signal import Signal
    from app.models.user import User


class ReviewBatch(Base):
    __tablename__ = "review_batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    review_type: Mapped[ReviewBatchType] = mapped_column(enum_values(ReviewBatchType))
    description: Mapped[str | None] = mapped_column(Text)
    asset_class: Mapped[AssetClass | None] = mapped_column(enum_values(AssetClass))
    strategy_type: Mapped[StrategyType | None] = mapped_column(enum_values(StrategyType))
    review_window_start: Mapped[date | None] = mapped_column(Date)
    review_window_end: Mapped[date | None] = mapped_column(Date)
    data_source: Mapped[str | None] = mapped_column(String(160))
    context_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="review_batches")
    entries: Mapped[list["ReviewEntry"]] = relationship(
        back_populates="batch", cascade="all, delete-orphan"
    )


class ReviewEntry(Base):
    __tablename__ = "review_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("review_batches.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    signal_id: Mapped[int | None] = mapped_column(ForeignKey("signals.id"), index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    asset_class: Mapped[AssetClass] = mapped_column(enum_values(AssetClass))
    strategy_type: Mapped[StrategyType] = mapped_column(enum_values(StrategyType))
    stored_data_start: Mapped[date | None] = mapped_column(Date)
    stored_data_end: Mapped[date | None] = mapped_column(Date)
    benchmark_context: Mapped[str | None] = mapped_column(String(32))
    signal_status: Mapped[SignalStatus] = mapped_column(enum_values(SignalStatus))
    score_class: Mapped[ScoreClass | None] = mapped_column(enum_values(ScoreClass))
    no_trade_reasons: Mapped[list | dict | None] = mapped_column(JSON)
    risk_flags: Mapped[list | dict | None] = mapped_column(JSON)
    quality_blockers: Mapped[list | dict | None] = mapped_column(JSON)
    entry_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    stop_loss: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    target_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    planned_risk_reward: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    manual_review_label: Mapped[ManualReviewLabel] = mapped_column(enum_values(ManualReviewLabel))
    finding_category: Mapped[str] = mapped_column(String(64), default="unknown")
    finding_category_source: Mapped[ReviewFindingCategorySource] = mapped_column(
        enum_values(ReviewFindingCategorySource), default=ReviewFindingCategorySource.DERIVED
    )
    outcome_r: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    outcome_measurement_rule: Mapped[str | None] = mapped_column(Text)
    follow_up_needed: Mapped[bool] = mapped_column(Boolean, default=False)
    follow_up_issue_url: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    batch: Mapped["ReviewBatch"] = relationship(back_populates="entries")
    user: Mapped["User"] = relationship(back_populates="review_entries")
    signal: Mapped["Signal | None"] = relationship()
    revisions: Mapped[list["ReviewEntryRevision"]] = relationship(
        back_populates="entry",
        cascade="all, delete-orphan",
        order_by="ReviewEntryRevision.created_at",
    )


class ReviewEntryRevision(Base):
    __tablename__ = "review_entry_revisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("review_entries.id"), index=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("review_batches.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    revision_number: Mapped[int]
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    previous_values: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    entry: Mapped["ReviewEntry"] = relationship(back_populates="revisions")

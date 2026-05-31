from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, HttpUrl, model_validator

from app.models.enums import (
    AssetClass,
    ManualReviewLabel,
    ReviewBatchType,
    ReviewFindingCategorySource,
    ScoreClass,
    SignalStatus,
    StrategyType,
)


class ReviewBatchCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    review_type: ReviewBatchType
    description: str | None = Field(default=None, max_length=5000)
    asset_class: AssetClass | None = None
    strategy_type: StrategyType | None = None
    review_window_start: date | None = None
    review_window_end: date | None = None
    data_source: str | None = Field(default=None, max_length=160)
    context_notes: str | None = Field(default=None, max_length=5000)

    @model_validator(mode="after")
    def validate_window(self) -> "ReviewBatchCreate":
        if (
            self.review_window_start is not None
            and self.review_window_end is not None
            and self.review_window_end < self.review_window_start
        ):
            raise ValueError("Review window end must be on or after start.")
        return self


class ReviewEntryCreate(BaseModel):
    signal_id: int | None = None
    symbol: str = Field(min_length=1, max_length=32)
    asset_class: AssetClass
    strategy_type: StrategyType
    stored_data_start: date | None = None
    stored_data_end: date | None = None
    benchmark_context: str | None = Field(default=None, max_length=32)
    signal_status: SignalStatus
    score_class: ScoreClass | None = None
    no_trade_reasons: list | dict | None = None
    risk_flags: list | dict | None = None
    quality_blockers: list | dict | None = None
    finding_category: str | None = Field(default=None, max_length=64)
    finding_category_source: ReviewFindingCategorySource = ReviewFindingCategorySource.DERIVED
    entry_price: Decimal | None = None
    stop_loss: Decimal | None = None
    target_price: Decimal | None = None
    planned_risk_reward: Decimal | None = None
    manual_review_label: ManualReviewLabel
    outcome_r: Decimal | None = None
    outcome_measurement_rule: str | None = Field(default=None, max_length=5000)
    follow_up_needed: bool = False
    follow_up_issue_url: HttpUrl | None = None
    notes: str | None = Field(default=None, max_length=5000)

    @model_validator(mode="after")
    def validate_review_entry(self) -> "ReviewEntryCreate":
        if (
            self.stored_data_start
            and self.stored_data_end
            and self.stored_data_end < self.stored_data_start
        ):
            raise ValueError("Stored data end must be on or after start.")
        if self.outcome_r is not None and not self.outcome_measurement_rule:
            raise ValueError("Outcome measurement rule is required when outcome R is recorded.")
        if self.manual_review_label in {
            ManualReviewLabel.TOO_PERMISSIVE,
            ManualReviewLabel.TOO_STRICT,
        }:
            self.follow_up_needed = True
        return self


class ReviewEntryUpdate(ReviewEntryCreate):
    pass


class ReviewEntryRevisionRead(BaseModel):
    id: int
    entry_id: int
    batch_id: int
    revision_number: int
    changed_at: datetime
    previous_values: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewEntryRead(BaseModel):
    id: int
    batch_id: int
    signal_id: int | None
    symbol: str
    asset_class: AssetClass
    strategy_type: StrategyType
    stored_data_start: date | None
    stored_data_end: date | None
    benchmark_context: str | None
    signal_status: SignalStatus
    score_class: ScoreClass | None
    no_trade_reasons: list | dict | None
    risk_flags: list | dict | None
    quality_blockers: list | dict | None
    entry_price: Decimal | None
    stop_loss: Decimal | None
    target_price: Decimal | None
    planned_risk_reward: Decimal | None
    manual_review_label: ManualReviewLabel
    finding_category: str
    finding_category_source: ReviewFindingCategorySource
    outcome_r: Decimal | None
    outcome_measurement_rule: str | None
    follow_up_needed: bool
    follow_up_issue_url: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    revisions: list[ReviewEntryRevisionRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ReviewBatchSummary(BaseModel):
    reviewed_count: int
    label_counts: dict[str, int]
    follow_up_needed_count: int
    repeated_attention_labels: list[str]
    repeated_blocker_patterns: list[str]
    finding_category_counts: dict[str, int]
    repeated_finding_categories: list[str]
    evidence_only_notice: str


class ReviewBatchRead(BaseModel):
    id: int
    name: str
    review_type: ReviewBatchType
    description: str | None
    asset_class: AssetClass | None
    strategy_type: StrategyType | None
    review_window_start: date | None
    review_window_end: date | None
    data_source: str | None
    context_notes: str | None
    created_at: datetime
    updated_at: datetime
    entries: list[ReviewEntryRead] = Field(default_factory=list)
    summary: ReviewBatchSummary

    model_config = {"from_attributes": True}

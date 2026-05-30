from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import AssetClass, Bias, ScoreClass, SignalStatus, StrategyType, Timeframe


class SignalReviewEventRead(BaseModel):
    id: int
    signal_id: int
    user_id: int
    event_type: str
    previous_status: SignalStatus | None
    new_status: SignalStatus | None
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SignalRead(BaseModel):
    id: int
    watchlist_item_id: int
    symbol: str
    asset_class: AssetClass
    exchange: str | None
    strategy_type: StrategyType
    status: SignalStatus
    bias: Bias
    score: int | None
    score_class: ScoreClass | None
    timeframe_context: Timeframe | None
    timeframe_setup: Timeframe | None
    timeframe_trigger: Timeframe | None
    entry_low: Decimal | None
    entry_high: Decimal | None
    trigger_level: Decimal | None
    stop_loss: Decimal | None
    target_1: Decimal | None
    target_2: Decimal | None
    risk_reward: Decimal | None
    invalidation_reason: str | None
    reasoning: list | dict | None
    risk_flags: list | dict | None
    no_trade_reasons: list | dict | None
    next_action: str | None
    quality_report: list[dict[str, str]] = Field(default_factory=list)
    review_note: str | None
    created_at: datetime
    updated_at: datetime
    triggered_at: datetime | None
    is_stale: bool
    stale_reason: str | None
    stale_after_days: int
    review_events: list[SignalReviewEventRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class SignalStatusUpdate(BaseModel):
    status: SignalStatus


class SignalReviewNoteUpdate(BaseModel):
    review_note: str | None = Field(default=None, max_length=5000)

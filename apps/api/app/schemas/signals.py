from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.enums import AssetClass, Bias, ScoreClass, SignalStatus, StrategyType, Timeframe


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
    created_at: datetime
    updated_at: datetime
    triggered_at: datetime | None

    model_config = {"from_attributes": True}


class SignalStatusUpdate(BaseModel):
    status: SignalStatus

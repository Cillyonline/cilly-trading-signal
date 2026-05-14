from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.models.enums import AssetClass, StrategyType, TradeStatus


class TradeCreate(BaseModel):
    watchlist_item_id: int | None = None
    signal_id: int | None = None
    strategy_type: StrategyType | None = None
    entry_price: Decimal = Field(gt=0)
    stop_loss: Decimal = Field(gt=0)
    target_1: Decimal | None = Field(default=None, gt=0)
    target_2: Decimal | None = Field(default=None, gt=0)
    position_size: Decimal = Field(gt=0)
    fees: Decimal | None = Field(default=None, ge=0)
    opened_at: datetime
    notes: str | None = None

    @model_validator(mode="after")
    def validate_long_trade_plan(self) -> "TradeCreate":
        if self.watchlist_item_id is None and self.signal_id is None:
            raise ValueError("watchlist_item_id or signal_id is required.")
        if self.entry_price <= self.stop_loss:
            raise ValueError("entry_price must be greater than stop_loss for long trades.")
        if self.target_1 is not None and self.target_1 <= self.entry_price:
            raise ValueError("target_1 must be greater than entry_price.")
        if self.target_2 is not None and self.target_2 <= self.entry_price:
            raise ValueError("target_2 must be greater than entry_price.")
        return self


class TradeRead(BaseModel):
    id: int
    signal_id: int | None
    watchlist_item_id: int
    status: TradeStatus
    strategy_type: StrategyType
    asset_class: AssetClass
    symbol: str
    entry_price: Decimal
    stop_loss: Decimal
    target_1: Decimal | None
    target_2: Decimal | None
    position_size: Decimal
    fees: Decimal | None
    opened_at: datetime
    closed_at: datetime | None
    exit_price: Decimal | None
    risk_per_unit: Decimal
    initial_risk_amount: Decimal | None
    initial_risk_percent: Decimal | None
    initial_risk_reward: Decimal | None
    target_1_potential_r: Decimal | None
    target_2_potential_r: Decimal | None
    result_amount: Decimal | None
    result_r: Decimal | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

from decimal import Decimal

from pydantic import BaseModel, Field


class SettingsRead(BaseModel):
    account_size: Decimal | None
    default_risk_percent: Decimal
    max_risk_percent: Decimal
    min_risk_reward: Decimal
    max_open_trades: int
    base_currency: str

    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    account_size: Decimal | None = Field(default=None, gt=0)
    default_risk_percent: Decimal | None = Field(default=None, gt=0, le=100)
    max_risk_percent: Decimal | None = Field(default=None, gt=0, le=100)
    min_risk_reward: Decimal | None = Field(default=None, gt=0)
    max_open_trades: int | None = Field(default=None, ge=1, le=100)
    base_currency: str | None = Field(default=None, min_length=3, max_length=3)

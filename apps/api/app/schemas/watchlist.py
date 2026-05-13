from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.enums import AssetClass


class WatchlistItemBase(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    name: str | None = Field(default=None, max_length=255)
    asset_class: AssetClass
    exchange: str | None = Field(default=None, max_length=64)
    currency: str | None = Field(default=None, max_length=16)
    is_active: bool = True
    notes: str | None = None

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("exchange", "currency")
    @classmethod
    def normalize_optional_uppercase(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        return normalized or None

    @field_validator("name", "notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class WatchlistItemCreate(WatchlistItemBase):
    pass


class WatchlistItemUpdate(BaseModel):
    symbol: str | None = Field(default=None, min_length=1, max_length=32)
    name: str | None = Field(default=None, max_length=255)
    asset_class: AssetClass | None = None
    exchange: str | None = Field(default=None, max_length=64)
    currency: str | None = Field(default=None, max_length=16)
    is_active: bool | None = None
    notes: str | None = None

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().upper()

    @field_validator("exchange", "currency")
    @classmethod
    def normalize_optional_uppercase(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        return normalized or None

    @field_validator("name", "notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class WatchlistItemRead(WatchlistItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_analyzed_at: datetime | None

    model_config = {"from_attributes": True}

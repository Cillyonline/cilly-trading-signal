from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import (
    AssetClass,
    ScreenerImportSource,
    ScreenerImportStatus,
    ScreenerResultStatus,
)


class ScreenerImportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    source: ScreenerImportSource
    file_name: str | None
    asset_class: AssetClass
    screener_preset: str | None
    snapshot_at: datetime | None
    row_count: int
    accepted_count: int
    rejected_count: int
    duplicate_count: int
    status: ScreenerImportStatus
    validation_errors: dict[str, Any] | list[Any] | None
    created_at: datetime


class ScreenerResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    screener_import_id: int
    user_id: int
    watchlist_item_id: int | None
    symbol: str
    name: str | None
    asset_class: AssetClass
    exchange: str | None
    currency: str | None
    sector: str | None
    industry: str | None
    price: Decimal | None
    change_percent: Decimal | None
    volume: Decimal | None
    relative_volume: Decimal | None
    market_cap: Decimal | None
    rsi14: Decimal | None
    ema20: Decimal | None
    ema50: Decimal | None
    ema200: Decimal | None
    rank: int | None
    status: ScreenerResultStatus
    duplicate_of_result_id: int | None
    validation_errors: dict[str, Any] | list[Any] | None
    raw_metadata: dict[str, Any] | list[Any] | None
    created_at: datetime
    updated_at: datetime


class ScreenerImportResult(BaseModel):
    import_record: ScreenerImportRead | None
    errors: list[dict[str, object | None]]


class ScreenerImportDetail(ScreenerImportRead):
    results: list[ScreenerResultRead]


class ScreenerResultFilters(BaseModel):
    asset_class: AssetClass | None = None
    status: ScreenerResultStatus | None = None
    exchange: str | None = None
    screener_import_id: int | None = None
    min_volume: Decimal | None = None
    min_relative_volume: Decimal | None = None
    min_rsi14: Decimal | None = None
    max_rsi14: Decimal | None = None
    sort_by: str = "created_at"
    sort_direction: str = "desc"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)


class ScreenerResultPage(BaseModel):
    items: list[ScreenerResultRead]
    total: int
    page: int
    page_size: int
    total_pages: int


class ScreenerResultBulkStatusUpdate(BaseModel):
    result_ids: list[int] = Field(min_length=1, max_length=200)
    status: ScreenerResultStatus

    @field_validator("status")
    @classmethod
    def validate_review_status(cls, value: ScreenerResultStatus) -> ScreenerResultStatus:
        if value not in {
            ScreenerResultStatus.CANDIDATE,
            ScreenerResultStatus.IGNORED,
            ScreenerResultStatus.REJECTED,
        }:
            raise ValueError("Bulk status must be candidate, ignored, or rejected.")
        return value


class ScreenerResultBulkStatusResult(BaseModel):
    requested_count: int
    updated_count: int
    skipped_count: int
    skipped_result_ids: list[int]
    results: list[ScreenerResultRead]

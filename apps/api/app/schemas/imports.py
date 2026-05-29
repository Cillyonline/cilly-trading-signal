from datetime import datetime

from pydantic import BaseModel

from app.models.enums import (
    MarketDataFreshnessStatus,
    MarketDataSource,
    MarketDataStatus,
    MarketDataSyncStatus,
    Timeframe,
)


class CsvImportError(BaseModel):
    row: int | None = None
    field: str | None = None
    message: str


class CsvImportResult(BaseModel):
    series_id: int | None
    watchlist_item_id: int
    timeframe: Timeframe
    status: MarketDataStatus
    candle_count: int
    start_time: datetime | None
    end_time: datetime | None
    source: MarketDataSource
    freshness_status: MarketDataFreshnessStatus
    sync_status: MarketDataSyncStatus
    last_synced_at: datetime | None
    errors: list[CsvImportError]


class ImportHistoryItem(BaseModel):
    series_id: int
    watchlist_item_id: int
    symbol: str
    timeframe: Timeframe
    status: MarketDataStatus
    candle_count: int
    start_time: datetime | None
    end_time: datetime | None
    imported_at: datetime
    source: MarketDataSource
    freshness_status: MarketDataFreshnessStatus
    sync_status: MarketDataSyncStatus
    last_synced_at: datetime | None
    provider_name: str | None
    file_name: str | None

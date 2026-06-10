from datetime import datetime

from pydantic import BaseModel, Field

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


class MarketDataSyncRequest(BaseModel):
    watchlist_item_id: int
    timeframe: Timeframe


class ProviderTimeframeCapabilityRead(BaseModel):
    timeframe: Timeframe
    supported: bool
    reason: str


def default_alpha_vantage_capabilities() -> list[ProviderTimeframeCapabilityRead]:
    return [
        ProviderTimeframeCapabilityRead(
            timeframe=Timeframe.ONE_WEEK,
            supported=False,
            reason=(
                "Alpha Vantage first path does not support weekly sync here; "
                "use CSV fallback."
            ),
        ),
        ProviderTimeframeCapabilityRead(
            timeframe=Timeframe.ONE_DAY,
            supported=True,
            reason="Guarded Daily/EOD sync path is supported for configured symbols.",
        ),
        ProviderTimeframeCapabilityRead(
            timeframe=Timeframe.FOUR_HOURS,
            supported=False,
            reason=(
                "4H/intraday provider sync is not selected; "
                "use TradingView CSV fallback."
            ),
        ),
    ]


class MarketDataSyncResponse(BaseModel):
    watchlist_item_id: int
    series_id: int
    source: MarketDataSource
    timeframe: Timeframe
    candle_count: int
    provider_name: str | None
    provider_symbol: str | None
    provider_exchange: str | None
    provider_timeframe: str | None
    sync_status: MarketDataSyncStatus
    freshness_status: MarketDataFreshnessStatus
    last_synced_at: datetime | None
    end_time: datetime | None
    sync_error_code: str | None
    sync_error_message: str | None
    capability_note: str = (
        "Provider sync is stored-data only. Unsupported timeframes require CSV fallback."
    )
    provider_capabilities: list[ProviderTimeframeCapabilityRead] = Field(
        default_factory=default_alpha_vantage_capabilities
    )

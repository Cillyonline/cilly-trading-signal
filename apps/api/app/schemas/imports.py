from datetime import datetime

from pydantic import BaseModel

from app.models.enums import MarketDataStatus, Timeframe


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
    errors: list[CsvImportError]

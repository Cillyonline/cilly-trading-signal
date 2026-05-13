import csv
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from io import StringIO

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.enums import MarketDataSource, MarketDataStatus, Timeframe
from app.models.market_data import MarketDataCandle, MarketDataSeries
from app.models.watchlist import WatchlistItem
from app.schemas.imports import CsvImportError, CsvImportResult

REQUIRED_COLUMNS = {"time", "open", "high", "low", "close", "volume"}
MIN_CANDLE_COUNT = 20


@dataclass(frozen=True)
class ParsedCandle:
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


def import_tradingview_csv(
    db: Session,
    watchlist_item: WatchlistItem,
    timeframe: Timeframe,
    file_name: str | None,
    content: str,
) -> CsvImportResult:
    errors: list[CsvImportError] = []
    candles = parse_tradingview_csv(content, errors)

    if len(candles) < MIN_CANDLE_COUNT:
        errors.append(
            CsvImportError(
                message=f"CSV must contain at least {MIN_CANDLE_COUNT} valid candles."
            )
        )

    if errors:
        return CsvImportResult(
            series_id=None,
            watchlist_item_id=watchlist_item.id,
            timeframe=timeframe,
            status=MarketDataStatus.FAILED,
            candle_count=0,
            start_time=None,
            end_time=None,
            errors=errors,
        )

    series = MarketDataSeries(
        watchlist_item_id=watchlist_item.id,
        source=MarketDataSource.TRADINGVIEW_CSV,
        timeframe=timeframe,
        start_time=candles[0].timestamp,
        end_time=candles[-1].timestamp,
        candle_count=len(candles),
        status=MarketDataStatus.VALIDATED,
        validation_errors=None,
        file_name=file_name,
    )
    db.add(series)
    db.flush()

    db.add_all(
        MarketDataCandle(
            series_id=series.id,
            timestamp=candle.timestamp,
            open=candle.open,
            high=candle.high,
            low=candle.low,
            close=candle.close,
            volume=candle.volume,
        )
        for candle in candles
    )

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        return CsvImportResult(
            series_id=None,
            watchlist_item_id=watchlist_item.id,
            timeframe=timeframe,
            status=MarketDataStatus.FAILED,
            candle_count=0,
            start_time=None,
            end_time=None,
            errors=[CsvImportError(message=f"Duplicate candle timestamp detected: {error}")],
        )

    db.refresh(series)
    return CsvImportResult(
        series_id=series.id,
        watchlist_item_id=watchlist_item.id,
        timeframe=timeframe,
        status=series.status,
        candle_count=series.candle_count,
        start_time=series.start_time,
        end_time=series.end_time,
        errors=[],
    )


def parse_tradingview_csv(content: str, errors: list[CsvImportError]) -> list[ParsedCandle]:
    reader = csv.DictReader(StringIO(content))
    columns = set(reader.fieldnames or [])
    missing_columns = sorted(REQUIRED_COLUMNS - columns)
    if missing_columns:
        errors.extend(
            CsvImportError(field=column, message=f"Missing required column: {column}")
            for column in missing_columns
        )
        return []

    candles: list[ParsedCandle] = []
    seen_timestamps: set[datetime] = set()

    for row_number, row in enumerate(reader, start=2):
        candle = parse_row(row, row_number, errors)
        if candle is None:
            continue
        if candle.timestamp in seen_timestamps:
            errors.append(
                CsvImportError(
                    row=row_number,
                    field="time",
                    message="Duplicate timestamp in CSV.",
                )
            )
            continue
        seen_timestamps.add(candle.timestamp)
        candles.append(candle)

    candles.sort(key=lambda candle: candle.timestamp)
    return candles


def parse_row(
    row: dict[str, str], row_number: int, errors: list[CsvImportError]
) -> ParsedCandle | None:
    timestamp = parse_timestamp(row.get("time", ""), row_number, errors)
    open_price = parse_decimal(row.get("open", ""), "open", row_number, errors)
    high = parse_decimal(row.get("high", ""), "high", row_number, errors)
    low = parse_decimal(row.get("low", ""), "low", row_number, errors)
    close = parse_decimal(row.get("close", ""), "close", row_number, errors)
    volume = parse_decimal(row.get("volume", ""), "volume", row_number, errors)

    if None in (timestamp, open_price, high, low, close, volume):
        return None

    assert timestamp is not None
    assert open_price is not None
    assert high is not None
    assert low is not None
    assert close is not None
    assert volume is not None

    if low > high:
        errors.append(
            CsvImportError(row=row_number, message="Low price cannot be above high price.")
        )
        return None

    if not (low <= open_price <= high):
        errors.append(
            CsvImportError(row=row_number, field="open", message="Open must be within low/high.")
        )
        return None

    if not (low <= close <= high):
        errors.append(
            CsvImportError(row=row_number, field="close", message="Close must be within low/high.")
        )
        return None

    if volume < 0:
        errors.append(
            CsvImportError(row=row_number, field="volume", message="Volume cannot be negative.")
        )
        return None

    return ParsedCandle(
        timestamp=timestamp,
        open=open_price,
        high=high,
        low=low,
        close=close,
        volume=volume,
    )


def parse_timestamp(
    value: str, row_number: int, errors: list[CsvImportError]
) -> datetime | None:
    normalized = value.strip()
    if not normalized:
        errors.append(CsvImportError(row=row_number, field="time", message="Time is required."))
        return None

    for parser in (datetime.fromisoformat,):
        try:
            return parser(normalized.replace("Z", "+00:00"))
        except ValueError:
            continue

    for format_string in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(normalized, format_string)
        except ValueError:
            continue

    errors.append(CsvImportError(row=row_number, field="time", message="Invalid timestamp."))
    return None


def parse_decimal(
    value: str, field: str, row_number: int, errors: list[CsvImportError]
) -> Decimal | None:
    normalized = value.strip().replace(",", "")
    if not normalized:
        errors.append(CsvImportError(row=row_number, field=field, message="Value is required."))
        return None

    try:
        return Decimal(normalized)
    except InvalidOperation:
        errors.append(CsvImportError(row=row_number, field=field, message="Invalid number."))
        return None

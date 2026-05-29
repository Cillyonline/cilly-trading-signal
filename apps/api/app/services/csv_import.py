import csv
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from io import StringIO

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.enums import (
    MarketDataFreshnessStatus,
    MarketDataSource,
    MarketDataStatus,
    MarketDataSyncStatus,
    Timeframe,
)
from app.models.market_data import MarketDataCandle, MarketDataSeries
from app.models.watchlist import WatchlistItem
from app.schemas.imports import CsvImportError, CsvImportResult

REQUIRED_COLUMNS = {"time", "open", "high", "low", "close", "volume"}
MIN_CANDLE_COUNT = 20
MAX_CANDLE_COUNT = 10_000
MAX_CSV_UPLOAD_BYTES = 2 * 1024 * 1024

FOUR_HOUR_MIN_INTERVAL = timedelta(hours=3)
FOUR_HOUR_MAX_INTERVAL = timedelta(hours=5)
DAILY_MIN_INTERVAL = timedelta(hours=18)
WEEKLY_MIN_INTERVAL = timedelta(days=5)
WEEKLY_LIKE_INTERVAL = timedelta(days=6)


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

    if not errors:
        validate_timeframe_consistency(candles, timeframe, errors)

    if errors:
        return CsvImportResult(
            series_id=None,
            watchlist_item_id=watchlist_item.id,
            timeframe=timeframe,
            status=MarketDataStatus.FAILED,
            candle_count=0,
            start_time=None,
            end_time=None,
            source=MarketDataSource.TRADINGVIEW_CSV,
            freshness_status=MarketDataFreshnessStatus.UNKNOWN,
            sync_status=MarketDataSyncStatus.NOT_APPLICABLE,
            last_synced_at=None,
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
        freshness_status=MarketDataFreshnessStatus.UNKNOWN,
        sync_status=MarketDataSyncStatus.NOT_APPLICABLE,
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
            source=MarketDataSource.TRADINGVIEW_CSV,
            freshness_status=MarketDataFreshnessStatus.FAILED,
            sync_status=MarketDataSyncStatus.NOT_APPLICABLE,
            last_synced_at=None,
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
        source=series.source,
        freshness_status=series.freshness_status,
        sync_status=series.sync_status,
        last_synced_at=series.last_synced_at,
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
        if len(candles) >= MAX_CANDLE_COUNT:
            errors.append(
                CsvImportError(
                    message=f"CSV must contain at most {MAX_CANDLE_COUNT} candles."
                )
            )
            break

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


def validate_timeframe_consistency(
    candles: list[ParsedCandle], timeframe: Timeframe, errors: list[CsvImportError]
) -> None:
    intervals = [
        candles[index].timestamp - candles[index - 1].timestamp
        for index in range(1, len(candles))
    ]
    if not intervals:
        return

    if timeframe == Timeframe.FOUR_HOURS:
        expected_intervals = [
            interval
            for interval in intervals
            if FOUR_HOUR_MIN_INTERVAL <= interval <= FOUR_HOUR_MAX_INTERVAL
        ]
        too_short_intervals = [
            interval for interval in intervals if interval < FOUR_HOUR_MIN_INTERVAL
        ]
        if too_short_intervals or not expected_intervals:
            errors.append(
                CsvImportError(
                    field="time",
                    message=(
                        "Selected timeframe 4H does not match CSV timestamps; "
                        "expected recurring four-hour candle spacing."
                    ),
                )
            )
        return

    if timeframe == Timeframe.ONE_DAY:
        intraday_intervals = [
            interval for interval in intervals if interval < DAILY_MIN_INTERVAL
        ]
        weekly_like = all(interval >= WEEKLY_LIKE_INTERVAL for interval in intervals)
        if intraday_intervals or weekly_like:
            errors.append(
                CsvImportError(
                    field="time",
                    message=(
                        "Selected timeframe 1D does not match CSV timestamps; "
                        "expected daily candle spacing with possible weekend or holiday gaps."
                    ),
                )
            )
        return

    if timeframe == Timeframe.ONE_WEEK:
        too_short_intervals = [
            interval for interval in intervals if interval < WEEKLY_MIN_INTERVAL
        ]
        if too_short_intervals:
            errors.append(
                CsvImportError(
                    field="time",
                    message=(
                        "Selected timeframe 1W does not match CSV timestamps; "
                        "expected weekly candle spacing."
                    ),
                )
            )


def parse_row(
    row: dict[str, str | None], row_number: int, errors: list[CsvImportError]
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
    value: str | None, row_number: int, errors: list[CsvImportError]
) -> datetime | None:
    if value is None:
        errors.append(CsvImportError(row=row_number, field="time", message="Time is required."))
        return None

    normalized = value.strip()
    if not normalized:
        errors.append(CsvImportError(row=row_number, field="time", message="Time is required."))
        return None

    for parser in (datetime.fromisoformat,):
        try:
            return normalize_timestamp(parser(normalized.replace("Z", "+00:00")))
        except ValueError:
            continue

    for format_string in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return normalize_timestamp(datetime.strptime(normalized, format_string))
        except ValueError:
            continue

    errors.append(CsvImportError(row=row_number, field="time", message="Invalid timestamp."))
    return None


def parse_decimal(
    value: str | None, field: str, row_number: int, errors: list[CsvImportError]
) -> Decimal | None:
    if value is None:
        errors.append(CsvImportError(row=row_number, field=field, message="Value is required."))
        return None

    normalized = value.strip().replace(",", "")
    if not normalized:
        errors.append(CsvImportError(row=row_number, field=field, message="Value is required."))
        return None

    try:
        return Decimal(normalized)
    except InvalidOperation:
        errors.append(CsvImportError(row=row_number, field=field, message="Invalid number."))
        return None


def normalize_timestamp(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)

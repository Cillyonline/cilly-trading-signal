from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from app.models.enums import MarketDataSource, Timeframe


def as_utc(value: datetime) -> datetime:
    # SQLite returns naive datetimes for stored UTC values.
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def normalize_provider_time(value: str, timezone: str) -> datetime:
    zone = ZoneInfo(timezone)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is not None:
        return parsed.astimezone(UTC)
    first = parsed.replace(tzinfo=zone, fold=0)
    second = parsed.replace(tzinfo=zone, fold=1)
    if first.utcoffset() != second.utcoffset():
        raise ValueError("Ambiguous or nonexistent provider time")
    if first.astimezone(UTC).astimezone(zone).replace(tzinfo=None) != parsed:
        raise ValueError("Nonexistent provider time")
    return first.astimezone(UTC)


def series_timezone(series: object) -> str:
    timezone = getattr(series, "timestamp_timezone", None)
    if timezone:
        ZoneInfo(timezone)
        return timezone
    if getattr(series, "source", None) == MarketDataSource.TRADINGVIEW_CSV:
        return "UTC"
    raise ValueError("Series timezone unknown; re-sync provider data")


def candle_end(timestamp: datetime, timeframe: Timeframe, timezone: str) -> datetime:
    start = as_utc(timestamp)
    if timeframe == Timeframe.FOUR_HOURS:
        return start + timedelta(hours=4)
    local = start.astimezone(ZoneInfo(timezone))
    days = 7 if timeframe == Timeframe.ONE_WEEK else 1
    end = local + timedelta(days=days)
    # If a calendar boundary falls in a DST overlap/gap, use the later instant.
    return max(end.replace(fold=fold).astimezone(UTC) for fold in (0, 1))


def completed_candles(series: object, candles: list, as_of: datetime) -> list:
    try:
        timezone = series_timezone(series)
    except (ValueError, KeyError):
        return []
    cutoff = as_utc(as_of)
    return [
        candle for candle in candles
        if candle_end(candle.timestamp, series.timeframe, timezone) <= cutoff
    ]

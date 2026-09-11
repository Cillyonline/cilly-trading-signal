from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from app.models.enums import MarketDataSource, Timeframe
from app.services.candle_time import candle_end, completed_candles, normalize_provider_time
from app.services.market_data_sync import parse_twelve_data_response


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-01-15 09:30:00", "2026-01-15T14:30:00+00:00"),
        ("2026-06-11 09:30:00", "2026-06-11T13:30:00+00:00"),
        ("2026-06-11T09:30:00-04:00", "2026-06-11T13:30:00+00:00"),
        ("2026-11-01T01:30:00-05:00", "2026-11-01T06:30:00+00:00"),
    ],
)
def test_exchange_times_preserve_the_actual_instant(value, expected):
    assert normalize_provider_time(value, "America/New_York").isoformat() == expected


@pytest.mark.parametrize("value", ["2026-03-08 02:30:00", "2026-11-01 01:30:00"])
def test_ambiguous_or_nonexistent_local_time_is_rejected(value):
    with pytest.raises(ValueError):
        normalize_provider_time(value, "America/New_York")


@pytest.mark.parametrize(
    ("start", "timeframe", "hours"),
    [
        ("2026-03-08T05:00:00+00:00", Timeframe.ONE_DAY, 23),
        ("2026-11-01T04:00:00+00:00", Timeframe.ONE_DAY, 25),
        ("2026-03-02T05:00:00+00:00", Timeframe.ONE_WEEK, 167),
        ("2026-10-26T04:00:00+00:00", Timeframe.ONE_WEEK, 169),
        ("2026-03-08T05:00:00+00:00", Timeframe.FOUR_HOURS, 4),
    ],
)
def test_calendar_intervals_and_elapsed_four_hours_across_dst(start, timeframe, hours):
    timestamp = datetime.fromisoformat(start)
    assert candle_end(timestamp, timeframe, "America/New_York") == (
        timestamp + timedelta(hours=hours)
    )


@pytest.mark.parametrize("timeframe", list(Timeframe))
def test_only_completed_candles_are_used_at_inclusive_cutoff(timeframe):
    start = datetime(2026, 6, 1, tzinfo=UTC)
    candle = SimpleNamespace(timestamp=start)
    series = SimpleNamespace(
        timeframe=timeframe, source=MarketDataSource.TRADINGVIEW_CSV, timestamp_timezone=None
    )
    end = candle_end(start, timeframe, "UTC")
    assert completed_candles(series, [candle], end - timedelta(microseconds=1)) == []
    assert completed_candles(series, [candle], end) == [candle]
    assert completed_candles(series, [candle], start - timedelta(days=1)) == []


def test_legacy_provider_series_requires_resync():
    series = SimpleNamespace(
        timeframe=Timeframe.ONE_DAY, source=MarketDataSource.PROVIDER, timestamp_timezone=None
    )
    candle = SimpleNamespace(timestamp=datetime(2026, 1, 1, tzinfo=UTC))
    assert completed_candles(series, [candle], datetime(2026, 6, 1, tzinfo=UTC)) == []


@pytest.mark.parametrize("meta", [{}, {"exchange_timezone": "invalid/secret-payload"}])
def test_provider_metadata_failure_is_sanitized(meta):
    payload = {
        "meta": meta,
        "values": [{"datetime": "2026-06-11", "open": "1", "high": "2",
                    "low": "1", "close": "2", "volume": "10"}],
    }
    assert parse_twelve_data_response(payload) == ([], "provider_invalid_response")


def test_crypto_provider_defaults_to_utc_only_for_explicit_asset_type():
    payload = {
        "meta": {"type": "Digital Currency"},
        "values": [{"datetime": "2026-06-11", "open": "1", "high": "2",
                    "low": "1", "close": "2", "volume": "10"}],
    }
    candles, error = parse_twelve_data_response(payload)
    assert error is None
    assert candles[0].timestamp == datetime(2026, 6, 11, tzinfo=UTC)

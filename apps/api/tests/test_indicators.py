from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.services.indicators import (
    IndicatorInputCandle,
    calculate_atr,
    calculate_ema,
    calculate_indicator_snapshots,
    calculate_rsi,
    calculate_simple_moving_average,
)


def decimal_values(start: int, end: int) -> list[Decimal]:
    return [Decimal(value) for value in range(start, end + 1)]


def assert_decimal_close(actual: Decimal | None, expected: Decimal) -> None:
    assert actual is not None
    assert actual == pytest.approx(expected)


def test_ema_uses_initial_sma_then_standard_smoothing() -> None:
    values = decimal_values(1, 21)

    ema20 = calculate_ema(values, period=20)

    assert ema20[:19] == [None] * 19
    assert_decimal_close(ema20[19], Decimal("10.5"))
    assert_decimal_close(ema20[20], Decimal("11.5"))


def test_rsi_returns_none_until_period_has_enough_changes() -> None:
    values = decimal_values(1, 15)

    rsi14 = calculate_rsi(values, period=14)

    assert rsi14[:14] == [None] * 14
    assert_decimal_close(rsi14[14], Decimal("100"))


def test_rsi_returns_neutral_for_flat_prices() -> None:
    values = [Decimal("10")] * 15

    rsi14 = calculate_rsi(values, period=14)

    assert_decimal_close(rsi14[14], Decimal("50"))


def test_atr_uses_wilder_smoothing_from_true_ranges() -> None:
    closes = decimal_values(10, 24)
    highs = [close + Decimal("1") for close in closes]
    lows = [close - Decimal("1") for close in closes]

    atr14 = calculate_atr(highs, lows, closes, period=14)

    assert atr14[:13] == [None] * 13
    assert_decimal_close(atr14[13], Decimal("2"))
    assert_decimal_close(atr14[14], Decimal("2"))


def test_volume_average_and_relative_volume_inputs_are_deterministic() -> None:
    volumes = decimal_values(1, 21)

    volume_avg20 = calculate_simple_moving_average(volumes, period=20)

    assert volume_avg20[:19] == [None] * 19
    assert_decimal_close(volume_avg20[19], Decimal("10.5"))
    assert_decimal_close(volume_avg20[20], Decimal("11.5"))


def test_indicator_snapshots_map_to_indicator_snapshot_fields() -> None:
    start_time = datetime(2024, 1, 1, tzinfo=UTC)
    candles = [
        IndicatorInputCandle(
            timestamp=start_time + timedelta(days=index - 1),
            high=Decimal(index + 1),
            low=Decimal(index - 1),
            close=Decimal(index),
            volume=Decimal(index),
        )
        for index in range(1, 202)
    ]

    snapshots = calculate_indicator_snapshots(list(reversed(candles)))
    latest = snapshots[-1]
    snapshot_kwargs = latest.to_indicator_snapshot_kwargs()

    assert len(snapshots) == 201
    assert latest.timestamp == start_time + timedelta(days=200)
    assert_decimal_close(latest.ema20, Decimal("191.5"))
    assert_decimal_close(latest.ema50, Decimal("176.5"))
    assert_decimal_close(latest.ema200, Decimal("101.5"))
    assert_decimal_close(latest.rsi14, Decimal("100"))
    assert_decimal_close(latest.atr14, Decimal("2"))
    assert_decimal_close(latest.volume_avg20, Decimal("191.5"))
    assert_decimal_close(latest.relative_volume, Decimal(201) / Decimal("191.5"))
    assert set(snapshot_kwargs) == {
        "timestamp",
        "ema20",
        "ema50",
        "ema200",
        "rsi14",
        "atr14",
        "volume_avg20",
        "relative_volume",
        "swing_high",
        "swing_low",
        "trend_state",
        "structure_state",
    }


def test_indicator_snapshots_return_none_for_insufficient_history() -> None:
    start_time = datetime(2024, 1, 1, tzinfo=UTC)
    candles = [
        IndicatorInputCandle(
            timestamp=start_time + timedelta(days=index),
            high=Decimal("11"),
            low=Decimal("9"),
            close=Decimal("10"),
            volume=Decimal("100"),
        )
        for index in range(13)
    ]

    snapshots = calculate_indicator_snapshots(candles)

    assert len(snapshots) == 13
    assert all(snapshot.ema20 is None for snapshot in snapshots)
    assert all(snapshot.ema50 is None for snapshot in snapshots)
    assert all(snapshot.ema200 is None for snapshot in snapshots)
    assert all(snapshot.rsi14 is None for snapshot in snapshots)
    assert all(snapshot.atr14 is None for snapshot in snapshots)
    assert all(snapshot.volume_avg20 is None for snapshot in snapshots)
    assert all(snapshot.relative_volume is None for snapshot in snapshots)

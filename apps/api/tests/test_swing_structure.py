from decimal import Decimal

import pytest

from app.services.swing_structure import (
    detect_swing_structure,
    latest_meaningful_swing_high,
    latest_meaningful_swing_low,
)


def decimals(values: list[str]) -> list[Decimal]:
    return [Decimal(value) for value in values]


def test_detects_unique_pivot_highs_and_lows() -> None:
    highs = decimals(["10", "12", "15", "13", "12", "14", "16", "13", "12"])
    lows = decimals(["9", "10", "11", "10", "8", "10", "12", "9", "10"])

    structure = detect_swing_structure(highs, lows, left=2, right=2)

    assert [(point.index, point.value) for point in structure.pivot_highs] == [
        (2, Decimal("15")),
        (6, Decimal("16")),
    ]
    assert [(point.index, point.value) for point in structure.pivot_lows] == [
        (4, Decimal("8"))
    ]
    assert structure.latest_pivot_high.value == Decimal("16")
    assert structure.latest_pivot_low.value == Decimal("8")


def test_detects_higher_high_and_higher_low_structure() -> None:
    highs = decimals(["10", "13", "16", "14", "12", "15", "18", "16", "14", "15"])
    lows = decimals(["9", "11", "12", "10", "8", "11", "13", "12", "10", "12"])

    structure = detect_swing_structure(highs, lows, left=1, right=1)

    assert structure.higher_high_confirmed is True
    assert structure.higher_low_confirmed is True


def test_ignores_equal_high_plateaus_as_noisy_pivots() -> None:
    highs = decimals(["10", "12", "15", "15", "13", "12"])
    lows = decimals(["9", "10", "12", "11", "10", "9"])

    structure = detect_swing_structure(highs, lows, left=1, right=1)

    assert structure.pivot_highs == []


def test_latest_meaningful_levels_fall_back_when_no_pivot_exists() -> None:
    highs = decimals(["10", "11", "12", "13"])
    lows = decimals(["9", "10", "11", "12"])

    assert latest_meaningful_swing_low(highs, lows) == Decimal("9")
    assert latest_meaningful_swing_high(highs, lows) == Decimal("13")


def test_rejects_mismatched_high_low_lengths() -> None:
    with pytest.raises(ValueError, match="same length"):
        detect_swing_structure(decimals(["10"]), decimals(["9", "8"]))


def test_rejects_invalid_pivot_windows() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        detect_swing_structure(decimals(["10"]), decimals(["9"]), left=0)

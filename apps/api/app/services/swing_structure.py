from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class SwingPoint:
    index: int
    value: Decimal


@dataclass(frozen=True)
class SwingStructure:
    pivot_highs: list[SwingPoint]
    pivot_lows: list[SwingPoint]

    @property
    def latest_pivot_high(self) -> SwingPoint | None:
        return self.pivot_highs[-1] if self.pivot_highs else None

    @property
    def latest_pivot_low(self) -> SwingPoint | None:
        return self.pivot_lows[-1] if self.pivot_lows else None

    @property
    def previous_pivot_high(self) -> SwingPoint | None:
        return self.pivot_highs[-2] if len(self.pivot_highs) >= 2 else None

    @property
    def previous_pivot_low(self) -> SwingPoint | None:
        return self.pivot_lows[-2] if len(self.pivot_lows) >= 2 else None

    @property
    def higher_low_confirmed(self) -> bool:
        latest = self.latest_pivot_low
        previous = self.previous_pivot_low
        return latest is not None and previous is not None and latest.value > previous.value

    @property
    def higher_high_confirmed(self) -> bool:
        latest = self.latest_pivot_high
        previous = self.previous_pivot_high
        return latest is not None and previous is not None and latest.value > previous.value


def detect_swing_structure(
    highs: list[Decimal], lows: list[Decimal], left: int = 2, right: int = 2
) -> SwingStructure:
    if left < 1 or right < 1:
        raise ValueError("left and right pivot windows must be at least 1.")
    if len(highs) != len(lows):
        raise ValueError("highs and lows must have the same length.")

    pivot_highs: list[SwingPoint] = []
    pivot_lows: list[SwingPoint] = []
    for index in range(left, len(highs) - right):
        high_window = highs[index - left : index + right + 1]
        low_window = lows[index - left : index + right + 1]
        high = highs[index]
        low = lows[index]

        if high == max(high_window) and high_window.count(high) == 1:
            pivot_highs.append(SwingPoint(index=index, value=high))
        if low == min(low_window) and low_window.count(low) == 1:
            pivot_lows.append(SwingPoint(index=index, value=low))

    return SwingStructure(pivot_highs=pivot_highs, pivot_lows=pivot_lows)


def latest_meaningful_swing_low(
    highs: list[Decimal], lows: list[Decimal], fallback_lookback: int = 20
) -> Decimal | None:
    structure = detect_swing_structure(highs, lows)
    latest = structure.latest_pivot_low
    if latest is not None:
        return latest.value
    recent_lows = lows[-fallback_lookback:]
    return min(recent_lows) if recent_lows else None


def latest_meaningful_swing_high(
    highs: list[Decimal], lows: list[Decimal], fallback_lookback: int = 20
) -> Decimal | None:
    structure = detect_swing_structure(highs, lows)
    latest = structure.latest_pivot_high
    if latest is not None:
        return latest.value
    recent_highs = highs[-fallback_lookback:]
    return max(recent_highs) if recent_highs else None

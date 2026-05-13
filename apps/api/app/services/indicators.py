from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.models.market_data import MarketDataCandle

EMA_PERIODS = (20, 50, 200)
RSI_PERIOD = 14
ATR_PERIOD = 14
VOLUME_AVG_PERIOD = 20


@dataclass(frozen=True)
class IndicatorInputCandle:
    timestamp: datetime
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


@dataclass(frozen=True)
class IndicatorSnapshotValues:
    timestamp: datetime
    ema20: Decimal | None
    ema50: Decimal | None
    ema200: Decimal | None
    rsi14: Decimal | None
    atr14: Decimal | None
    volume_avg20: Decimal | None
    relative_volume: Decimal | None
    swing_high: Decimal | None = None
    swing_low: Decimal | None = None
    trend_state: None = None
    structure_state: None = None

    def to_indicator_snapshot_kwargs(self) -> dict[str, object]:
        return {
            "timestamp": self.timestamp,
            "ema20": self.ema20,
            "ema50": self.ema50,
            "ema200": self.ema200,
            "rsi14": self.rsi14,
            "atr14": self.atr14,
            "volume_avg20": self.volume_avg20,
            "relative_volume": self.relative_volume,
            "swing_high": self.swing_high,
            "swing_low": self.swing_low,
            "trend_state": self.trend_state,
            "structure_state": self.structure_state,
        }


def calculate_indicator_snapshots(
    candles: list[IndicatorInputCandle],
) -> list[IndicatorSnapshotValues]:
    ordered_candles = sorted(candles, key=lambda candle: candle.timestamp)
    closes = [candle.close for candle in ordered_candles]
    highs = [candle.high for candle in ordered_candles]
    lows = [candle.low for candle in ordered_candles]
    volumes = [candle.volume for candle in ordered_candles]

    ema_by_period = {period: calculate_ema(closes, period) for period in EMA_PERIODS}
    rsi14 = calculate_rsi(closes, RSI_PERIOD)
    atr14 = calculate_atr(highs, lows, closes, ATR_PERIOD)
    volume_avg20 = calculate_simple_moving_average(volumes, VOLUME_AVG_PERIOD)

    snapshots: list[IndicatorSnapshotValues] = []
    for index, candle in enumerate(ordered_candles):
        volume_average = volume_avg20[index]
        relative_volume = None
        if volume_average is not None and volume_average != 0:
            relative_volume = candle.volume / volume_average

        snapshots.append(
            IndicatorSnapshotValues(
                timestamp=candle.timestamp,
                ema20=ema_by_period[20][index],
                ema50=ema_by_period[50][index],
                ema200=ema_by_period[200][index],
                rsi14=rsi14[index],
                atr14=atr14[index],
                volume_avg20=volume_average,
                relative_volume=relative_volume,
            )
        )

    return snapshots


def indicator_input_from_model(candle: MarketDataCandle) -> IndicatorInputCandle:
    return IndicatorInputCandle(
        timestamp=candle.timestamp,
        high=candle.high,
        low=candle.low,
        close=candle.close,
        volume=candle.volume,
    )


def calculate_ema(values: list[Decimal], period: int) -> list[Decimal | None]:
    if period <= 0:
        raise ValueError("EMA period must be positive.")

    output: list[Decimal | None] = [None] * len(values)
    if len(values) < period:
        return output

    smoothing = Decimal(2) / Decimal(period + 1)
    ema = sum(values[:period]) / Decimal(period)
    output[period - 1] = ema

    for index in range(period, len(values)):
        ema = (values[index] - ema) * smoothing + ema
        output[index] = ema

    return output


def calculate_rsi(values: list[Decimal], period: int = RSI_PERIOD) -> list[Decimal | None]:
    if period <= 0:
        raise ValueError("RSI period must be positive.")

    output: list[Decimal | None] = [None] * len(values)
    if len(values) <= period:
        return output

    gains: list[Decimal] = []
    losses: list[Decimal] = []
    for index in range(1, period + 1):
        change = values[index] - values[index - 1]
        gains.append(max(change, Decimal(0)))
        losses.append(max(-change, Decimal(0)))

    average_gain = sum(gains) / Decimal(period)
    average_loss = sum(losses) / Decimal(period)
    output[period] = rsi_from_average_gain_loss(average_gain, average_loss)

    for index in range(period + 1, len(values)):
        change = values[index] - values[index - 1]
        gain = max(change, Decimal(0))
        loss = max(-change, Decimal(0))
        average_gain = ((average_gain * Decimal(period - 1)) + gain) / Decimal(period)
        average_loss = ((average_loss * Decimal(period - 1)) + loss) / Decimal(period)
        output[index] = rsi_from_average_gain_loss(average_gain, average_loss)

    return output


def calculate_atr(
    highs: list[Decimal], lows: list[Decimal], closes: list[Decimal], period: int = ATR_PERIOD
) -> list[Decimal | None]:
    if period <= 0:
        raise ValueError("ATR period must be positive.")
    if not (len(highs) == len(lows) == len(closes)):
        raise ValueError("ATR inputs must have the same length.")

    output: list[Decimal | None] = [None] * len(closes)
    if len(closes) < period:
        return output

    true_ranges = calculate_true_ranges(highs, lows, closes)
    atr = sum(true_ranges[:period]) / Decimal(period)
    output[period - 1] = atr

    for index in range(period, len(closes)):
        atr = ((atr * Decimal(period - 1)) + true_ranges[index]) / Decimal(period)
        output[index] = atr

    return output


def calculate_simple_moving_average(
    values: list[Decimal], period: int
) -> list[Decimal | None]:
    if period <= 0:
        raise ValueError("Moving average period must be positive.")

    output: list[Decimal | None] = [None] * len(values)
    if len(values) < period:
        return output

    window_sum = sum(values[:period])
    output[period - 1] = window_sum / Decimal(period)

    for index in range(period, len(values)):
        window_sum += values[index] - values[index - period]
        output[index] = window_sum / Decimal(period)

    return output


def calculate_true_ranges(
    highs: list[Decimal], lows: list[Decimal], closes: list[Decimal]
) -> list[Decimal]:
    if not (len(highs) == len(lows) == len(closes)):
        raise ValueError("True range inputs must have the same length.")

    true_ranges: list[Decimal] = []
    for index, high in enumerate(highs):
        low = lows[index]
        if index == 0:
            true_ranges.append(high - low)
            continue

        previous_close = closes[index - 1]
        true_ranges.append(
            max(
                high - low,
                abs(high - previous_close),
                abs(low - previous_close),
            )
        )

    return true_ranges


def rsi_from_average_gain_loss(average_gain: Decimal, average_loss: Decimal) -> Decimal:
    if average_loss == 0:
        if average_gain == 0:
            return Decimal("50")
        return Decimal("100")

    relative_strength = average_gain / average_loss
    return Decimal("100") - (Decimal("100") / (Decimal("1") + relative_strength))

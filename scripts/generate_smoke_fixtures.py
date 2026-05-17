"""Generate deterministic sample/paper CSV fixtures for the MVP smoke test.

Output is committed under test-data/csv/. Re-run this script if the smoke test
workflow needs to be reproduced from scratch — output is fully deterministic.

The generated data is NOT market data. It is a synthetic, deterministic curve
intended only for exercising the CSV import and analysis pipeline locally.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

HEADER = "time,open,high,low,close,volume\n"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "test-data" / "csv"


def synthesize(index: int) -> tuple[float, float, float, float, int]:
    """Produce a deterministic OHLCV tuple from a candle index.

    Pattern: gentle uptrend + sinusoidal swing to give the analysis pipeline
    enough variance to compute trend, momentum, and volatility indicators.
    """
    base = 100.0 + index * 0.20 + 10.0 * math.sin(index / 10.0)
    open_ = round(base, 2)
    close = round(base + math.cos(index / 6.0) * 1.5, 2)
    high = round(max(open_, close) + 1.25, 2)
    low = round(min(open_, close) - 1.25, 2)
    volume = 1000 + (index * 37 % 500)
    return open_, high, low, close, volume


def generate(filename: str, start: datetime, step: timedelta, count: int) -> None:
    rows: list[str] = [HEADER]
    cursor = start
    for index in range(count):
        open_, high, low, close, volume = synthesize(index)
        time_str = cursor.strftime("%Y-%m-%dT%H:%M:%SZ")
        rows.append(f"{time_str},{open_},{high},{low},{close},{volume}\n")
        cursor += step

    path = OUTPUT_DIR / filename
    path.write_text("".join(rows), encoding="utf-8", newline="")
    print(f"wrote {path} ({count} candles)")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    start_utc = datetime(2024, 1, 1, tzinfo=timezone.utc)

    generate("sample_paper_1d.csv", start_utc, timedelta(days=1), count=250)
    generate("sample_paper_4h.csv", start_utc, timedelta(hours=4), count=250)
    generate("sample_paper_1w.csv", start_utc, timedelta(days=7), count=60)


if __name__ == "__main__":
    main()

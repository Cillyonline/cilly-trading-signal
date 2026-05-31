# Sample/Paper CSV Fixtures

These files are deterministic, synthetic samples used by MVP smoke and browser
clickthrough tests. They are **not** market data, **not** broker output, and
**not** suitable for any backtest, profitability claim, or trading decision.

## Files

| File | Timeframe | Candles | Purpose |
| --- | --- | --- | --- |
| `sample_paper_1w.csv` | 1W | 60 | Weekly context for smoke import |
| `sample_paper_1d.csv` | 1D | 250 | Daily setup data for smoke analysis |
| `sample_paper_4h.csv` | 4H | 250 | Intraday trigger data for smoke analysis |
| `screener_smoke.csv` | n/a | 2 rows | Fake TradingView-style screener candidates for `/screener` upload |

The candle count exceeds the indicator warmup so that EMA20/EMA50/EMA200,
RSI14, and ATR14 produce non-null values during the analysis step.

## OHLCV Data Shape

- Header: `time,open,high,low,close,volume` (TradingView export compatible).
- Timestamps: ISO-8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`).
- OHLC values: generated from a sinusoidal curve around a gentle linear
  uptrend so the strategies have enough variance to evaluate.
- Volume: deterministic mod-based integer.

The series is intentionally regular so smoke runs are reproducible.

## Screener Data Shape

- Header: `Symbol,Name,Exchange,Sector,Price,Change %,Volume,Relative Volume,Market Cap,RSI (14)`.
- Symbols use the `SMOKE-SCR-` prefix and `SAMPLE` exchange.
- Rows are review candidates only. Uploading the screener fixture must not
  automatically create analyses, signals, trades, alerts, broker actions, or
  orders.

## Usage

1. Create a watchlist item for a clearly fake symbol such as
   `SMOKE-PAPER-001` (asset class `stock`, exchange `SAMPLE`).
2. On the Import page, upload each CSV with the matching timeframe.
3. After all three timeframes are imported, run analysis from the
   import history to generate signals for review.
4. On the Screener page, upload `screener_smoke.csv` to create fake review
   candidates and optionally convert them to watchlist entries manually.

Refer to `docs/MVP_SMOKE_TEST.md` and
`docs/FINAL_BROWSER_CLICKTHROUGH_CHECKLIST.md` for the full workflows.

## Regenerating

The fixtures are produced by `scripts/generate_smoke_fixtures.py`. Output is
deterministic — re-running the script reproduces these exact files.

```powershell
python scripts/generate_smoke_fixtures.py
```

## Safety Reminder

These fixtures exist only to exercise the import, screener, and analysis
pipelines. The app remains a manual documentation cockpit and does not execute
orders. No profitability or backtest claim is implied by the presence of this
data.

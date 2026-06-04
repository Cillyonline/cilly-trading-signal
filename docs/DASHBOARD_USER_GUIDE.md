# Dashboard User Guide

## Purpose

The dashboard is the cockpit landing page for a single owner/operator. It summarizes stored review data and points to the next manual review tasks.

The dashboard is not a live trading screen, broker screen, profitability dashboard, strategy-validation report, buy/sell instruction, or automatic execution workflow.

## How To Read The Dashboard

Use the dashboard in this order:

1. Check data quality first.
2. Check alert delivery issues.
3. Review triggered or armed signals manually.
4. Review active risk and concentration warnings before adding more exposure.
5. Document open trades and complete journal reviews after close.
6. Use performance only as historical documentation, not prediction.

If any high-risk data quality, alert, or risk warning is unclear, stop and investigate before treating any setup as reviewable.

## Dashboard Cards

### Watchlist Items

Shows how many symbols are available as the analysis base.

Operator interpretation:

- A higher count only means more symbols are tracked.
- It does not mean those symbols have fresh data, valid setups, or tradeable signals.
- Open `/watchlist` to check source, freshness, benchmark context, and sync state.

Stop points:

- Missing symbol metadata.
- Wrong asset class.
- Unknown or stale market data.
- Missing benchmark context for review workflows that need it.

### Market Data Issues

Counts missing, stale, unknown, failed, or partial market-data states.

Operator interpretation:

- This is one of the first dashboard cards to review.
- Any non-zero value means the data context needs manual inspection.
- Failed and partial states are stronger stop points than stale states.

What not to infer:

- `0` issues does not prove live or realtime data.
- Freshness is context for stored data only.
- Fresh data does not imply a valid setup.

### Signals To Review

Counts stored signals with statuses that need manual review, especially `armed` or `triggered`.

Operator interpretation:

- These are review prompts, not instructions.
- Triggered signals still require full context, setup, trigger, and risk review.
- No-Trade reasons and stale warnings remain valid conservative blockers.

What not to infer:

- A triggered or armed signal is not a buy instruction.
- The app does not create trades, position sizes, broker actions, or orders from this card.

### Screener Candidates

Shows stored TradingView screener rows still marked as candidates.

Operator interpretation:

- Screener rows are prefilter candidates only.
- They are not analyzed setups and not recommendations.
- Use `/screener` to inspect candidate quality, duplicates, rejected rows, validation errors, and explicit Watchlist conversion.

Stop points:

- Validation errors.
- Duplicate or rejected status.
- Insufficient context to intentionally add the symbol to the Watchlist.

### Active Risk

Shows documented risk for active trade statuses compared with configured risk limits.

Operator interpretation:

- This is risk documentation for manually logged trades.
- `warning` means active documented risk exceeds or approaches configured boundaries.
- `unknown` means one or more active trades have incomplete risk data.

Stop points:

- `warning` status before opening or logging more trades.
- `unknown` status until missing entry, stop, size, or risk data is corrected.
- Any mismatch between actual broker position and manually logged app state.

What not to infer:

- The app does not enforce broker risk.
- The app does not size positions automatically.
- The card does not know real account exposure unless the operator manually documented it accurately.

### Concentration

Shows simple active-trade asset concentration warnings.

Operator interpretation:

- Warnings mean active documented exposure may be clustered by asset class or related grouping.
- This is a simple review prompt, not a portfolio optimizer.

Stop points:

- Concentration warnings before adding related exposure.
- Missing or incorrect trade classification.

### Correlation Proxies

Shows simple proxy warnings for active exposure clusters.

Operator interpretation:

- This is not statistical correlation modelling.
- It is a conservative prompt to manually inspect related exposure.

Stop points:

- Proxy warnings without a manual operator decision.
- Unknown proxy state due to incomplete data.

### Alert Issues

Counts pending or failed alert delivery events.

Operator interpretation:

- Alerts are review prompts only.
- Failed or pending delivery should be inspected before relying on notification coverage.

What not to infer:

- Alert delivery is not trade execution.
- Alert text must not be read as buy/sell advice.
- Telegram or webhook support does not imply broker readiness.

### Documented Total R

Shows R-multiple results from manually documented closed trades.

Operator interpretation:

- This is historical process documentation.
- Use it to review trade logging quality, journal quality, and process consistency.

What not to infer:

- It is not a profitability claim.
- It is not a backtest.
- It is not expectancy, win-rate, benchmark outperformance, or strategy validation.

### Reviews Needed

Counts closed trades that still need journal review.

Operator interpretation:

- This is process debt.
- Complete journal review before treating performance evidence as complete.

Stop points:

- Closed trades without review when evaluating process quality.
- Private or emotionally sensitive notes that should not be copied into issues, screenshots, or shared evidence.

## Review Priorities Panel

The Review Priorities panel ranks the next manual review tasks. It can show up to five priorities.

Priority order is conservative:

1. Failed or partial market data.
2. Other market data freshness problems.
3. Pending or failed alert delivery.
4. Triggered setups.
5. Armed setups.
6. Open trade documentation.
7. Active risk warnings or incomplete active risk data.
8. Asset concentration warnings.
9. Correlation proxy warnings.
10. Missing journal reviews after close.

Use red priorities as immediate blockers. Use yellow priorities as manual review warnings. Use slate or emerald priorities as normal review prompts.

## Market Data Quality Panel

The Market Data Quality panel breaks down Watchlist data into:

- `Missing`: no stored market data.
- `Stale`: stored data exists but is old relative to expected freshness.
- `Unknown`: freshness cannot be confidently determined.
- `Failed`: recent sync/import failed.
- `Partial`: sync/import partially succeeded.
- `Fresh`: stored data is current enough for the app's freshness model.

Operator rule:

- Treat `missing`, `unknown`, `failed`, and `partial` as blockers for current setup review.
- Treat `stale` as a strong warning that requires manual context.
- Treat `fresh` as necessary but not sufficient.

## MVP Workflows Panel

This is a navigation map, not a task recommendation engine.

Use it to open:

- Watchlist: maintain symbol universe and data context.
- CSV Import: import stored OHLCV and run analysis deliberately.
- Signals: inspect generated setup cards and No-Trade reasons.
- Alerts: audit webhook and notification records.
- Trades: manually document externally executed trades.
- Performance: review historical documented R and active risk.
- Review Batches: collect paper/historical calibration evidence.

## CSV Import Workflow

Use `/import` for stored OHLCV data. CSV remains a supported manual baseline and
fallback; it is not a live data feed and does not place orders.

Bulk workflow:

1. Select the default Watchlist symbol and Timeframe for context.
2. Choose one or more TradingView-compatible CSV files.
3. Review the CSV mapping table for detected symbol, exchange, and timeframe.
4. Correct every row that is ambiguous or mapped to the wrong Watchlist symbol or
   Timeframe.
5. Submit the import manually.
6. Review Import Readiness by symbol as a planning view across saved usable imports
   and the current mapping preview.
7. Use the CSV-Arbeitsplan to separate weekly universe updates, daily active-review
   updates, and targeted `4H` trigger-list updates.
8. Click `Vollstaendige Symbole analysieren` only when you intentionally want to
   batch-analyze complete symbols.
9. Read skipped-symbol reasons and Ampel results before technical metrics.

Filename rules:

- Examples: `BATS_AAPL_1D.csv`, `BATS_AAPL_240.csv`, `GETTEX_ABEA, 1W.csv`,
  `AAPL_1D.csv`.
- `1W` maps to weekly, `1D` maps to daily, and `240` or `4H` maps to four-hour.
- The mapping table starts from detected filenames, but the operator must confirm or
  correct each target Watchlist symbol and Timeframe before import.

### 12-File CSV Batch Walkthrough

Use this walkthrough for a complete four-symbol review batch. The filenames are
public examples only; do not use private broker/account exports.

Example file set:

| Symbol | Weekly | Daily | 4H |
| --- | --- | --- | --- |
| `AAPL` | `BATS_AAPL_1W.csv` | `BATS_AAPL_1D.csv` | `BATS_AAPL_240.csv` |
| `MSFT` | `BATS_MSFT_1W.csv` | `BATS_MSFT_1D.csv` | `BATS_MSFT_240.csv` |
| `NVDA` | `BATS_NVDA_1W.csv` | `BATS_NVDA_1D.csv` | `BATS_NVDA_240.csv` |
| `GOOG` | `BATS_GOOG_1W.csv` | `BATS_GOOG_1D.csv` | `BATS_GOOG_240.csv` |

Step-by-step:

1. Confirm all four symbols already exist in the Watchlist.
2. Select all 12 CSV files in one file picker action.
3. In `CSV-Zuordnung vor Import`, verify each row shows the intended target symbol.
4. Confirm `1W`, `1D`, and `240 = 4H` are mapped correctly.
5. Correct any row that says `Symbol waehlen`, `Waehlen`, `unklar`, or the wrong
   target symbol/timeframe.
6. Keep the import blocked until every row says `Bereit`.
7. Click `CSV-Dateien importieren` once.
8. Review per-file results; one failed file does not prove the other files failed or
   succeeded incorrectly.
9. Review Import Readiness by symbol. A symbol is complete only when saved usable
   imports cover `1W`, `1D`, and `4H`.
10. Click `Vollstaendige Symbole analysieren` only after the intended complete symbols
    are visible.
11. Use the batch summary and filters to review `Paper-Kandidat`, `Beobachten`,
    `Kein Trade`, `Datenproblem`, skipped, failed, and waiting states.
12. Treat skipped reasons as valid stop points, not annoyances to bypass.

Common error cases:

- `240` is left unmapped: select `4H` manually.
- A file name contains an exchange or punctuation variant the app cannot parse:
  choose the Watchlist symbol and Timeframe manually.
- A symbol is missing from Watchlist: add the symbol intentionally first, then return
  to import. Do not map it to a different symbol.
- Import Readiness still shows missing timeframes after upload: confirm the saved
  per-file import result, not only the filename preview.
- Analyze-All skips a symbol: read the missing-timeframe reason and fix data before
  expecting analysis.

Error interpretation:

- Failed files do not make other files successful or failed automatically; inspect
  the per-file result list.
- Missing saved/imported timeframes make symbols incomplete and skipped by Analyze-All.
- A filename preview can make a symbol look planned-complete before submit; do not
  treat it as usable data until the import result is saved and valid.
- Failed, skipped, zero-candle, stale, partial, or unknown data should be treated
  conservatively and not as actionable.
- Do not upload private broker exports, account history, fills, balances, cookies,
  secrets, personal notes, or production data for evidence.

## Signal Radar Decisions

The Signal Radar and Import analysis use a German traffic-light layer above the
technical signal fields:

- `Paper-Kandidat` / green: strong enough for manual paper review, not a real trade instruction.
- `Beobachten` / yellow: interesting, but wait for cleaner confirmation.
- `Kein Trade` / red: rejected by a required filter or quality blocker.
- `Datenproblem` / gray: missing, stale, failed, partial, or insufficient data blocks review.

Use the Ampel first, then inspect technical fields such as score, risk flags,
No-Trade reasons, trigger, stop, and target. A green or yellow decision is still
only a review prompt; external execution remains manual and outside the app.

### Active Review Shortlist

The Signals page includes an Active Review shortlist for daily work. It ranks a small
set of current review cards from existing signal data:

- `Paper-Kandidat`: strongest manual paper-review candidates.
- `Am Trigger` and `Nah dran`: symbols that may need targeted `4H` CSV refresh and
  detail review.
- `Beobachten`: interesting symbols to keep on the active list.
- `Datenproblem`: stale or blocked data that should be fixed before review.

The shortlist does not create analysis, alerts, trades, orders, broker actions, or
buy/sell instructions. It is only a practical worklist before reading the full Radar
Rangliste.

## Cockpit Snapshot

The snapshot shows recent signals, active trades, and review-needed trades.

Operator interpretation:

- It is a quick reminder of current manual work.
- It is not exhaustive workflow evidence.
- Open the linked workflow pages before making any manual decision.

## Empty Dashboard State

If the dashboard has no data, start with:

1. Add sample-only Watchlist symbols.
2. Import sample OHLCV CSV data.
3. Run analysis from imported data.
4. Review signals and No-Trade outcomes.
5. Optionally log sample/paper trades for workflow testing.

Do not use real account data during smoke tests or public/shared evidence collection.

## Dashboard Stop Conditions

Stop and create a sanitized follow-up issue if:

- Dashboard cannot load after API health is green.
- Protected dashboard data remains visible after logout.
- A card or panel implies buy/sell instruction, trading advice, automatic execution, broker readiness, live/realtime data, profitability, or strategy validation.
- Data quality, alert delivery, or active-risk warnings cannot be explained with current docs.
- Any dashboard evidence would require exposing private symbols, account values, journal text, cookies, tokens, secrets, or database URLs.

## Evidence Notes

When recording dashboard evidence for local or VPS review, include only:

- Date and environment.
- Branch or commit.
- Browser viewport type.
- Pass/fail/blocked state.
- Sanitized fake symbols or aggregate counts.
- Follow-up issue links.

Do not include screenshots or raw outputs containing private data, cookies, tokens, local storage, account data, database URLs, secrets, or private journal notes.

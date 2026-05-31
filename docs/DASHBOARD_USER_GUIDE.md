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

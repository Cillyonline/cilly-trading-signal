# Owner/Operator Cockpit Manual

## Purpose

This manual explains how a single owner/operator should use the cockpit end to end for controlled internal review. It is designed as a practical companion for local smoke checks and later private VPS staging validation.

This manual is not trading advice, a production-readiness statement, broker-readiness evidence, real-money readiness evidence, strategy validation, profitability evidence, live/realtime market-data evidence, or approval for automatic execution.

## Core Rules

- The app supports review and documentation only.
- All trade execution, order placement, order modification, and broker/account actions happen outside the app.
- Signals and alerts are prompts for manual review, not buy/sell instructions.
- `No Trade`, stale data, missing benchmark context, failed/partial provider states, ignored/rejected screener candidates, and unclear review outcomes are valid stop points.
- Use sample, synthetic, or paper data for smoke tests, PR evidence, browser clickthroughs, and VPS validation evidence.
- Do not share secrets, cookies, session data, `.env` values, database URLs, raw logs, private symbols, private journal text, account data, or screenshots with sensitive data.

## Signal Radar Ampel

The cockpit uses German traffic-light decisions to make review outcomes easier to
read. They summarize the stored signal context; they do not change the strategy
rules and are not trading instructions.

| Ampel | Label | Meaning | Operator action |
| --- | --- | --- | --- |
| Green | `Paper-Kandidat` | The setup is strong enough for manual paper review. | Review context, risk, and chart manually. No automatic or real trade is created. |
| Yellow | `Beobachten` | The setup is interesting but not strong enough for a clear review decision. | Keep on watchlist and wait for cleaner confirmation. |
| Red | `Kein Trade` | A required filter or quality blocker rejects the setup. | Do not trade and do not log as paper trade. Recheck after new data or changed context. |
| Gray | `Datenproblem` | Required data is missing, stale, failed, partial, or not sufficient. | Fix/import/sync data first. Treat analysis as blocked. |

Operator rule: green and yellow mean "look closer" only. They never mean buy,
sell, place an order, or connect to a broker.

## Recommended Operator Flow

Use this order for a clean sample-only review session:

1. Log in.
2. Review the dashboard.
3. Check Watchlist data context.
4. Import or verify Screener candidates.
5. Import stored OHLCV data.
6. Run or review generated signal analysis.
7. Review Signals and Signal Detail.
8. Create or update Review Batches.
9. Log sample/paper Trades manually.
10. Add Trade Detail events, close documentation, and journal review.
11. Review Performance/Risk.
12. Audit Alerts.
13. Check Settings.
14. Log out and verify protected data is unavailable.

## 1. Login

Open `/login` and sign in with the configured single admin account.

Operator checks:

- Login page loads without exposing credentials.
- Session uses the app login flow, not copied browser storage or tokens.
- For shared evidence, record only pass/fail status, not cookies or session details.

Stop if:

- Login requires exposing secrets in docs, chat, screenshots, or issues.
- Protected pages are accessible without login.
- Logout later does not clear protected access.

## 2. Dashboard

Open `/` after login.

Use [Dashboard User Guide](DASHBOARD_USER_GUIDE.md) for detailed card interpretation.

Operator checks:

- Market Data Issues are reviewed before Signals.
- Alert Issues are reviewed before relying on notification coverage.
- Active Risk, Concentration, and Correlation Proxy warnings are reviewed before adding exposure.
- Reviews Needed is treated as process debt.

Stop if:

- Dashboard cannot load while API health is expected to be green.
- Dashboard copy implies live/realtime, profitability, trading advice, or automatic execution.
- A card warning cannot be explained with current docs.

## 3. Watchlist

Open `/watchlist`.

Purpose:

- Maintain the symbol universe.
- Check asset class, exchange/source context, market-data freshness, and benchmark context.

Operator checks:

- Symbols are intentional and sample-only during evidence runs.
- Asset class is correct: `stock` or `crypto`.
- Freshness/source states are understood before analysis.
- Benchmark context is present where required by review workflows.

Stop if:

- Symbol metadata is wrong.
- Market data is missing, unknown, failed, partial, or stale without accepted manual context.
- You would need private watchlist data for the evidence run.

## 4. Screener

Open `/screener`.

Purpose:

- Import TradingView Screener CSV snapshots as review candidates.
- Validate rows.
- Explicitly convert chosen candidates to Watchlist items.

Operator checks:

- Screener rows are candidates only, not recommendations.
- Import errors are reviewed and not ignored.
- Bulk actions change review status only.
- Watchlist conversion is explicit and manual.
- Conversion does not create analysis, signals, trades, alerts, broker actions, or orders automatically.

Stop if:

- CSV includes private or real account data during evidence runs.
- Import validation errors cannot be explained.
- UI copy implies a screener candidate is tradeable or recommended.

## 5. Market Data Import

Open `/import`.

Purpose:

- Import stored OHLCV CSV data for Watchlist symbols.
- Run analysis deliberately from stored data.
- Use bulk CSV import as the low-friction fallback when provider sync is unavailable,
  disabled, stale, partial, or unsupported for the needed timeframe.

Operator checks:

- Use sample CSV fixtures for smoke/evidence runs.
- Confirm timeframe and symbol match the intended sample symbol.
- For bulk imports, select all intended CSV files together, then review the filename
  mapping table before submitting.
- Supported TradingView-style filename patterns include exchange-prefixed names such
  as `BATS_AAPL_1D.csv`, `BATS_AAPL_240.csv`, and comma/space variants such as
  `GETTEX_ABEA, 1W.csv`; `240` is interpreted as `4H`.
- The CSV mapping table starts from filename detection but must be reviewed by the
  operator. Correct every row where symbol or timeframe is ambiguous before import.
- Use Import Readiness as a planning view across saved usable imports and the
  current mapping preview. Before batch analysis, confirm the files were actually
  submitted and the saved import results are usable for `1W`, `1D`, and `4H`.
- For a 12-file batch, use four symbols times three timeframes: `1W`, `1D`, and
  `240`/`4H`. Example: `BATS_AAPL_1W.csv`, `BATS_AAPL_1D.csv`,
  `BATS_AAPL_240.csv` plus the same set for three other public/sample symbols.
- Treat a blocked mapping row as a stop point. Do not import until each row is mapped
  to the intended Watchlist symbol and Timeframe.
- Use `Vollstaendige Symbole analysieren` only when you want to explicitly analyze
  all complete imported symbols. Incomplete symbols must stay skipped with a visible
  missing-timeframe reason.
- Use the batch summary filters to scan outcomes, but keep `Alle` as the default
  safety view so skipped, failed, and waiting states remain visible.
- Read the Ampel decision before reading technical backend metrics.
- Treat conservative `No Setup` or `No Trade` as valid output.
- Confirm analysis does not create trades or orders.
- Confirm CSV files contain public/synthetic OHLCV only, not broker exports, account
  balances, fills, private notes, or personal identifiers.

Stop if:

- Data source, timeframe, or symbol is wrong.
- Import creates unexpected private data exposure.
- Filename preview is unclear or conflicts with the manually selected symbol/timeframe.
- CSV mapping is unclear, blocked, or would require guessing the symbol/timeframe.
- Readiness marks required timeframes as missing and the workflow would require
  guessing or overriding that blocker.
- Analysis copy implies guaranteed outcome, profitability, or trading instruction.

## 6. Signals

Open `/signals`.

Purpose:

- Review the Signal Radar.
- Review the Trigger Radar as a manual attention queue for stored trigger context.
- Prioritize `Paper-Kandidat` and `Beobachten` while keeping `Kein Trade` and
  `Datenproblem` visible as valid conservative outcomes.
- Inspect setup score, status, stale state, risk flags, No-Trade reasons, and next action only after the Ampel decision is understood.

Operator checks:

- `No Trade` remains first-class and valid.
- Triggered and armed statuses are prompts for manual review only.
- `Trigger geplant`, `Nah dran`, and `Am Trigger` are German review labels, not
  execution labels.
- `Nah dran` requires manual 4H close/freshness/risk review before any external decision.
- Stale data and missing context are reviewed before acting outside the app.
- Risk flags and quality blockers are read before considering any manual external action.

Stop if:

- A signal is interpreted as a buy/sell instruction.
- A trigger or alert is interpreted as permission to enter, size, route, or automate a trade.
- Required data context is stale, missing, failed, unknown, or partial.
- Risk plan is incomplete or unclear.

## 7. Signal Detail

Open `/signals/[id]` from a signal card.

Purpose:

- Review the full signal context.
- Add sanitized review notes if needed.

Operator checks:

- Explainability and No-Trade reasons are understandable.
- Manual review notes contain no private account data.
- Signal detail still does not create trades or orders automatically.

Stop if:

- Detail context contradicts the list card.
- Notes would require private account or broker information.
- UI implies blind signal following.

## 8. Review Batches

Open `/reviews` and `/reviews/[id]`.

Purpose:

- Record historical or paper review evidence.
- Track manual labels, blockers, finding categories, corrections, and follow-up needs.

Operator checks:

- Review batches are process evidence, not backtests.
- Finding categories are evidence categories, not automatic rule changes.
- Corrections are auditable and should be used rather than deleting context.
- Follow-up drafts are reviewed for private data before filing issues.

Stop if:

- Review evidence is being treated as profitability proof.
- Private trading notes would be required.
- A rule change is implied without calibration workflow and golden-case evidence.

## 9. Trades

Open `/trades`.

Purpose:

- Manually log trades that were executed outside the app.
- Document source, risk plan, execution time, and notes.

Operator checks:

- Source is selected deliberately: Watchlist or Signal.
- Entry, stop, size, and execution time are complete.
- The app computes risk/R only for documentation.
- No broker action, order, or position sizing is created automatically.

Stop if:

- Actual broker state differs from app documentation and cannot be reconciled.
- Entry/stop/size are incomplete or incoherent.
- Logging would require exposing private account data in shared evidence.

## 10. Trade Detail

Open `/trades/[id]`.

Purpose:

- Add routine management events.
- Log manual close decisions.
- Complete journal review.

Operator checks:

- Manual management boundary is visible before action forms.
- Routine events are distinguished from close/final actions.
- Close logging documents an external manual decision only.
- Journal review records process quality, not prediction.

Stop if:

- Close action is confused with broker execution.
- Management events are missing required timestamps or prices.
- Journal notes include private/sensitive data that should not be shared.

## 11. Performance And Risk

Open `/performance`.

Purpose:

- Review documented closed trades in R-multiples.
- Review active risk, concentration warnings, and simple correlation proxies.

Operator checks:

- Performance is historical documentation only.
- Active risk warnings are reviewed before manually adding exposure outside the app.
- Incomplete risk data is corrected before relying on summaries.

What not to infer:

- No profitability claim.
- No expectancy or win-rate validation.
- No benchmark outperformance claim.
- No real-money readiness.

## 12. Alerts

Open `/alerts`.

Purpose:

- Audit webhook and notification events.
- Review delivery status and alert content boundaries.

Operator checks:

- Alerts are prompts, not instructions.
- Pending or failed delivery is reviewed.
- Telegram or webhook delivery does not imply broker execution.

Stop if:

- Alert copy reads like buy/sell advice.
- Alert delivery failure means the operator would miss required review prompts.
- External notification evidence would expose secrets or private channels.

## 13. Settings

Open `/settings`.

Purpose:

- Review risk settings and alert/test configuration.

Operator checks:

- Risk settings are documentation constraints, not automatic position sizing.
- Telegram test actions are explicit operator actions.
- No secrets are shown or copied into evidence.

Stop if:

- Settings imply automatic order execution or broker integration.
- Secret or token handling would be exposed.

## 14. Logout

Use Logout from the dashboard/header where available.

Operator checks:

- Logout succeeds.
- Protected routes or protected API data are unavailable after logout.
- Browser evidence does not expose cookies, local storage, or session values.

Stop if:

- Protected data remains available after logout.
- Logout fails repeatedly.

## Evidence Rules

For local, PR, or VPS evidence, record only:

- Date/time.
- Environment: local, disposable, or private staging.
- Commit or branch.
- Browser and viewport type.
- Data scope: sample, synthetic, or paper.
- Pass/fail/blocked steps.
- Sanitized fake symbols or aggregate counts.
- Follow-up issue links.

Never record:

- Cookies, session values, local storage, tokens, or `.env` values.
- Database URLs, backup dumps, raw logs, or provider secrets.
- Private trading symbols, account balances, broker screenshots, or private journal notes.
- Screenshots containing sensitive data.

## Before VPS Validation

Before touching private VPS staging:

1. Read [Owner/Operator Wiki](OWNER_OPERATOR_WIKI.md).
2. Read [Dashboard User Guide](DASHBOARD_USER_GUIDE.md).
3. Run or review [MVP Smoke Test](MVP_SMOKE_TEST.md) locally.
4. Prepare sample data for [Final Browser Clickthrough Checklist](FINAL_BROWSER_CLICKTHROUGH_CHECKLIST.md).
5. Confirm [VPS Environment Checklist](VPS_ENVIRONMENT_CHECKLIST.md) with the operator.
6. Confirm the current gate in [Final Internal Review Decision Gate](FINAL_INTERNAL_REVIEW_DECISION_GATE.md).

Do not begin VPS execution until the operator explicitly approves access, target, secrets handling, and any migration or service restart.

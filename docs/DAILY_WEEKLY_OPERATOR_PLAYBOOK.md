# Daily And Weekly Operator Playbook

## Purpose

This playbook turns the v4.4 CSV-first workflow into a practical routine for a
single owner/operator. It helps decide what to update and review without trying to
refresh every symbol all day.

This is not trading advice, live/realtime market-data evidence, strategy validation,
profitability evidence, broker-readiness evidence, or approval for automatic
execution.

## Working Lists

Use three working lists:

| List | Typical size | Purpose | Data focus |
| --- | --- | --- | --- |
| Universe | Up to about 200 symbols | Broad mixed-asset opportunity set. | Weekly and daily context. |
| Active review shortlist | About 20-40 symbols | Symbols worth checking in the current review cycle. | Current `1D` plus enough higher-timeframe context. |
| Trigger shortlist | About 5-15 symbols | Symbols near trigger or needing focused review. | Fresh targeted `4H` context. |

Do not try to refresh the full 200-symbol universe several times per day. That is
too much manual work and does not fit the current zero-budget provider decision.

## Weekly Preparation

Use this flow once per week, preferably on the weekend or before the next trading
week starts.

1. Review the Watchlist universe.
2. Remove obvious dead symbols only if you are sure they are no longer needed.
3. Add new candidates intentionally from screener review or manual research.
4. Export and import `1W` CSV files for the universe or the broadest practical subset.
5. Export and import `1D` CSV files for the universe or the active review subset.
6. Use Import Readiness to find symbols missing `1W`, `1D`, or `4H`.
7. Run analysis only for symbols with complete required context.
8. Build the active review shortlist from `Paper-Kandidat`, `Beobachten`, near-trigger,
   and data-problem items that are worth fixing.

Stop points:

- The export includes broker/account/fill data instead of public OHLCV candles.
- A filename maps to the wrong symbol or timeframe.
- Required timeframes are missing and would require guessing.
- The workflow starts treating the full universe as something to refresh intraday.

## Daily Review

Use this flow once per trading day, after the daily close or before your next review
session.

1. Open the dashboard and check data quality first.
2. Open `/import` and read the CSV-Arbeitsplan before selecting files.
3. Refresh `1D` CSV for the active review shortlist.
4. Review Import Readiness for the refreshed symbols.
5. Analyze complete symbols deliberately.
6. Open `/signals` and start with the Active Review shortlist.
7. Read Ampel outcomes before technical fields.
8. Move symbols into or out of the active review shortlist based on current context.
9. Identify the smaller trigger shortlist for any intraday `4H` review.

Operator interpretation:

- `Paper-Kandidat` means manual paper review candidate, not an entry instruction.
- `Beobachten` means keep watching, not trade now.
- `Kein Trade` is a valid outcome and should not be forced into a setup.
- `Datenproblem` means fix data first or ignore the symbol for this cycle.

## Trigger Shortlist Review

Use this flow only for symbols that are already near trigger or deserve focused
manual review.

1. Keep the trigger shortlist small, normally 5-15 symbols.
2. Export targeted `4H` CSV for those symbols around relevant candle closes.
3. Import the `4H` files through `/import` and verify mapping before submit.
4. Use the CSV-Arbeitsplan and Import Readiness to confirm `4H` is targeted, not a
   full-universe refresh.
5. Analyze only complete symbols.
6. Open Trigger Radar and read proximity labels as manual review priorities.
7. Check freshness, setup quality, risk flags, invalidation, and No-Trade reasons.
8. Make any external trading decision manually outside the app.

Trigger Radar order of operations:

1. Update `4H` CSV only for the small trigger shortlist.
2. Open each visible Trigger Radar card through `Detail pruefen`.
3. Confirm freshness, risk, invalidation, and No-Trade context before any external
   action.
4. Keep extra candidates in Radar-Rangliste instead of expanding the trigger shortlist
   beyond practical size.

Do not treat `Nah dran`, `Am Trigger`, an alert, or a green Ampel as a buy/sell or
entry instruction. They mean review the stored context.

## Crypto Handling

Crypto can move outside stock-market sessions, but the workflow should still stay
small and practical.

- Keep crypto trigger checks limited to the trigger shortlist.
- Refresh `4H` more often only when you are actively monitoring.
- Do not expand crypto updates into a full-universe intraday refresh loop.
- Treat stale, missing, failed, partial, and unknown data as blockers.

## What To Do When Time Is Limited

If you only have a few minutes:

1. Check dashboard data quality and alerts.
2. Review Trigger Radar for `Datenproblem`, `Nah dran`, and `Am Trigger` items.
3. Refresh `4H` only for the smallest trigger shortlist.
4. Ignore the full universe until the next scheduled weekly/daily review.

If you have a normal daily session:

1. Refresh `1D` for the active review shortlist.
2. Refresh `4H` for the trigger shortlist.
3. Analyze complete symbols.
4. Review Signal Radar and Trigger Radar.

If you have a longer weekly session:

1. Refresh `1W` and `1D` for the broader universe.
2. Clean up Watchlist and screener candidates.
3. Rebuild active review and trigger shortlists.

## Evidence And Privacy Rules

For PRs, issues, docs, chat, and screenshots, record only sanitized evidence:

- Environment class.
- Branch or commit.
- Pass/fail/blocked status.
- Aggregate counts.
- Public or redacted symbols.
- Follow-up issue links.

Never record:

- Provider keys, `.env` values, request URLs, cookies, raw logs, database URLs, or raw
  provider payloads.
- Private Watchlist symbols when the operator considers them sensitive.
- Broker exports, account balances, fills, order IDs, or account screenshots.
- Private journal notes or personal identifiers.

## Escalation Rules

Create a follow-up issue when:

- The app does not show which timeframe is missing clearly enough.
- Trigger Radar does not make the next manual review priority obvious.
- Active review still requires scanning too many symbols manually.
- A wording or UI state could be read as trading advice, buy/sell instruction, live
  data, broker readiness, or automatic execution.

Do not create an implementation shortcut that bypasses these boundaries. Keep CSV as
the baseline until provider budget, licensing, coverage, and rate limits are accepted
explicitly.

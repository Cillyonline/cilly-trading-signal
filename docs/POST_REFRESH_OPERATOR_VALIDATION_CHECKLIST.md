# Post-Refresh Operator Validation Checklist

## Purpose

This checklist validates the manual owner/operator workflow after the v5.6 data
refresh guidance. It is for local or explicitly approved private-staging checks
with sample, synthetic, or paper data only.

This checklist is not a production-readiness statement, broker-readiness claim,
real-money readiness claim, profitability claim, strategy-validation claim,
trading advice, live/realtime data claim, or approval for automatic execution.

## Safety And Evidence Rules

- Use sample, synthetic, or paper data only.
- Prefer fake symbols such as `SMOKE-REFRESH-001` for shared evidence.
- Do not use private watchlists, private CSVs, broker exports, account data,
  private journal text, provider dashboards, screenshots with sensitive data,
  cookies, session tokens, `.env` values, provider keys, request URLs, raw logs,
  raw API responses, raw provider payloads, or raw CSV rows.
- Record only route names, pass/fail/blocked status, sanitized fake/public symbol
  scope, viewport class, aggregate counts, and follow-up issue links.
- Confirm no workflow creates analysis, signals, trades, alerts, orders, broker
  actions, position sizing, or executions automatically unless an explicit manual
  operator action is required and performed.

Use `docs/POST_REFRESH_VALIDATION_EVIDENCE_FORMAT.md` when recording evidence for
this checklist.

## Preconditions

- Current branch or commit is known.
- Local stack or approved private-staging target is running and healthy.
- Operator can log in through the normal app login flow.
- Test data is sample/synthetic/paper only.
- Any provider sync used in the check is guarded, manual, and clearly within
  documented symbol/timeframe scope.
- TradingView CSV remains available as fallback when provider coverage, mapping,
  entitlement, rate-limit, payload quality, or freshness is unclear.

## Validation Matrix

Record each step as `pass`, `fail`, `blocked`, or `not run`.

| Step | Route or workflow | Expected result |
| --- | --- | --- |
| 1 | `/login` | Login succeeds without exposing credentials, cookies, session values, or local storage. |
| 2 | Dashboard `/` | Data-quality and alert/risk cards remain decision-support only. No live/realtime, broker, profitability, or auto-execution wording appears. |
| 3 | `/watchlist` sample symbol | Fake/sample symbol is active and has correct asset class. No private symbols are required for validation. |
| 4 | `/import` CSV-Arbeitsplan | Weekly, daily, and trigger refresh modes are visible and frame refresh as manual CSV-first work. |
| 5 | `/import` CSV mapping | Sample CSV file mapping is reviewed before submit. Ambiguous symbol/timeframe mapping is treated as a stop point. |
| 6 | `/import` CSV refresh | Sample `1W`, `1D`, and `4H` CSV imports persist as stored market data without creating analysis, signals, trades, alerts, orders, or broker actions automatically. |
| 7 | `/import` readiness | Readiness shows present/missing timeframes and clear manual next actions. Missing, stale, failed, partial, skipped, and unknown states remain blockers or fallback prompts. |
| 8 | `/import` provider fallback wording | Provider sync panel remains advanced/manual. Failed, partial, skipped, rate-limit, entitlement, unsupported, or unclear provider states point back to CSV fallback or skip. |
| 9 | Explicit manual analysis | Analysis starts only after an operator action. Complete sample symbols may be analyzed; incomplete symbols remain skipped or blocked. |
| 10 | Analysis result interpretation | `Paper-Kandidat`, `Beobachten`, `Kein Trade`, and `Datenproblem` are review labels only, not trade instructions. |
| 11 | `/signals` list | Active Review and Trigger Radar load with stored-data context. Trigger labels remain manual review priorities only. |
| 12 | `/signals/[id]` detail | Signal detail explains reasoning, risk flags, No-Trade reasons, and next action without buy/sell wording. |
| 13 | `/trades` manual sample trade | Any trade record is created only by explicit manual action and uses sample/paper values. No broker action or order routing appears. |
| 14 | `/trades/[id]` management and journal | Events, close documentation, and journal notes remain documentation only. No private trading notes are required. |
| 15 | `/performance` | R-multiple summaries remain historical/paper documentation, not profitability evidence. |
| 16 | `/alerts` | Alerts are review prompts only. No buy/sell instruction or broker execution path appears. |
| 17 | Logout | Logout succeeds and protected data is unavailable after logout. |

## Mobile/Narrow Viewport Spot Check

When feasible, repeat or spot-check these views at a narrow mobile viewport:

- `/import` CSV-Arbeitsplan, mapping, readiness, and manual analysis action.
- `/signals` Active Review and Trigger Radar cards.
- `/signals/[id]` signal detail safety wording.
- `/trades` manual trade creation and `/trades/[id]` management/journal groups.

Mobile validation passes only if safety wording and manual-action boundaries remain
visible enough to prevent interpreting the app as an execution or advice system.

## Stop Conditions

Stop validation and record only sanitized failure metadata if:

- Login, API health, migrations, or core DB-backed pages fail repeatedly.
- Any workflow requires private trading data, private CSV rows, broker data,
  provider account details, cookies, tokens, `.env` values, raw logs, raw API
  responses, raw provider payloads, or screenshots with sensitive data.
- Any UI copy implies buy/sell instruction, trading advice, profitability,
  strategy validation, live/realtime data, broker readiness, production readiness,
  or automatic execution.
- Refresh creates analysis, signals, trades, alerts, orders, broker actions,
  position sizing, or executions automatically.
- Provider sync is required to pass the validation but coverage, entitlement,
  mapping, rate-limit, or payload quality is unclear.
- Manual trade logging cannot be completed with sample/paper values only.

## Follow-Up Criteria

Create a focused follow-up issue if:

- A manual next action is unclear after missing, stale, partial, skipped, failed, or
  unknown refresh states.
- CSV fallback is not visible when provider state cannot be trusted.
- A route hides key manual-action boundaries on desktop or mobile.
- A wording issue could be read as advice, live/realtime readiness, production
  readiness, broker readiness, or automatic execution.
- A regression causes refresh or analysis to create downstream records without
  explicit operator action.

## Related Docs

- `docs/OWNER_OPERATOR_COCKPIT_MANUAL.md`
- `docs/DAILY_WEEKLY_OPERATOR_PLAYBOOK.md`
- `docs/POST_REFRESH_VALIDATION_EVIDENCE_FORMAT.md`
- `docs/DATA_REFRESH_EVIDENCE_FORMAT.md`
- `docs/BROWSER_SMOKE_EVIDENCE_FORMAT.md`
- `docs/PRIVATE_DATA_EVIDENCE_HANDLING.md`

# Final Browser Clickthrough Checklist

## Purpose

This checklist records a repeatable browser clickthrough path for the final internal owner/operator workflow. It complements the API-assisted smoke runner evidence in `docs/MVP_SMOKE_TEST.md` and is intended for local or approved private-staging review with sample, synthetic, or paper data only.

Automation has been evaluated and intentionally deferred for now. See
`docs/POST_DEPLOY_BROWSER_SMOKE_AUTOMATION_EVALUATION.md`, including the safe
dry-run browser smoke contract for any future opt-in script.

This checklist is not a production-readiness statement, broker-readiness statement, real-money readiness claim, profitability claim, strategy-validation claim, trading advice, or approval for automatic execution.

## Safety And Evidence Rules

- Use sample, synthetic, or paper data only.
- Do not use private watchlists, real account data, real journal entries, provider credentials, cookies, session tokens, `.env` values, raw logs, database URLs, or screenshots with sensitive data.
- Record pass/fail status, route names, sanitized fake symbols, timestamps, and follow-up issue links only.
- Do not paste browser cookies, local storage, session values, screenshots with personal data, or raw API responses into issues, PRs, docs, or chat.
- Treat every signal, alert, review batch, and performance view as decision support only.
- Confirm no broker action, automatic trade creation, automatic position sizing, automatic order execution, buy/sell instruction, profitability claim, live/realtime claim, or trading advice appears during the workflow.

## Prerequisites

- Review [Owner/Operator Wiki](OWNER_OPERATOR_WIKI.md), [Owner/Operator Cockpit Manual](OWNER_OPERATOR_COCKPIT_MANUAL.md), and [Dashboard User Guide](DASHBOARD_USER_GUIDE.md) before recording browser evidence.
- Docker Desktop is running and the Linux engine is reachable.
- Local `.env` exists and uses local placeholder credentials only.
- The local stack is started with the smoke runner:

```powershell
.\scripts\smoke_test.ps1 -TimeoutSeconds 180
```

- The runner has applied migrations and returned a passing API health check.
- Sample fixtures are available under `test-data/csv/`.
- For repeatable local runs, follow the sample-state guidance in
  `test-data/csv/README.md#repeatable-browser-smoke-state` and use a new fake
  symbol for each run, such as `SMOKE-PAPER-YYYYMMDD-001`.
- For Screener upload, use the sample-only fixture `test-data/csv/screener_smoke.csv`:

```csv
Symbol,Name,Exchange,Sector,Price,Change %,Volume,Relative Volume,Market Cap,RSI (14)
SMOKE-SCR-001,Smoke Screener One,SAMPLE,Technology,100.00,1.25%,100000,1.10,1000000,55.2
SMOKE-SCR-002,Smoke Screener Two,SAMPLE,Healthcare,50.00,-0.50%,80000,0.95,500000,60.1
```

## Clickthrough Steps

Record each step as `pass`, `fail`, `blocked`, or `not run`.

| Step | Route or workflow | Expected result |
| --- | --- | --- |
| 1 | `/login` | Login page loads. Local placeholder credentials work only in the local environment. |
| 2 | Authenticated landing/dashboard | Dashboard or cockpit home loads without exposing secrets or private data. Safety wording remains decision-support oriented. |
| 3 | `/watchlist` | Watchlist loads. Create or verify a clearly fake sample symbol such as `SMOKE-PAPER-001` with `SAMPLE` exchange metadata. |
| 4 | `/screener` upload | Upload `test-data/csv/screener_smoke.csv`. Accepted/rejected counts are visible and no private data appears. |
| 5 | `/screener` review results | Candidate cards/table are review candidates only, not recommendations. Filters, selected count, and bulk actions remain usable. |
| 6 | Screener-to-Watchlist conversion | Explicit conversion confirms no analysis, signal, trade, alert, broker action, or order is created automatically. Converted result shows `watchlist_added` or safe duplicate state. |
| 7 | `/import` | Import OHLCV fixtures `sample_paper_1w.csv`, `sample_paper_1d.csv`, and `sample_paper_4h.csv` for the fake Watchlist symbol with matching timeframes. |
| 8 | Import history analysis action | Run analysis from imported sample data. Conservative `No Setup` / `No Trade` remains a valid pass. |
| 9 | `/signals` | Signals list loads. Signal cards show status, score class, reasoning, risk flags, No-Trade reasons where applicable, and stale/freshness context. |
| 10 | `/signals/[id]` | Signal detail loads. Add or review a sample-only review note without turning the signal into an instruction. |
| 11 | `/reviews` | Create or open a paper/historical review batch with sample-only context. Evidence-only wording remains visible. |
| 12 | `/reviews/[id]` | Add or update a review entry using fake symbol data. Labels such as `unclear`, `too_permissive`, and `too_strict` remain process evidence only. |
| 13 | `/trades` create | Create a manual sample trade record from fake/paper values only. Manual execution/no-order boundary remains visible. |
| 14 | `/trades/[id]` management | Add a routine management note/event. Distinguish documentation from close/final actions. |
| 15 | `/trades/[id]` close | Close the sample trade as documentation only. Confirm no broker, account, or order workflow appears. |
| 16 | `/trades/[id]` journal | Add a sample journal review. Do not enter private trading notes. |
| 17 | `/performance` | Performance and risk summary loads. R-multiple output is historical/paper documentation, not forecast or profitability evidence. |
| 18 | `/alerts` | Alerts list loads. Any alert copy is a review prompt only, not a buy/sell instruction. Do not trigger external Telegram delivery unless separately scoped. |
| 19 | `/settings` | Settings page loads without exposing secrets. Risk settings remain review configuration only, not automatic position sizing. |
| 20 | Logout | Logout succeeds. Protected data is not available after logout. |

## Mobile Spot Check

Run the same checklist at a narrow phone viewport when feasible. At minimum, spot-check:

- Login and dashboard/home.
- Watchlist create or review.
- Screener upload/results/conversion.
- Signal card and signal detail.
- Review batch entry.
- Trade create and trade detail management/close/journal.
- Performance summary.

Known mobile follow-up gaps may still exist, but safety wording and manual-review boundaries must remain visible.

## Evidence Template

```markdown
## Browser Clickthrough Evidence

- Date/time:
- Operator:
- Environment: local / private staging / disposable test
- Branch or commit:
- Browser and viewport: desktop / narrow mobile / both
- Data scope: sample / synthetic / paper only
- Smoke runner status: pass / fail / not run
- API health: pass / fail / not checked
- Browser steps completed: x/20
- Failed or blocked steps:
- Follow-up issues created:
- Secrets/private data/cookies/tokens/screenshots with sensitive data included: no
- Production-readiness, broker-readiness, real-money, profitability, live/realtime, trading-advice, or automatic-execution claim made: no
```

## Stop Conditions

Stop the clickthrough and create a follow-up issue with sanitized evidence if:

- Login, migration, API health, or core DB-backed pages fail repeatedly.
- Any workflow exposes secrets, cookies, tokens, private data, or raw sensitive logs.
- Any UI copy implies buy/sell instruction, trading advice, profitability, strategy validation, live/realtime data, broker readiness, or automatic execution.
- A sample workflow creates an analysis, signal, trade, alert, broker action, or order automatically where explicit manual action is required.
- A close, journal, or performance path cannot be completed without entering private data.

## Cleanup

After local review, stop the stack with volumes preserved unless disposable reset was explicitly intended:

```powershell
.\scripts\smoke_test.ps1 -Cleanup
```

Use `-PurgeVolumes` only for local disposable data resets.

For private staging, do not reset volumes, restore backups, rotate secrets,
restart services, or delete shared sample data as a browser-smoke cleanup step
without explicit operator approval. Prefer adding a new fake symbol for the next
run and recording duplicates as acceptable sample-state evidence.

# Issue #828: seeded sample browser smoke

- Date/time UTC: 2026-09-11, approximately 20:08-20:11 UTC.
- Environment class: local, disposable Docker network and PostgreSQL database.
- Commit SHA: 508a6884a81b4c59eb103b5c170fb7b04afe1780.
- Data class: synthetic / paper only.
- Browser and viewport class: Microsoft Edge, desktop default viewport; mobile not tested.
- Result: PASS for the specified browser guidance checks.

## Setup

Built API and web images from the recorded commit using the repository Dockerfiles.
Started isolated PostgreSQL 16, API, web and Caddy containers. Only the proxy was
published, on loopback port 18280. Existing application containers, databases and
local environment files were not used or changed. Provider sync and Telegram
routing remained disabled. The complete Alembic chain through 20260911_0011
completed successfully on the empty disposable database.

Seeded one synthetic watchlist item, two explicitly constructed signal records
(paper candidate and No Trade), and one open paper trade. These are UI fixtures,
not outputs of a market-data analysis. Signed in through the normal login form
with a disposable local fixture account. No credentials are included here.

## Browser checks

| Route | Result | Observed evidence |
| --- | --- | --- |
| `/signals/[id]`, paper candidate | pass | Manual paper-review handoff, next review step and paper-logging rule visible. Link leads to the trade form; handoff states it creates no trade or order. |
| `/signals/[id]`, No Trade | pass | Explicit instruction not to log a paper trade; no paper-logging link. Review and rejection remain available outcomes. |
| `/trades` | pass | Decide/document/review guidance and documentation-only save boundary visible. Synthetic entry, stop and size entered into a draft; logging button became enabled. Draft was not submitted. |
| `/trades/[id]` | pass | Seeded open record loaded. Management and close forms require prior manual decisions; private broker/account/order data explicitly excluded. Journal is gated until close. |
| `/performance` | pass | Historical paper R-multiple interpretation, journal/process framing and sample-only export guidance visible. Zero closed trades produced the documented valid empty state. Incomplete synthetic risk metadata was visibly reported as unknown. |

- Export check: wording inspected; download not run because no export artifact was required.
- Screenshots captured: no; checks used browser accessibility observations.
- Follow-up issue: none; no blocker or boundary-copy gap found within this scope.
- Cleanup: done; all four disposable containers, their anonymous database volume,
  and the dedicated network were removed. Build images retained as local cache.
- Secrets, private records, raw logs/exports, provider payloads, cookies, local
  storage, broker/account data, profitability or strategy-validation claims included: no.

## Verification

Commands run:

```powershell
docker build -t cilly-smoke-828-api apps/api
docker build -t cilly-smoke-828-web apps/web
docker run --rm --network cilly-smoke-828 cilly-smoke-828-api alembic upgrade head
.\scripts\browser_smoke_dry_run.ps1 -TargetBaseUrl http://localhost:18280 -CommitSha 508a6884a81b4c59eb103b5c170fb7b04afe1780
git diff --check
```

Both image builds passed, including the frontend production build and type checks.
Migration passed. Browser checks above passed. Diff whitespace check passed.
Backend pytest/Ruff were not repeated: this issue changes only this evidence
document, with no application, strategy, infrastructure or script changes.

Complete sanitized output of the repository HTTP smoke command:

```text
## Browser Smoke Evidence

- Date/time: 2026-09-11T20:08:09Z
- Operator or role: not recorded
- Environment class: local-sample
- Target URL class: local
- Branch or commit SHA: 508a6884a81b4c59eb103b5c170fb7b04afe1780
- Browser and viewport class: http dry-run / viewport not applicable
- Data scope: sample / synthetic / paper only
- Pages or workflows checked: /login=pass, /=pass, /import=pass, /signals=pass
- Route-level status: pass
- Failed or blocked pages: none
- Sanitized failure category: none
- Follow-up issues or PRs: none recorded by script
- Screenshots captured: no
- Cookies, tokens, local storage, `.env` values, provider keys, database URLs, raw logs, raw API responses, private symbols, broker data, or private trading records included: no
- Production-readiness, live/realtime, broker-readiness, profitability, strategy-validation, trading-advice, or automatic-execution claim made: no
```

## Limits

This closes the specified seeded browser-guidance check only. It does not test
trade-save/close/journal mutations, CSV downloads, mobile layout, provider data,
strategy expectancy, deployment of the migration to an existing database, or
production readiness. No real orders or broker actions were performed.

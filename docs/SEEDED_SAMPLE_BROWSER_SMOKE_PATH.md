# Seeded Sample Browser Smoke Path

## Purpose

This document defines a repeatable local browser-smoke path for the polished
sample/paper workflow. It closes the v6.3 validation gap without using private
trading data, provider credentials, VPS changes, broker data, backups, raw exports,
or production-readiness evidence.

This path is sample/paper-only process validation. It is not live/realtime market
data evidence, broker readiness, profitability evidence, strategy validation,
trading advice, real-money readiness, production readiness, or approval for
automatic execution.

## Decision

Use a checklist-first browser smoke with an optional script-assisted HTTP dry run.

- Checklist-first: the operator validates authenticated route behavior and visible
  guidance in a browser using sample, fake, synthetic, or paper-only records.
- Script-assisted: `scripts/browser_smoke_dry_run.ps1` may be run against a local
  target to capture sanitized route availability evidence, but it does not replace
  the authenticated browser checks.

Do not require private staging, provider access, provider keys, VPS changes, or
private data for this smoke path.

## Preconditions

- Use a local environment unless a later issue explicitly approves another safe
  environment.
- Use only sample, fake, synthetic, or paper-only data.
- Do not load, paste, import, screenshot, export, or describe private watchlists,
  private trades, private notes, broker/account details, provider payloads, cookies,
  local storage, `.env` values, database URLs, or raw logs.
- Start from a known commit SHA and record only the SHA, environment class, route
  names, data class, pass/fail status, and sanitized failure category.

## Seed Data Requirements

The browser session should contain enough sample/paper records to exercise:

- One signal detail route representing a paper candidate or documented sample setup.
- One signal state representing observe, no-trade, or data-problem guidance if
  available.
- One paper trade draft/logging path from `/trades`.
- One trade detail route with management, close, and journal guidance visible.
- `/performance` with either zero closed paper trades or sanitized sample closed
  paper trades.

If a route cannot be reached because seed data is missing, record `blocked_seed_data`
and create a follow-up issue. Do not use private records to fill the gap.

## Route Coverage

Check these routes in the browser:

| Route | Required check |
| --- | --- |
| `/signals/[id]` | Paper handoff shows next review step and paper-logging rule; observe/no-trade/data-problem states do not invite trade logging. |
| `/trades` | Manual logging shows decide/document/review guidance and states that saving creates only a documentation record. |
| `/trades/[id]` | Management, close, and journal guidance require manual decisions before logging and forbid private broker/account/order data. |
| `/performance` | R-multiple, journal, export, and empty-state guidance is framed as historical paper/process documentation only. |

Optional HTTP dry-run coverage may include public/protected route availability only;
it must not inspect cookies, local storage, private data, or raw API responses.

## Evidence Format

Record evidence under `docs/reviews/` using this sanitized structure:

```markdown
- Date/time UTC:
- Environment class: local / approved safe environment
- Commit SHA:
- Data class: sample / fake / synthetic / paper
- Browser and viewport class:
- Optional HTTP dry run: not run / pass / fail
- `/signals/[id]` check: pass / fail / blocked with sanitized category
- `/trades` check: pass / fail / blocked with sanitized category
- `/trades/[id]` check: pass / fail / blocked with sanitized category
- `/performance` check: pass / fail / blocked with sanitized category
- Export check: not run / pass / fail / skipped with reason
- Follow-up issue:
- Screenshots captured: no / sample-only with no sensitive data
- Private records, secrets, raw logs, raw exports, provider payloads, cookies, local storage, broker/account data, profitability claims, or strategy-validation claims included: no
```

Allowed sanitized failure categories:

- `auth_setup_blocked`
- `blocked_seed_data`
- `route_unavailable`
- `guidance_missing`
- `boundary_copy_missing`
- `export_boundary_unclear`
- `target_unreachable`
- `not_run`

## Cleanup Rules

- Delete disposable sample records if the local operator created them solely for
  the smoke and cleanup is practical.
- Do not export or attach CSV output containing private or non-disposable records.
- Do not preserve screenshots unless they are sample-only and contain no private
  symbols, notes, cookies, browser storage, account data, or devtools.
- Record cleanup as `done`, `not applicable`, or `skipped with reason`.

## Stop Conditions

Stop and record a sanitized blocker if:

- Authentication requires secrets not already available to the operator.
- Seed data cannot be created without private records.
- A route exposes private symbols, notes, exports, cookies, local storage, or broker
  data.
- The smoke would require provider keys, VPS changes, backup/restore actions, or
  production-like exposure.

## Verification

- Existing `scripts/browser_smoke_dry_run.ps1` reviewed. It remains suitable only
  as optional local route-availability evidence and does not replace authenticated
  browser checks.
- Existing browser-smoke evidence boundaries reviewed conceptually; this document
  adds the seeded sample/paper route checklist needed after v6.3.

# Post-Deploy Browser Smoke Automation Evaluation

## Purpose

This document evaluates whether a lightweight automated post-deploy browser smoke script is useful for private staging. It does not implement automation, approve production-like exposure, approve private-data use, create a monitoring service, or replace the operator-run browser checklist.

Sanitized browser smoke evidence must follow
`docs/BROWSER_SMOKE_EVIDENCE_FORMAT.md`.

## Current Decision

Status: Keep post-deploy browser smoke manual for now.

Date: 2026-06-01.

Rationale:

- The existing smoke runner already automates local preflight, stack startup, migrations, and API health checks.
- The browser clickthrough currently validates safety wording, manual-action boundaries, and visual workflow context that a brittle script could miss.
- Private staging checks may require operator credentials, cookies, or environment-specific state; automating them now would increase secret-handling risk.
- No browser automation harness is currently present in the repo, and adding one would require dependency, CI, and evidence-handling decisions beyond this follow-up.

## What Automation Could Be Worth Later

A later opt-in script could be useful if it remains narrow:

- Load `/login`, `/`, `/watchlist`, `/screener`, `/import`, `/signals`, `/reviews`, `/trades`, `/performance`, `/alerts`, and `/settings` after a deployment.
- Verify that authenticated routes load, key page headings or safety text are present, and logout works.
- Use a dedicated sample/paper test account and fake symbols only.
- Record only pass/fail, route names, timestamps, commit SHA, and sanitized error categories.
- Run only when explicitly invoked by the operator, not as automatic VPS remediation.

## Not Worth Implementing Now

Do not implement automation yet if it requires any of these:

- Storing real operator credentials, cookies, session tokens, database URLs, provider keys, Telegram tokens, or private data in the repo or CI.
- Resetting private staging volumes, restoring backups, rotating secrets, restarting VPS services, changing firewall rules, or deleting data without explicit operator approval.
- Capturing screenshots that may show private watchlists, trade notes, journal text, account data, provider dashboards, cookies, or local storage.
- Treating a passing script as production readiness, live/realtime readiness, broker readiness, profitability validation, strategy validation, real-money readiness, or trading advice.
- Performing broker actions, account sync, automatic trade creation, automatic position sizing, or automatic order execution.

## Future Implementation Requirements

If this is implemented later, require a new issue and PR that documents:

- Tool choice, such as Playwright or a minimal HTTP-plus-browser harness, with dependency impact reviewed.
- Exact route coverage and assertions.
- Sample/paper account and fake-symbol setup.
- Secret handling for private staging without committing or printing credentials.
- Screenshot policy: disabled by default or sanitized sample-only screenshots.
- Operator approval boundary for any VPS service-impacting action.
- Local-only and private-staging modes kept separate.
- Evidence template aligned with `docs/PRIVATE_DATA_EVIDENCE_HANDLING.md`.
- Browser smoke evidence format aligned with `docs/BROWSER_SMOKE_EVIDENCE_FORMAT.md`.

## Safe Dry-Run Browser Smoke Contract

This contract is preparation only. It does not add Playwright, browser
automation, CI jobs, VPS actions, credential handling, or service-impacting
behavior.

Modes:

| Mode | Allowed Target | Approval Boundary |
| --- | --- | --- |
| local-sample | Local app started by the operator with sample, synthetic, or paper data. | Operator invokes manually; no private data or provider keys. |
| private-staging-dry-run | Existing private staging URL using a dedicated sample/paper account. | Explicit operator approval is required before each run. |

Allowed route checks for a future dry-run script:

| Route | Allowed Assertion |
| --- | --- |
| `/login` | Page loads and login form or expected auth boundary is visible. |
| `/` | Authenticated cockpit/dashboard loads and decision-support wording is visible. |
| `/watchlist` | Page loads without secrets; sample/fake symbols only if a create step is explicitly scoped. |
| `/screener` | Page loads and screener copy remains review-candidate oriented. |
| `/import` | Page loads; no private files are uploaded by the dry run. |
| `/signals` | Signal list loads and signal language remains review support, not advice. |
| `/reviews` | Review batch page loads and evidence-only wording remains visible. |
| `/trades` | Trade log page loads and manual-execution boundary remains visible. |
| `/performance` | Performance page loads and does not imply forecasts or profitability. |
| `/alerts` | Alerts page loads and alert wording remains a review prompt only. |
| `/settings` | Settings page loads without exposing secrets or automatic sizing claims. |

Optional detail routes such as `/signals/[id]`, `/reviews/[id]`, and
`/trades/[id]` may be checked only when the id belongs to sample/paper data
created for that run or pre-approved by the operator.

Forbidden actions:

- Capturing, printing, posting, or storing cookies, session tokens, local storage,
  passwords, `.env` values, provider keys, database URLs, raw API responses, raw
  logs, screenshots with private data, or account/broker/trade details.
- Uploading private CSVs, private watchlists, broker statements, private journal
  notes, provider exports, screenshots, or DB dumps.
- Creating broker actions, orders, automatic trades, automatic position sizing,
  provider-key syncs, Telegram sends, or external notifications.
- Restarting services, changing firewall rules, rotating secrets, restoring
  backups, purging volumes, deleting private data, or remediating VPS state.
- Treating a pass as production readiness, live/realtime readiness, broker
  readiness, profitability validation, strategy validation, real-money readiness,
  trading advice, or approval for automatic execution.

Sanitized evidence output may contain only:

- Run mode: `local-sample` or `private-staging-dry-run`.
- Date/time, operator initials or role, branch/commit SHA, browser name, viewport
  class, and target class without secrets.
- Route-level pass/fail/blocked/not-run status.
- Sanitized error category, such as `auth_failed`, `route_unavailable`,
  `safety_copy_missing`, or `unexpected_private_data_prompt`.
- Follow-up issue or PR links.
- Explicit `no` answers for cookies/tokens/private data/screenshots/raw logs and
  production/live/broker/profitability/trading-advice/automatic-execution claims.

Private-staging rules:

- Run only after explicit operator approval for that exact target and commit.
- Use a sample/paper account or operator-approved sample state only.
- Do not save credentials in the repo, CI, shell history, docs, PRs, or issues.
- Do not capture screenshots unless a later approved implementation proves the
  screenshot is sample-only and sanitized by default.
- If any page exposes private or sensitive data, stop immediately and record only
  a sanitized failure category.

## Manual Path That Remains Approved

Continue using:

- `scripts/smoke_test.ps1` for local stack startup, migrations, and API health.
- `docs/FINAL_BROWSER_CLICKTHROUGH_CHECKLIST.md` for the full 20-step browser workflow.
- `docs/DEPLOYMENT_RUNBOOK.md#post-deploy-checks` for compact private-staging post-deploy route checks.

## Final Evaluation Statement

Automated post-deploy browser smoke is useful enough to reconsider later, but not worth implementing now. The current safe path remains operator-run, sample/paper-only browser evidence with sanitized pass/fail recording and explicit approval for any VPS service-impacting action.

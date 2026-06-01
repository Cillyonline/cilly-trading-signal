# Post-Deploy Browser Smoke Automation Evaluation

## Purpose

This document evaluates whether a lightweight automated post-deploy browser smoke script is useful for private staging. It does not implement automation, approve production-like exposure, approve private-data use, create a monitoring service, or replace the operator-run browser checklist.

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

## Manual Path That Remains Approved

Continue using:

- `scripts/smoke_test.ps1` for local stack startup, migrations, and API health.
- `docs/FINAL_BROWSER_CLICKTHROUGH_CHECKLIST.md` for the full 20-step browser workflow.
- `docs/DEPLOYMENT_RUNBOOK.md#post-deploy-checks` for compact private-staging post-deploy route checks.

## Final Evaluation Statement

Automated post-deploy browser smoke is useful enough to reconsider later, but not worth implementing now. The current safe path remains operator-run, sample/paper-only browser evidence with sanitized pass/fail recording and explicit approval for any VPS service-impacting action.

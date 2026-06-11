# Browser Smoke Evidence Format

## Purpose

Browser smoke evidence records sanitized pass/fail results for manual or future
dry-run browser smoke checks. It is not production-readiness evidence, live or
realtime evidence, broker-readiness evidence, profitability evidence, strategy-
validation evidence, trading advice, or approval for automatic execution.

Use this format with `docs/FINAL_BROWSER_CLICKTHROUGH_CHECKLIST.md`,
`docs/V4_7_BROWSER_WORKFLOW_SMOKE_CHECKLIST.md`, and any future safe browser
smoke dry-run script.

## Required Fields

```markdown
## Browser Smoke Evidence

- Date/time:
- Operator or role:
- Environment class: local-sample / private-staging-dry-run / disposable-test
- Target URL class: local / private staging / other sanitized class
- Branch or commit SHA:
- Browser and viewport class: desktop / narrow mobile / both
- Data scope: sample / synthetic / paper only
- Pages or workflows checked:
- Route-level status: pass / fail / blocked / not run
- Failed or blocked pages:
- Sanitized failure category:
- Follow-up issues or PRs:
- Screenshots captured: no / sanitized sample-only
- Cookies, tokens, local storage, `.env` values, provider keys, database URLs, raw logs, raw API responses, private symbols, broker data, or private trading records included: no
- Production-readiness, live/realtime, broker-readiness, profitability, strategy-validation, trading-advice, or automatic-execution claim made: no
```

## Allowed Evidence

Allowed evidence is limited to:

- Date/time, operator role, branch or commit SHA, browser name, and viewport class.
- Environment class, such as local sample data or approved private-staging dry run.
- Page or route names checked, such as `/login`, `/watchlist`, `/signals`, or `/trades`.
- Pass, fail, blocked, or not-run status.
- Sanitized fake symbols or sample fixture names.
- Sanitized failure categories, such as `auth_failed`, `route_unavailable`,
  `safety_copy_missing`, `unexpected_private_data_prompt`, or `manual_action_boundary_missing`.
- Follow-up issue or PR links.
- Explicit `no` confirmations for sensitive data and false readiness claims.

## Forbidden Evidence

Do not record, paste, attach, commit, or upload:

- Secrets, `.env` values, provider keys, database URLs, credentials, cookies,
  session tokens, local storage, or browser profiles.
- Raw logs, raw API responses, raw provider payloads, stack traces containing
  secrets, database dumps, backup files, or private CSV files.
- Private watchlists, private symbols, personal trade notes, journal text,
  broker/account data, fills, balances, screenshots from broker/provider
  dashboards, or screenshots showing private data.
- Screenshots by default. If a later approved workflow permits screenshots, they
  must be sample-only and sanitized before being used as evidence.
- Claims that a passing smoke run proves production readiness, live/realtime data
  readiness, broker readiness, profitability, strategy validity, real-money
  readiness, trading advice, or approval for automatic execution.

## Stop Conditions

Stop the smoke run and record only a sanitized failure category if:

- A page exposes private or sensitive data.
- Any evidence would require cookies, tokens, credentials, raw logs, raw API
  responses, provider keys, private CSVs, screenshots with private data, or
  broker/account data.
- UI copy implies buy/sell instruction, trading advice, profitability,
  strategy-validation, live/realtime data, broker readiness, or automatic
  execution.
- A workflow creates analysis, signal, alert, trade, broker action, position
  sizing, or order execution automatically where explicit manual action is
  required.

## Example

```markdown
## Browser Smoke Evidence

- Date/time: 2026-06-11 21:55 UTC
- Operator or role: owner/operator
- Environment class: local-sample
- Target URL class: local
- Branch or commit SHA: abc1234
- Browser and viewport class: desktop
- Data scope: sample / synthetic / paper only
- Pages or workflows checked: `/login`, `/`, `/watchlist`, `/signals`, `/trades`
- Route-level status: pass
- Failed or blocked pages: none
- Sanitized failure category: none
- Follow-up issues or PRs: none
- Screenshots captured: no
- Cookies, tokens, local storage, `.env` values, provider keys, database URLs, raw logs, raw API responses, private symbols, broker data, or private trading records included: no
- Production-readiness, live/realtime, broker-readiness, profitability, strategy-validation, trading-advice, or automatic-execution claim made: no
```

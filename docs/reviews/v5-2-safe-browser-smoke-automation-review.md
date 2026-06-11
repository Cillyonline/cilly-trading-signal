# v5.2 Safe Browser Smoke Automation Review

## Scope

Milestone: `v5.2 - Safe Browser Smoke Automation`

Review issue: #706

Reviewed issues:

- #685 `docs: record browser smoke evidence format`
- #683 `ci: evaluate browser smoke CI versus manual runner`
- #682 `test: add safe browser smoke dry-run implementation`

## Outcome

v5.2 is complete.

The milestone added a safe, opt-in, local/manual browser-smoke dry-run path and
the evidence policy around it. It did not add required CI browser automation,
private-staging automation, provider-key handling, screenshots, browser storage
access, broker integration, automatic execution, live/realtime claims,
profitability claims, strategy-validation claims, or production-readiness claims.

## Completed Work

#685 added `docs/BROWSER_SMOKE_EVIDENCE_FORMAT.md` as the canonical sanitized
browser-smoke evidence format. Existing browser smoke docs now reference it.

#683 recorded the execution-model decision in
`docs/POST_DEPLOY_BROWSER_SMOKE_AUTOMATION_EVALUATION.md`: use an explicit
local/manual dry-run first; do not make browser smoke a required CI gate in v5.2.
Private-staging dry runs remain approval-gated for the exact target and commit.

#682 added `scripts/browser_smoke_dry_run.ps1`, an explicit PowerShell HTTP
dry-run helper. It checks `/login`, `/`, `/import`, and `/signals`, prints only
sanitized Markdown pass/fail evidence, blocks non-local targets in `local-sample`
mode, and requires `-ApprovedPrivateStaging` for `private-staging-dry-run` mode.
Docs were updated in `docs/MVP_SMOKE_TEST.md`,
`docs/FINAL_BROWSER_CLICKTHROUGH_CHECKLIST.md`, and
`docs/POST_DEPLOY_BROWSER_SMOKE_AUTOMATION_EVALUATION.md`.

## Verification Evidence

PR checks passed before merge:

- #703: `API lint and tests`, `Web build`, `Dependency visibility`, and
  `Container visibility` passed.
- #704: `API lint and tests`, `Web build`, `Dependency visibility`, and
  `Container visibility` passed.
- #705: `API lint and tests`, `Web build`, `Dependency visibility`, and
  `Container visibility` passed.

Local dry-run verification performed for #682:

```powershell
.\scripts\browser_smoke_dry_run.ps1 -TargetBaseUrl http://localhost:1 -CommitSha dry-run-test
```

Result: expected sanitized failure output and exit code `1` for an unavailable
local target. The output included only route status categories and explicit `no`
statements for cookies, tokens, browser storage, `.env` values, provider keys,
database URLs, raw logs, raw API responses, private symbols, broker data,
private trading records, screenshots, and readiness claims.

The dry-run was not executed against a live local app in this review. That leaves
route-pass behavior dependent on the normal local stack being started by the
operator before use.

## Security And Privacy

No secrets, `.env` files, provider keys, private data, cookies, browser storage,
raw logs, raw API responses, screenshots, broker/account data, or private market
data were added.

The script does not print the full target URL in evidence; it prints only the
target class. Route paths are limited to the documented dry-run route set.

## Trading Logic Review

No trading logic changed. The dry-run checks page availability only and does not
create analysis, signals, alerts, trades, broker actions, position sizing, or
orders. It does not validate profitability, strategy quality, live/realtime data,
or production readiness.

## Remaining Gaps

No follow-up issue is required for the v5.2 scope.

Known limitations remain intentional:

- The dry-run is an HTTP route smoke, not a full browser rendering or clickthrough
  replacement.
- The dry-run is not a required CI gate.
- Private-staging dry runs still require explicit operator approval for the exact
  target and commit.
- The full 20-step visual workflow remains manual through
  `docs/FINAL_BROWSER_CLICKTHROUGH_CHECKLIST.md`.

## Decision

Close `v5.2 - Safe Browser Smoke Automation` after this review PR merges.

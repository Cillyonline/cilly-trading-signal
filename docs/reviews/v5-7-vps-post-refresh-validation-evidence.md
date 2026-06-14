# v5.7 VPS Post-Refresh Validation Evidence

Date: 2026-06-14

## Scope

This file records the approved private VPS post-refresh validation evidence after
the v5.7 checklist and evidence format were completed.

This is controlled private-staging, sample/paper-only process evidence. It is not
production-readiness evidence, live or realtime data evidence, broker-readiness
evidence, profitability evidence, strategy-validation evidence, trading advice,
real-money readiness, or approval for automatic execution.

## Evidence

- Date/time UTC: 2026-06-14
- Operator or role: owner/operator
- Environment class: private staging
- Approval gate: approved by owner-operator in-session
- Target domain: `trading.cillyonline.de`
- Branch or commit SHA: `924f0a842027de1df5036b9b91665442e0c7aba3`
- Browser and viewport class: desktop browser plus HTTP dry-run / viewport not applicable for dry-run
- Data scope: sample / synthetic / paper only
- Sample symbol scope: aggregate only / redacted
- Checklist used: `docs/POST_REFRESH_OPERATOR_VALIDATION_CHECKLIST.md`
- Evidence format used: `docs/POST_REFRESH_VALIDATION_EVIDENCE_FORMAT.md`
- Routes or workflows checked: `/login`, `/`, `/watchlist`, `/import`, `/signals`, `/signals/[id]`, `/trades`, `/performance`, `/alerts`, logout
- Refresh path checked: manual post-refresh workflow; no provider smoke recorded in this evidence
- Compose project status: pass
- Existing unrelated `staging` project unaffected: pass
- Internal API health: pass
- HTTPS API health: pass
- HTTPS web health: pass
- Browser dry-run: pass
- Manual login: pass
- Dashboard: pass
- Watchlist: pass
- Import Readiness status: pass
- CSV fallback guidance visible: pass
- Provider fallback guidance visible: pass
- Manual analysis boundary visible: pass
- Signals: pass
- Signal detail: pass
- Signal review boundary visible: pass
- Trades: pass
- Manual trade logging boundary visible: pass
- Performance: pass
- Alerts: pass
- Logout/protected-route behavior: pass
- No automatic analysis, signal, trade, order, broker action, position sizing, or alert created: pass
- Failed or blocked steps: none
- Sanitized failure category: none
- Follow-up issues or PRs: none required from this validation
- Screenshots captured: no
- Secrets, `.env` values, provider keys, request URLs, raw payloads, raw CSV rows, cookies, local storage, screenshots with sensitive data, private symbols, broker data, provider account details, or private trading records included: no
- Production-readiness, live/realtime, broker-readiness, profitability, strategy-validation, trading-advice, real-money-readiness, or automatic-execution claim made: no

## Server Checks

Sanitized server outcomes recorded by the operator:

- VPS checkout fast-forwarded from `0c5cd36b09d55b68761dc1fb2fb53629c419f9f9` to `924f0a842027de1df5036b9b91665442e0c7aba3`.
- `.env` existence check returned present; `.env` contents were not printed or recorded.
- Compose listed `cilly-trading-signal` as `running(4)`.
- Compose listed the unrelated `staging` project separately as `running(1)`.
- `postgres`, `api`, `web`, and `caddy` were running for the `cilly-trading-signal` project after rebuild/restart.
- Internal API health returned `status=ok` and `environment=staging`.
- HTTPS API health returned `status=ok` and `environment=staging`.
- HTTPS web returned HTTP 200.

The first post-restart internal API health request returned a transient connection
reset while the API container had just restarted. A later internal API health check
passed, and external HTTPS API health passed.

## Browser Dry-Run

The safe browser dry-run was executed against the private-staging target with
`scripts/browser_smoke_dry_run.ps1` and explicit private-staging approval.

Sanitized result:

- `/login`: pass
- `/`: pass
- `/import`: pass
- `/signals`: pass
- Route-level status: pass
- Failed or blocked pages: none
- Sanitized failure category: none

The dry-run did not read credentials, cookies, local storage, `.env`, provider
keys, raw logs, raw API responses, private symbols, broker data, private trading
records, or screenshots.

## Decision

The private VPS post-refresh validation passed for controlled owner/operator
sample/paper-only use.

No follow-up issue is required from this validation. `v5.8 - Review Calibration
Follow-up` remains deferred because this validation did not identify concrete
signal-quality or review-calibration gaps.

## Boundary

This evidence does not approve:

- Public SaaS or multi-user operation.
- Private trading data handling.
- Real-money workflows.
- Broker integration.
- Automatic order execution.
- Automatic trade creation.
- Scheduler-driven provider reliance.
- Live or realtime market-data claims.
- Profitability, strategy-validation, trading-advice, production-readiness, or
  real-money-readiness claims.

# v1.2 Release Candidate Decision Gate

## Purpose

This document records the final v1.2 release-candidate decision gate for controlled internal handoff. It is based on the current release checklist, smoke-test evidence, deployment and backup/restore documentation, light MVP security review, demo-reset documentation, and handoff summary.

This decision is not a production-readiness statement, profitability claim, strategy validation, trading advice, broker-readiness claim, or public SaaS readiness claim.

## Decision

Accept RC for internal handoff.

## Rationale

- The latest smoke-test evidence documents a passing Docker Compose proxy stack rebuild, direct API health check, Caddy-routed API health check, Caddy web load, authenticated browser workflow, logout, and protected API data denial after logout. See [MVP Smoke Test](MVP_SMOKE_TEST.md#latest-run).
- The Caddy deployment path, health checks, secret-handling boundaries, deployment smoke-test checklist, PostgreSQL backup guidance, PostgreSQL restore guidance, and disposable demo data reset procedure are documented in [Deployment Runbook](DEPLOYMENT_RUNBOOK.md).
- PostgreSQL backup/restore mechanics passed on a disposable Compose project with sample-only marker data. See [PostgreSQL Backup/Restore Evidence](MVP_RELEASE_CHECKLIST.md#postgresql-backuprestore-evidence).
- [#143](https://github.com/Cillyonline/cilly-trading-signal/issues/143) fixed the protected-route UX after logout.
- [#144](https://github.com/Cillyonline/cilly-trading-signal/issues/144) completed the light MVP security review and concluded that the reviewed posture is acceptable for internal RC handoff only.
- [#145](https://github.com/Cillyonline/cilly-trading-signal/issues/145) documented the disposable demo data reset procedure.
- [#146](https://github.com/Cillyonline/cilly-trading-signal/issues/146) created the v1.2 release-candidate handoff summary and identified this decision gate as the remaining step before broader release decisions.
- The direct API/web host port exposure follow-up ([#150](https://github.com/Cillyonline/cilly-trading-signal/issues/150)) has been addressed by binding direct API and web ports to localhost in the provided Compose file; [#151](https://github.com/Cillyonline/cilly-trading-signal/issues/151) remains open.

## Blocker Classification

### Blockers for internal RC handoff

- None identified in the reviewed evidence.

### Non-blockers for internal RC handoff

- [#150](https://github.com/Cillyonline/cilly-trading-signal/issues/150) Restrict direct API/web host port exposure in Caddy deployments has been addressed by binding direct API and web ports to localhost in the provided Compose file.
- [#151](https://github.com/Cillyonline/cilly-trading-signal/issues/151) Make backup script default output path safer for sensitive dumps, while the RC remains controlled/internal, backups are treated as sensitive, and the risk is tracked.
- Dashboard, Journal, Performance, Alerts, and Settings remain MVP-level views, not full analytics or operations consoles.
- Risk enforcement covers core manual trade logging rules, not full portfolio exposure, correlation, or account-level risk management.
- Stale signal handling flags old saved signals, but does not refresh market data or re-run strategy automatically.
- Telegram support currently covers explicit operator test messages; production alert routing is not complete.
- TradingView webhook support persists review events, but does not trigger broker execution, auto-trade creation, or automatic Telegram delivery.
- Production monitoring and operational alerting are not documented as passed.
- Full mobile app/PWA hardening beyond responsive MVP layouts is not documented as passed.

### Blockers for broader/public/prod-like exposure

- [#151](https://github.com/Cillyonline/cilly-trading-signal/issues/151) unless it is addressed or explicitly accepted in a separate broader-release decision.
- No production-readiness evidence is documented as passed.
- No full penetration test is documented as completed.
- No dependency or container vulnerability scan is documented as completed.
- No production monitoring or operational alerting is documented as passed.
- Production alert routing is not complete.

## Not Included / Safety Boundary

- No broker integration.
- No automatic order execution.
- No automatic trading.
- No real-money trading.
- No production-readiness claim.
- No profitability claim.
- No trading advice.
- No broker readiness.
- No public SaaS readiness.
- No live market data or live account sync.
- No production alert-routing readiness claim.

## Follow-Up Requirements

- The direct API/web host port exposure follow-up ([#150](https://github.com/Cillyonline/cilly-trading-signal/issues/150)) has been addressed by binding direct API and web ports to localhost in the provided Compose file.
- [#151](https://github.com/Cillyonline/cilly-trading-signal/issues/151) Make backup script default output path safer for sensitive dumps remains relevant before broader or production-like exposure.
- Production monitoring and operational alerting must be handled separately before any production-like readiness claim.
- Any broader release, production-like public exposure, broker-readiness claim, real-money use, profitability claim, or public SaaS readiness claim requires an explicit follow-up decision after the relevant security and operational gaps are addressed or explicitly accepted.

## Final Assessment

- v1.2 RC is accepted for controlled internal handoff/review.
- v1.2 RC is not accepted for production-like public exposure.
- v1.2 RC is not accepted for broker readiness, automatic execution, real-money trading, profitability claims, trading advice, or public SaaS readiness.
- Any broader release requires an explicit follow-up decision after security and operational gaps are addressed or accepted.

# Production-Like Requirements Review

## Purpose

This review documents requirements and blockers for any future production-like exposure while preserving the current No Go state. It does not approve production use, public launch, broker integration, live/realtime trading, real-money reliance, profitability validation, strategy validation, trading advice, or automatic execution.

## Current Decision

Status: No Go for production-like exposure.

Date: 2026-06-01.

v2.9 rebaseline snapshot, 2026-06-02: current-main local validation passed for
sample-only local stack build/startup, migrations, API health, web HTTP load,
sanitized evidence formatting, and cleanup. This is local/internal review evidence
only and does not satisfy production-like requirements.

Production-like means any environment or workflow that has one or more of these properties:

- Public internet exposure beyond controlled owner/operator staging.
- Real private trading data as routine operational data.
- Multi-user, customer, public SaaS, billing, onboarding, or support operation.
- Real-money reliance, broker/account connectivity, exchange account sync, order routing, automatic trade creation, automatic position sizing, or automatic execution.
- Operational claims that users or third parties could reasonably interpret as production-ready, live/realtime, secure, profitable, validated, or broker-ready.

## Out Of Scope Unless Separately Approved

- Broker integration, exchange account sync, order routing, automatic position sizing, automatic trade creation, automatic order execution, or automatic trading.
- Public launch, customer onboarding, billing, support operation, multi-tenant use, or public SaaS operation.
- Live/realtime market-data claims, trading advice, buy/sell instructions, profitability claims, win-rate claims, backtest-validation claims, benchmark-outperformance claims, strategy-validation claims, or real-money-readiness claims.

## Required Evidence Before Reconsideration

Production-like exposure may be reconsidered only after a new explicit gate records current sanitized evidence for all of these areas:

| Area | Required evidence |
| --- | --- |
| Scope and owner acceptance | Exact intended exposure, data class, users, domain, operator responsibilities, and explicit residual-risk acceptance. |
| Deployment smoke | Current target-environment deployment smoke, health checks, migration status, HTTPS/Caddy routing, and rollback readiness. |
| API/Web verification | Current CI on `main` or the intended release commit, plus any target-specific smoke checks. |
| Dependency/container security | Reviewed scan output under `docs/SECURITY_SCAN_REVIEW_POLICY.md`, including treatment of critical/high findings. |
| Monitoring and alerting | Health, service availability, disk, memory/load, database, certificate, backup freshness, failed jobs, and escalation coverage. |
| Backups and restore | Offsite/geographic encrypted backup target, current backup evidence, restore drill from that target into a disposable environment, and retention expectations. |
| Incident response | Rehearsed incident response for database restore, secret rotation, private-data exposure, deployment rollback, and communication. |
| Secret handling | Documented storage, rotation, access boundaries, server environment handling, provider credentials, app secrets, database credentials, and backup credentials. |
| Privacy handling | Private-data evidence rules, trade/journal privacy review, screenshot/log handling, and backup/restore evidence boundaries. |
| Rollback and data compatibility | App rollback plan, database migration compatibility decision, and restore decision point for schema-changing releases. |
| Product safety | No-broker/no-execution boundary, No Trade as first-class outcome, stale/failed/partial data stop points, and no trading-advice/profitability wording. |

## Current Blockers

Production-like exposure remains blocked because these are not complete as production-like evidence:

- No explicit production-like target, exposure model, user model, domain, operator responsibility model, or owner acceptance is recorded.
- No current production-like deployment smoke exists for an intended target.
- Dependency/container scans are visible and thresholds are documented, but current findings still need production-like review and acceptance for the intended release.
- Monitoring escalation expectations are documented, but production-like alert destinations, thresholds, operator response evidence, and owner acceptance are not complete.
- Offsite/geographic backup target evaluation is documented, but target selection, configuration, and restore evidence are not complete.
- Private-data readiness remains No Go for routine private trading records.
- Incident rehearsal exists for private-data database restore/secret rotation, but production-like incident ownership and communication acceptance are not complete.
- Rollback and database-restore decision evidence exists as runbook guidance, not target-specific production-like proof.
- Public SaaS, broker/account connectivity, live/realtime claims, and automatic execution remain outside the approved scope.

The consolidated production-like evidence map is tracked in
`docs/PRODUCTION_LIKE_READINESS_GAP_REGISTER.md`. That register is planning
evidence only and does not change this No Go decision.

Current evidence still missing before any reconsideration:

- Exact production-like target, exposure model, user model, and owner/operator
  residual-risk acceptance.
- Target-environment deployment smoke, browser evidence, monitoring operation,
  rollback evidence, and incident ownership.
- Reviewed dependency/container scan output for the intended release and target.
- Offsite/geographic encrypted backup configuration and restore evidence from that
  storage path into a disposable target.
- Privacy handling package for screenshots, logs, backups, restores, private
  records, and evidence sharing.
- Secret rotation and environment handling evidence for app, database, provider,
  backup, and deployment credentials.

## Evidence Handling

Use `docs/PRIVATE_DATA_EVIDENCE_HANDLING.md` for all production-like review evidence. Do not include secrets, `.env` values, database URLs, cookies, tokens, provider keys, backup repository credentials, raw logs, screenshots with private data, dump contents, restored rows, private watchlists, trade notes, journal notes, broker/account data, or provider dashboards.

Allowed review evidence is limited to sanitized status, pass/fail, workflow links, commit SHA, check names, issue/PR references, target class, snapshot ID prefix, and explicit follow-up links.

## Required New Gate

Any future reconsideration must create a new production-like decision gate with:

- Current date and intended release/commit.
- Exact approved and disallowed use.
- Evidence table for every required area above.
- Residual risks and owner/operator acceptance.
- Explicit No-Go conditions and reopen triggers.
- Statement that broker execution, public launch, live trading, and private-data reliance remain disallowed unless that gate explicitly and narrowly approves them.

## Final Review Statement

The current product remains acceptable only for local review and controlled private owner/operator staging with sample, synthetic, paper, or separately sanitized workflows under existing gates. Production-like exposure remains No Go until a separate current gate records complete sanitized evidence and explicit owner/operator residual-risk acceptance.

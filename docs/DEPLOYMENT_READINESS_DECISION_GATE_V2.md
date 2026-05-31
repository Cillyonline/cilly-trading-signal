# Deployment Readiness Decision Gate v2

## Purpose

This document records the current deployment-readiness gate for controlled owner/operator use after the v2.1-v2.6 operational-readiness work. It separates local review, private staging, and production-like exposure so evidence cannot be over-interpreted.

This is not a production-readiness statement, security certification, broker-readiness claim, profitability claim, strategy-validation claim, trading advice, or approval for automatic execution.

## Current Decision

Status: Conditional Go for local review and private owner/operator staging only.

Date: 2026-05-31.

Production-like exposure: No Go.

Rationale:

- The app has documented local setup, deployment runbooks, health checks, monitoring checklists, backup guidance, restore guidance, and a repeatable backup restore drill.
- Private VPS staging previously passed documented smoke and hardening checks for controlled owner/operator use.
- Structured API health details are available for operator diagnostics without exposing secrets.
- Current broader monitoring, incident response, dependency/container scanning, offsite encrypted backup storage, and production-like evidence are not yet complete.
- The product remains decision-support only with manual execution only.

## Safety Boundaries

- No broker integration.
- No automatic order execution.
- No automatic trading.
- No buy/sell instructions or trading advice.
- No profitability, win-rate, backtest-validation, benchmark-outperformance, or real-money-readiness claim.
- No live/realtime market-data claim.
- No public SaaS, multi-user, billing, onboarding, or customer-support claim.
- No handling of private trading data beyond a separately approved controlled owner/operator process.

## Gate Matrix

| Environment | Current status | Approved use | Required evidence before use | Non-go conditions |
| --- | --- | --- | --- | --- |
| Local review | Go | Development, docs review, automated checks, disposable smoke tests, sample/paper data review | Local setup docs followed; relevant API/Web checks pass or skipped with reason; secrets stay local/untracked; no dump files in repo | Missing required config, failed auth or safety checks, committed secrets, backup dumps in repo, broker/auto-execution scope introduced |
| Private owner/operator staging | Conditional Go | Controlled single-owner review, sample/paper workflows, sanitized operational checks | Private VPS staging gate remains valid; health checks pass; backups are external to repo; backup restore drill is documented or recently run when needed; staging secrets are server-local; monitoring checklist reviewed | Public launch, real-money claim, real private-data reliance without separate approval, failed health/smoke/backup checks, unclear restore target, unrelated VPS projects affected |
| Production-like exposure | No Go | None under this gate | Separate production-like gate with completed evidence for security review, dependency/container scans, incident runbook, operational monitoring, backup restore drill, rollback, privacy handling, and explicit owner acceptance | Any missing required evidence, unresolved critical/high security issue, no current smoke evidence, no tested restore path, no incident process, public SaaS or broker/execution scope requested |

## Current Pass/Fail Evidence

| Evidence item | Current result | Reference |
| --- | --- | --- |
| Manual execution and no-broker safety boundary | Pass | `docs/MVP_RELEASE_CHECKLIST.md`, `docs/STRATEGY_AND_ALERTS.md` |
| Local/API/Web CI on recent PRs | Pass | Latest merged PR checks on `main` |
| Private VPS staging decision | Pass for private owner/operator staging only | `docs/VPS_STAGING_DECISION_GATE.md` |
| Deployment and rollback guidance | Pass as documented operator guidance | `docs/DEPLOYMENT_RUNBOOK.md` |
| Structured health diagnostics | Pass for sanitized operator diagnostics | `/api/health`, `/api/health/details` |
| Backup creation guidance | Pass as documented operator guidance | `docs/DEPLOYMENT_RUNBOOK.md#postgresql-backups` |
| Backup restore drill procedure | Pass as documented procedure; run evidence required before operational reliance | `docs/DEPLOYMENT_RUNBOOK.md#backup-restore-drill` |
| Monitoring expectations | Partial; checklist exists, production monitoring evidence not complete | `docs/APPLICATION_MONITORING_CHECKLIST.md` |
| Dependency/container scan evidence | Fail for production-like exposure; not yet completed under this gate | Follow-up issue `#333` |
| Incident response runbook | Fail for production-like exposure; not yet completed under this gate | Follow-up issue `#334` |
| Offsite encrypted backups | Fail for production-like exposure; not documented as implemented | This gate |
| Production-like/public exposure decision | Fail; explicitly No Go | This gate |

## Required Evidence

### Local Review Gate

- `README.md` setup path remains current for the touched area.
- Relevant checks pass for the change type, such as API lint/tests for backend changes, web build for frontend changes, or docs review for docs-only changes.
- Docker Compose smoke is run when feasible for deployment-affecting changes, or the blocker is documented.
- `.env`, credentials, cookies, database URLs, dumps, screenshots with sensitive data, and private trading data are not committed or pasted.
- Safety wording remains decision-support only and manual-execution only.

### Private Staging Gate

- `docs/VPS_STAGING_DECISION_GATE.md` remains valid or is explicitly reopened.
- `docs/DEPLOYMENT_RUNBOOK.md` is followed for deployment, health checks, backups, restore, rollback, and sanitized evidence.
- `docs/APPLICATION_MONITORING_CHECKLIST.md` is reviewed before relying on the staging instance operationally.
- `/api/health` and, when appropriate, `/api/health/details` return expected sanitized status.
- PostgreSQL backups are stored outside the repository checkout and have non-zero recent artifacts.
- Restore readiness is covered by the repeatable `docs/DEPLOYMENT_RUNBOOK.md#backup-restore-drill` procedure on a disposable target.
- Any evidence recorded in issues, PRs, or docs is sanitized.

### Production-Like Gate

Production-like exposure requires a new explicit decision. Minimum evidence must include:

- Current Docker Compose or equivalent deployment smoke evidence on the intended target.
- Current API/Web CI results from `main`.
- Dependency and container scan results reviewed and accepted.
- Incident runbook with severity, triage, rollback, communication, and evidence-handling steps.
- Monitoring and alerting evidence for health, logs, disk, memory, database, backup freshness, and certificate expiry.
- Backup restore drill evidence on a disposable target using sanitized proof only.
- Rollback evidence for app deployment and database compatibility assumptions.
- Secret rotation and environment handling procedure.
- Explicit acceptance of residual risks by the owner/operator.

## Explicit Non-Go Conditions

The gate is No Go if any of these are true:

- Broker integration, automatic order execution, automatic trading, or account sync is introduced.
- Marketing, UI, docs, alerts, or issue evidence imply buy/sell instructions, trading advice, profitability, or real-money readiness.
- Required checks are failing without an accepted reason.
- The app is exposed publicly without a current production-like decision gate.
- Secrets, `.env` files, database URLs, cookies, backup dumps, raw private logs, screenshots with sensitive data, trade journal content, or private trading data are committed or attached.
- A restore target is not clearly disposable or explicitly approved.
- Health checks, smoke checks, backup creation, or restore drills fail.
- Critical/high security findings are open without documented owner acceptance.
- The unrelated VPS `staging` project, ports, volumes, or routing are affected.

## Reopen This Gate If

- Production-like exposure, public SaaS use, multi-user behavior, billing, onboarding, broker integration, account sync, or automatic execution is proposed.
- Real private trading data or real-money workflows become part of routine use.
- Authentication, session handling, CORS, cookies, secret management, Caddy, Docker networking, firewall, backup, restore, or monitoring changes materially.
- Dependency/container scanning or incident-runbook work identifies a blocker.
- A smoke test, health check, backup, restore drill, or deployment rollback fails.

## Final Gate Statement

The current product is acceptable only for local review and controlled private owner/operator staging with sample or paper workflows. Production-like exposure remains blocked until a separate gate records current evidence for security, monitoring, incident response, backup restore, rollback, and privacy handling. The trading workflow remains decision-support only, manual-execution only, with no broker integration and no automatic order execution.

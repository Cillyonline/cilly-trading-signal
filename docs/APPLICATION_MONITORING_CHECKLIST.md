# Application Monitoring Checklist

## Purpose

This checklist defines the minimum monitoring review expected before relying more heavily on the app in owner/operator environments.

It is not a monitoring service integration, production-readiness claim, SLA, trading alerting system, broker readiness statement, or profitability evidence.

For the production-like monitoring escalation plan and evidence template, see
`docs/PRODUCTION_LIKE_MONITORING_ESCALATION_PLAN.md`. That plan is required
planning evidence only and does not approve production-like exposure.

## Safety And Privacy Rules

- Do not commit or paste `.env` files, database URLs, credentials, cookies, API keys, backup dumps, raw logs, screenshots with private data, or trading journal contents.
- Review and redact logs before using them in issues, PRs, screenshots, or chat.
- Monitoring evidence must use status summaries such as pass/fail, timestamps, sanitized service names, and follow-up issue links.
- Signals, alerts, risk warnings, and monitoring checks are decision-support and operations prompts only, not trade instructions.
- Do not expose direct API or web service ports publicly when using the Caddy route.

## Environment Levels

### Local

Use local monitoring for development and disposable smoke checks only.

Cadence:

- Before and after local smoke tests.
- After dependency, Docker, config, migration, import, or auth changes.
- Before sharing any local failure evidence.

Checklist:

- API health: `http://localhost:8000/api/health` returns a healthy response when the API is running.
- Web load: `http://localhost:3000` loads when the frontend is running.
- Containers: expected Docker Compose services are running for the selected profile.
- Logs: API, web, PostgreSQL, and Caddy logs have no repeated startup failures or stack traces relevant to the change.
- Disk: local Docker disk usage is not blocking builds, database writes, or imports.
- Database: local PostgreSQL accepts connections and migrations/tests are not failing due to DB availability.
- Backups: only disposable backup/restore checks are performed locally unless explicitly approved.
- Failed jobs: failed test, build, import, provider-sync, or backup/restore commands are captured as sanitized summaries.

### Private Staging

Use private staging monitoring for owner/operator validation on the VPS. This is still not production readiness.

Cadence:

- Run the automated VPS health check every 15 minutes when enabled through systemd.
- Review health, containers, disk, and backup freshness daily during active staging use.
- Run the full checklist after every deployment, restart, restore drill, DNS change, firewall change, Caddy change, or secret rotation.
- Review failed job status the same day it is detected.

Checklist:

- Health: `https://<app-domain>/api/health` returns a healthy response through Caddy.
- Web route: `https://<app-domain>/` loads through Caddy over HTTPS.
- Containers: `postgres`, `api`, `web`, and `caddy` are running and not repeatedly restarting.
- Logs: short tails for API, web, PostgreSQL, and Caddy show no repeated config guard failures, DB errors, auth errors, certificate errors, or stack traces requiring action.
- Disk: root filesystem and Docker usage leave room for images, PostgreSQL data, logs, and backups.
- Database: PostgreSQL is healthy and database-dependent pages work after login.
- Backups: the backup timer exists if enabled, the last run status is understood, and recent non-empty dumps are outside the repository checkout.
- Failed jobs: failed health-check timer runs, backup timer runs, restore drills, imports, provider-sync attempts, deployments, and smoke tests have a sanitized follow-up note or issue.

### Production-Like

Use production-like monitoring only after a separate decision gate explicitly approves the environment. Passing this checklist still does not create a production-readiness, real-money, broker, or profitability claim.

Cadence:

- Health and web route: continuous external monitoring or a documented operator equivalent.
- Containers and failed jobs: at least daily during active use, and immediately after deploys or restarts.
- Disk and backup freshness: daily.
- Restore evidence: on a scheduled drill cadence before broader reliance.
- Security/privacy review: before sharing any operational evidence outside the private operator context.

Checklist:

- Health: public Caddy-routed API health is monitored without exposing direct service ports.
- Logs: operational log review has a redaction rule and a private storage location outside git.
- Disk: alert threshold is defined before disk pressure threatens database writes or backups.
- Database: DB health and app DB-dependent paths are checked after deploys, restores, and migrations.
- Backups: backup freshness, non-zero dump size, external storage location, and restore-drill evidence are tracked.
- Failed jobs: deployment, backup, restore, import, provider sync, and health-check failures produce operator-visible follow-up records.
- Incident handling: failures that affect login, data integrity, backups, restores, or public routing are handled through the [Operational Incident Runbook](OPERATIONAL_INCIDENT_RUNBOOK.md).

Required before production-like exposure is reconsidered:

- External health monitoring or a documented operator-equivalent check must cover
  API health and web route availability without exposing direct service ports.
- Operator-visible escalation must exist for API health failure, web route
  failure, PostgreSQL unhealthy state, repeated container restarts, failed backup
  jobs, stale backup evidence, disk pressure, certificate expiry risk, and failed
  restore drills.
- Alert destinations, quiet-hours behavior, and owner/operator response windows
  must be documented without posting tokens, chat IDs, phone numbers, private
  email addresses, or provider account details.
- Backup freshness and disk usage must have explicit thresholds and follow-up
  actions before data loss or write failures are likely.
- A failed alert, failed health check, or unavailable operator response path must
  be treated as a No-Go condition for production-like reliance until resolved or
  explicitly accepted.

Production-like escalation expectations:

| Area | Trigger | Expected operator response | Evidence boundary |
| --- | --- | --- | --- |
| API health | `/api/health` fails or returns unexpected status repeatedly. | Stop relying on app output, check `/api/health/details` if safe, inspect sanitized logs, open incident/follow-up. | Pass/fail, timestamp, route, commit; no raw logs with secrets/private data. |
| Web route | HTTPS web route fails, certificate is invalid/near expiry, or Caddy routing breaks. | Stop public reliance, check Caddy/container status, verify direct ports remain private, follow deployment runbook. | HTTP status category and sanitized service status only. |
| Service availability | Expected containers are exited, unhealthy, or repeatedly restarting. | Freeze data-changing workflows, check disk/memory/logs, escalate through incident runbook. | Service names and pass/fail only. |
| Database | PostgreSQL unhealthy, DB-backed pages fail, migrations mismatch, or restore uncertainty exists. | Stop data-changing workflows, confirm backup state, avoid destructive repair without approval. | Health status and migration version only. |
| Backups | Latest backup missing, zero size, stale, failed timer, failed Restic check, or stale restore drill. | Treat private-data/production-like reliance as blocked, run documented backup/restore triage, create follow-up. | Target category, snapshot ID prefix, pass/fail; no dump contents or credentials. |
| Disk and storage | Root/Docker/PostgreSQL/backup storage approaches documented threshold. | Reduce nonessential growth, preserve DB/backups, avoid deploys/imports until safe. | Usage percentage/range only; no sensitive paths if private. |
| Failed jobs | Deploy, backup, restore, provider sync, health check, or smoke job fails repeatedly. | Record sanitized failure category, stop affected workflow reliance, open issue. | Job name, status, follow-up link. |

Private staging versus production-like monitoring:

| Requirement | Private staging | Production-like reconsideration |
| --- | --- | --- |
| Health checks | Timer/manual checks are acceptable for controlled owner/operator staging. | External or operator-equivalent monitoring with documented escalation is required. |
| Backups | Local/VPS backup evidence can support staging validation. | Offsite/geographic encrypted backup evidence and restore drill are required. |
| Disk review | Daily during active staging use. | Thresholds, escalation path, and response expectation must be documented. |
| Failed alerts/checks | Same-day review during active staging use. | Operator-visible alerting and blocked-reliance behavior must be documented. |
| Evidence | Sanitized issue/checklist notes. | Sanitized evidence plus explicit owner/operator acceptance in a production-like gate. |

## Minimum Evidence Record

For each monitoring review, record only sanitized evidence:

- Date/time and environment level.
- Checks run and pass/fail status.
- Failed boundary, if any: health, logs, disk, DB, backups, failed jobs, or routing.
- Follow-up issue or incident record, if needed.
- Confirmation that no secrets, private data, raw logs, backup contents, or credentials were included.

## v3.5 Existing VPS Partial Monitoring Evidence

Date: 2026-06-03

Scope:

- Target: existing VPS at `trading.cillyonline.de`.
- Exposure: controlled private owner/operator staging only.
- Data class: sample, synthetic, and paper data only.
- Action class: non-destructive public route check only.

Evidence:

- API health route: PASS via local `Invoke-RestMethod` against
  `https://trading.cillyonline.de/api/health`, returning healthy staging status.
- API health route: PASS via local `curl.exe --ssl-no-revoke` against
  `https://trading.cillyonline.de/api/health`.
- Web route: PASS via local `curl.exe --ssl-no-revoke -fsSI` against
  `https://trading.cillyonline.de/`, returning `HTTP/1.1 200 OK` through Caddy.
- Web/API route checks without the Windows Schannel revocation workaround remain
  not conclusive from this local environment. See
  `docs/MVP_SMOKE_TEST.md#v35-existing-vps-public-route-partial-evidence`.
- Containers: not checked; requires operator-guided VPS status evidence.
- PostgreSQL: not checked; requires operator-guided VPS or authenticated smoke
  evidence.
- Disk/storage: not checked; requires operator-guided VPS evidence.
- Backup freshness: not checked; remains blocked pending operator approval.
- Certificate status: not accepted as monitored; local Schannel revocation check
  was inconclusive from this environment.
- Failed jobs: not checked; requires operator-visible monitoring/timer/job review.
- Alert destination class: not reviewed; requires owner/operator decision.
- Fallback path: not reviewed; requires owner/operator decision.
- Operator response window: not accepted; requires owner/operator decision.
- Secrets/private data/raw logs included: no.
- Production-like exposure approved by this evidence: no.

Conclusion:

- This partial evidence confirms that the public API health and public web route
  are reachable from the local environment when using the same Windows Schannel
  revocation workaround recorded in v3.1.
- It does not satisfy production-like monitoring escalation evidence and does not
  close the v3.5 monitoring issue. Full completion still requires operator-visible
  monitoring coverage for API health, web route, containers, PostgreSQL,
  disk/storage, backup freshness, certificate status, failed jobs, alert
  destination class, fallback path, and response windows.

## v3.5 Existing VPS Monitoring Escalation Evidence

Date: 2026-06-03

Scope:

- Target: existing VPS at `trading.cillyonline.de`.
- Exposure: controlled private owner/operator staging only.
- Data class: sample, synthetic, and paper data only.
- Monitoring model: operator-visible systemd timers plus manual SSH/GitHub review;
  no external alert integration is approved by this evidence.
- Quiet-hours behavior: no overnight reliance. Failed checks are reviewed during
  the next active owner/operator window unless the operator is actively using the
  app.
- Response windows: high severity same day during active staging use; medium
  severity next active owner/operator day; low severity backlog/follow-up.

Technical evidence:

- Compose services: PASS, API, web, Caddy, and PostgreSQL running.
- PostgreSQL health: PASS, PostgreSQL container healthy.
- API direct route: PASS, `http://127.0.0.1:8000/api/health` returned healthy
  staging status.
- Public web route: PASS, `https://trading.cillyonline.de/` returned `HTTP 200`
  through Caddy.
- Disk/storage: PASS, root filesystem used 9% with substantial free space.
- Docker usage: REVIEWED, images and build cache are present; no cleanup was run.
- Health timer: PASS, `cilly-vps-health-check.timer` active and waiting.
- Last health-check service run: PASS, exited `0/SUCCESS` with `failed_checks=0`.
- Health-check evidence included PASS statuses for HTTPS route, PostgreSQL, API,
  web, Caddy, disk usage, and backup freshness.
- Backup timer: PASS, `cilly-postgres-backup.timer` active and waiting.
- Last backup service run: PASS, exited `0/SUCCESS`.
- Backup freshness: PASS for private staging, latest listed PostgreSQL dump was
  from 2026-06-03 and non-zero.
- Recent backup artifacts: REVIEWED, five recent non-zero dump files listed under
  the external backup directory.
- Failed jobs: PASS for reviewed timer status; latest health and backup services
  were inactive/dead after successful one-shot completion, not failed.
- Certificate/public route status: PASS for web route HTTP response through Caddy;
  no separate certificate-expiry monitor is approved by this evidence.

Escalation evidence:

- Alert destination class: manual SSH/GitHub review by owner/operator.
- Fallback path: direct manual SSH status checks using this checklist and the
  operational incident runbook.
- Quiet-hours behavior: no overnight reliance; review in next active operator
  window unless actively using the app.
- Owner/operator response window accepted: yes for private staging only.
- Failed-monitoring No-Go behavior accepted: yes. If health, route, database,
  backup freshness, or timer checks fail, stronger reliance stops until reviewed
  or explicitly accepted.
- Secrets/private data/raw logs included: no.
- Production-like exposure approved by this evidence: no.

Remaining gaps:

- This does not configure external alerting, push, email, Telegram, phone, or a
  third-party monitoring dashboard.
- This does not satisfy offsite encrypted backup or restore-drill evidence; that
  remains tracked separately.
- This does not approve routine private trading data, production-like exposure,
  broker integration, automatic execution, live/realtime claims, profitability
  claims, or trading advice.

## Escalation Triggers

Create a follow-up issue or incident record when any of these occur:

- API health or web route fails repeatedly.
- PostgreSQL is unhealthy or DB-backed pages fail.
- Backup freshness is unknown, backup files are missing, or restore evidence is stale.
- Disk usage approaches the documented threshold.
- Containers repeatedly restart.
- Logs show repeated config guard, auth, Caddy certificate, provider-sync, import, or database errors.
- Monitoring evidence cannot be shared safely without exposing secrets or private trading data.

Use the [Operational Incident Runbook](OPERATIONAL_INCIDENT_RUNBOOK.md) for severity, first response, sanitized evidence, rollback, restore, and escalation handling. Passing this checklist or following the runbook does not create a production-readiness, broker-readiness, real-money-readiness, profitability, trading-advice, or automatic-execution claim.

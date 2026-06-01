# Application Monitoring Checklist

## Purpose

This checklist defines the minimum monitoring review expected before relying more heavily on the app in owner/operator environments.

It is not a monitoring service integration, production-readiness claim, SLA, trading alerting system, broker readiness statement, or profitability evidence.

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

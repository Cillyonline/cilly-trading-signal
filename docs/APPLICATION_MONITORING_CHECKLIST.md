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
- Incident handling: failures that affect login, data integrity, backups, restores, or public routing are handled through the operational incident runbook once available.

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

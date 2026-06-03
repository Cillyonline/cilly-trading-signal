# Production-Like Monitoring Escalation Plan

## Purpose

This plan defines the monitoring, escalation, and sanitized evidence expected
before production-like exposure can be reconsidered.

It is not a monitoring integration, alert delivery setup, service-level
objective, production-readiness approval, security certification, broker-readiness
claim, profitability claim, trading advice, or approval for automatic execution.

## Current Decision

Status: planning evidence only.

Production-like exposure remains No Go until a separate current decision gate
records complete evidence and explicit owner/operator residual-risk acceptance.

## Required Coverage

| Area | Required signal | Initial threshold before escalation | Expected operator response | Evidence boundary |
| --- | --- | --- | --- | --- |
| API health | Caddy-routed `/api/health` check | Repeated failure or unexpected response | Stop relying on app output, check sanitized `/api/health/details` if safe, inspect service status, open incident/follow-up. | Route category, pass/fail, timestamp, commit; no headers, cookies, tokens, or raw logs. |
| Web route | HTTPS web route check | Repeated non-2xx/3xx response, TLS error, or unreachable route | Stop public reliance, verify Caddy/container state, confirm direct ports remain private, follow deployment runbook. | HTTP status category and sanitized service names only. |
| Containers | Expected services running without restart loop | Any required service exited/unhealthy or repeated restarts | Freeze data-changing workflows, inspect sanitized status/log tails, check disk and DB health. | Service names and pass/fail only. |
| PostgreSQL | Container health and DB-backed page behavior | Unhealthy DB, login failure caused by DB, migration mismatch, or DB-backed pages failing | Stop data-changing workflows, confirm backup freshness, avoid destructive repair without approval. | Health category and migration version only. |
| Disk and storage | Root/Docker/PostgreSQL/backup usage | Usage approaches the documented local threshold for safe writes and backups | Pause deploys/imports/backups likely to worsen pressure, preserve DB/backups, open follow-up. | Usage percentage/range only; avoid sensitive paths. |
| Backup freshness | Latest backup exists, non-zero, outside repo, expected target class | Missing, stale, zero-size, failed timer, failed Restic check, or stale restore evidence | Treat private-data/production-like reliance as blocked, run backup/restore triage only with approval. | Target category, snapshot ID prefix, pass/fail; no dump contents, repo credentials, or private paths. |
| Certificate expiry | HTTPS certificate validity and renewal status | Certificate invalid, near expiry within the accepted response window, or renewal failing | Treat route as unreliable, inspect Caddy status, avoid DNS/firewall changes without approval. | Expiry date/range and route category only. |
| Failed jobs | Deploy, backup, restore, provider sync, import, health check, smoke check | Repeated failure or any failure affecting data integrity, backups, restores, or routing | Stop affected workflow reliance, record sanitized failure category, open incident/follow-up. | Job name, status, follow-up link; no raw logs with secrets/private data. |

## Alert Destination Requirements

Before production-like reconsideration, the owner/operator must define:

- Which destination receives API health, web route, container, database, backup,
  disk, certificate, and failed-job alerts.
- Quiet-hours behavior and whether alerts are delayed, suppressed, or escalated.
- Response windows for high, medium, and low operational failures.
- A fallback path when the primary alert destination fails.
- Who is allowed to view alert evidence and where sanitized records are kept.

Do not record tokens, chat IDs, phone numbers, private email addresses, provider
account details, monitoring dashboard secrets, webhook URLs, or raw notification
payloads in repository docs, issues, PRs, screenshots, or chat.

## Escalation Levels

| Level | Examples | Required response |
| --- | --- | --- |
| High | API unavailable, DB unhealthy, repeated restarts, missing backups, restore uncertainty, certificate failure on exposed route. | Stop app reliance, freeze data-changing workflows, open incident record, confirm backup status before repair. |
| Medium | Backup stale but recent safe copy exists, failed provider sync, repeated import failure, failed scheduled health check with manual pass. | Stop relying on affected workflow, create follow-up, resolve before broader reliance. |
| Low | One-off transient check failure with immediate manual pass and no data impact. | Record sanitized note if relevant and watch for recurrence. |

## No-Go Conditions

Production-like reliance remains blocked when any of these are true:

- Required health, web route, database, backup, disk, certificate, or failed-job
  monitoring is absent.
- Alert destination, fallback, quiet-hours behavior, or response window is unclear.
- The operator cannot receive or respond to high-severity alerts within the
  accepted window.
- Backup freshness or restore evidence is stale, missing, or unverifiable.
- Monitoring evidence cannot be shared safely without exposing secrets, private
  data, raw logs, credentials, or provider/account context.
- A failed monitoring check is accepted silently without follow-up or documented
  owner/operator acceptance.

## Evidence Template

```markdown
## Monitoring Escalation Evidence

- Date/time UTC:
- Environment: private staging / production-like candidate / disposable target
- Commit SHA:
- Health route status:
- Web route status:
- Required containers status:
- PostgreSQL status:
- Disk/storage threshold status:
- Backup freshness status:
- Certificate status:
- Failed jobs status:
- Alert destination class reviewed: yes/no
- Fallback path reviewed: yes/no
- Operator response window accepted: yes/no
- Open incidents or follow-ups:
- Secrets/private data/raw logs included: no
- Production-like exposure approved by this evidence: no
```

## Final Statement

This plan defines evidence expectations only. It does not install monitoring,
configure alerts, approve production-like exposure, approve private-data reliance,
or permit broker integration, automatic execution, trading advice, live/realtime
claims, or profitability claims.

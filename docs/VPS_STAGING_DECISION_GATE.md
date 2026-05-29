# Private VPS Staging Decision Gate

## Purpose

This document records the decision gate for private VPS staging use after the initial VPS inventory, deployment planning, environment checklist, backup/restore verification, monitoring baseline, operations hardening, and post-hardening smoke test.

This is a controlled staging decision only. It is not a production-readiness statement, public SaaS approval, broker-readiness claim, profitability claim, trading advice, or approval for automatic execution.

## Decision

Status: Go for private staging only.

Date: 2026-05-29.

Decision rationale:

- The private VPS staging deployment passed the documented smoke test in `docs/VPS_STAGING_SMOKE_TEST.md`.
- The post-hardening VPS smoke test passed in `docs/VPS_STAGING_SMOKE_TEST.md` after firewall, deploy-user, backup, and health-monitoring changes.
- HTTPS routing, API health, web health, migrations, TLS issuance, login, sample-data browser workflow, logout, and protected-route behavior passed.
- The unrelated existing `staging` Compose project remained separate and running.
- Backup/restore mechanics were verified on a disposable VPS-like Compose project with external backup storage, documented in `docs/MVP_RELEASE_CHECKLIST.md`.
- Minimum monitoring checks are documented in `docs/DEPLOYMENT_RUNBOOK.md`.
- Host firewall hardening was applied and persisted with sanitized evidence recorded in `docs/VPS_STAGING_SMOKE_TEST.md`.
- The non-root deploy-user path was applied for routine operations and verified with sanitized evidence recorded in `docs/VPS_STAGING_SMOKE_TEST.md`.
- The private VPS PostgreSQL backup schedule and retention policy were applied through a systemd timer and verified with sanitized evidence recorded in `docs/VPS_STAGING_SMOKE_TEST.md`.
- The minimum automated VPS health-check timer was applied and verified with sanitized evidence recorded in `docs/VPS_STAGING_SMOKE_TEST.md`.

## Approved Use

This gate approves:

- Private staging access for the project owner/operator.
- Sample-data and paper-data validation.
- Manual review of explainable signals.
- Manual trade logging for sample or paper records.
- Continued VPS staging checks using the deployment runbook.

## Not Approved

This gate does not approve:

- Public SaaS launch.
- Real-money readiness.
- Broker integration.
- Automatic order execution.
- Profitability claims.
- Trading advice claims.
- Handling private trading data without a separate operational readiness review.
- Treating the VPS as production without a separate production gate.

## Evidence Summary

Inventory and constraints:

- `docs/VPS_INVENTORY.md` records the VPS as a netcup KVM VPS running Debian 13 with Docker and Docker Compose available.
- The server already hosts an unrelated Compose project named `staging` that must not be modified.
- Existing public `80` and `443` listeners were not observed before this app's Caddy profile started.
- The existing staging API uses `127.0.0.1:18000`, so this app avoids that port.
- Runtime data, backups, and logs must stay outside the repository checkout; `.env` remains untracked and server-local.

Deployment and environment posture:

- `docs/VPS_STAGING_PLAN.md` defines the non-disruptive deployment plan and rollback boundary for Compose project `cilly-trading-signal`.
- `docs/VPS_ENVIRONMENT_CHECKLIST.md` defines required staging environment values and secret-handling rules.
- The VPS `.env` file was created only on the server, remained untracked, and unsafe placeholders were replaced.
- The stack was started with an explicit `--env-file .env` to ensure Compose used the intended staging values.

Backup and restore:

- `docs/MVP_RELEASE_CHECKLIST.md` records a passed VPS-like backup/restore mechanics check using the disposable Compose project `cilly_br_verify`.
- Backup output used `/srv/backups/cilly-trading-signal/postgres`, outside the repository checkout.
- Restore verification used disposable sample marker data only and did not touch the unrelated `staging` project or real data.

Monitoring baseline:

- `docs/DEPLOYMENT_RUNBOOK.md` documents checks for API health, containers, logs, PostgreSQL health, HTTPS/Caddy routing, disk space, memory/load, and backup freshness.
- During active staging use, health, containers, disk, and backup freshness should be checked daily.
- `cilly-vps-health-check.timer` is enabled for private staging and reports sanitized PASS/FAIL output for API, HTTPS, Compose, disk, and backup freshness checks.

Operations hardening:

- `docs/VPS_FIREWALL_HARDENING_PLAN.md` defines the minimal nftables firewall posture.
- The firewall was applied and persisted through `nftables`, preserving SSH, Caddy `80`/`443`, Docker behavior, direct localhost-only app ports, and the unrelated `staging` project.
- `docs/VPS_DEPLOY_USER_RUNBOOK.md` defines the non-root `cillydeploy` routine operation path.
- `cillydeploy` can SSH with the operator key, authenticate to GitHub with the read-only deploy key, run Git fetch/pull, and run Docker Compose status checks without broad passwordless sudo.
- `cilly-postgres-backup.timer` is enabled for daily PostgreSQL backups under `/srv/backups/cilly-trading-signal/postgres` with retention configured and no dumps in the repository checkout.

Smoke tests:

- `docs/VPS_STAGING_SMOKE_TEST.md` records the first private VPS staging smoke test as passed.
- `docs/VPS_STAGING_SMOKE_TEST.md` records the post-hardening VPS smoke test as passed.
- DNS resolved for `trading.cillyonline.de`.
- Caddy obtained a Let's Encrypt certificate.
- Direct local API and web checks passed.
- HTTPS API and web checks passed.
- Migrations completed through `20260517_0005`.
- Browser workflow checks passed for login, dashboard, watchlist, CSV import, analysis, signals list, signal detail, trades page, performance page, logout, and protected-route behavior after logout.
- After hardening, browser checks passed for app load, login, dashboard, watchlist, signals, trades, performance, logout, protected page after logout, and safety wording.

## Known Risks

- Swap is not configured on the VPS.
- This gate is based on sample/paper data only and does not validate real-money operations or private trading data handling.
- The post-hardening smoke test confirms availability, authentication, operational hardening, and safety wording only; it does not validate that current page content is trader-actionable or suitable for real-money decisions.
- Backup automation currently stores local VPS backups only; offsite and encrypted backup storage remain outside this gate.
- The health-check timer is a private staging safety net, not a full observability stack, paging system, SLA, SLO, or production monitoring platform.

## Required Follow-Ups

- Consider swap configuration if VPS memory pressure appears during active staging use.
- Define offsite and encrypted backup storage before handling private trading data or relying on the VPS regularly.
- Re-run the smoke test after any DNS, Caddy, firewall, Docker, migration, environment, backup, or monitoring change.
- Keep current content and signal quality separate from operations readiness; do not treat reachable pages as trader-actionable validation.

## Reopen The Gate If

- The app is exposed beyond private staging.
- Real user data, private trading data, or real-money workflows are introduced.
- Broker integration or automatic execution is proposed.
- VPS firewall, reverse proxy, Docker networking, storage, or backup strategy materially changes.
- The unrelated `staging` project is affected or begins sharing routing, storage, ports, or operational procedures with this app.
- Smoke tests, backups, restores, or monitoring checks fail.

## Final Gate Statement

Private VPS staging is accepted for controlled owner/operator use only after the documented hardening and post-hardening smoke test. Broader production-like use, public SaaS use, real-money workflows, private trading data handling, broker integration, automatic execution, trading advice claims, and profitability claims remain blocked until a separate operational readiness decision explicitly approves them.

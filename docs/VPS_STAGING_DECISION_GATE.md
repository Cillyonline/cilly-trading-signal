# Private VPS Staging Decision Gate

## Purpose

This document records the decision gate for private VPS staging use after the initial VPS inventory, deployment planning, environment checklist, backup/restore verification, monitoring baseline, and smoke test.

This is a controlled staging decision only. It is not a production-readiness statement, public SaaS approval, broker-readiness claim, profitability claim, trading advice, or approval for automatic execution.

## Decision

Status: Conditional Go for private staging only.

Date: 2026-05-29.

Decision rationale:

- The private VPS staging deployment passed the documented smoke test in `docs/VPS_STAGING_SMOKE_TEST.md`.
- HTTPS routing, API health, web health, migrations, TLS issuance, login, sample-data browser workflow, logout, and protected-route behavior passed.
- The unrelated existing `staging` Compose project remained separate and running.
- Backup/restore mechanics were verified on a disposable VPS-like Compose project with external backup storage, documented in `docs/MVP_RELEASE_CHECKLIST.md`.
- Minimum monitoring checks are documented in `docs/DEPLOYMENT_RUNBOOK.md`.
- The minimal host firewall hardening plan is documented in `docs/VPS_FIREWALL_HARDENING_PLAN.md`; application remains an operator-run follow-up until sanitized VPS evidence is recorded.
- Remaining operational hardening items are acceptable for private staging only, not for broader production-like or public use.

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
- Runtime data, backups, logs, and `.env` files must stay outside `/root/repos/cilly-trading-signal`.

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

Smoke test:

- `docs/VPS_STAGING_SMOKE_TEST.md` records the first private VPS staging smoke test as passed.
- DNS resolved for `trading.cillyonline.de`.
- Caddy obtained a Let's Encrypt certificate.
- Direct local API and web checks passed.
- HTTPS API and web checks passed.
- Migrations completed through `20260517_0005`.
- Browser workflow checks passed for login, dashboard, watchlist, CSV import, analysis, signals list, signal detail, trades page, performance page, logout, and protected-route behavior after logout.

## Known Risks

- Host firewall hardening is planned but not yet operator-applied; the current private staging acceptance relies on the documented provider/iptables posture.
- Deployment currently uses root SSH access; a non-root deploy user remains a follow-up.
- Backup automation and retention policy are not yet fully operationalized for ongoing staging use.
- Monitoring is documented as a manual baseline, not an automated alerting system.
- Swap is not configured on the VPS.
- This gate is based on sample/paper data only and does not validate real-money operations or private trading data handling.

## Required Follow-Ups

- Apply the documented minimal host firewall plan and record sanitized evidence that SSH, Caddy, Docker behavior, localhost-only direct app ports, and the existing project routing remain intact.
- Create or document a non-root deploy user for routine operations where feasible.
- Automate PostgreSQL backups and define retention for private staging.
- Add or document automated uptime/health monitoring if staging becomes relied on regularly.
- Re-run the smoke test after any DNS, Caddy, firewall, Docker, migration, or environment change.

## Reopen The Gate If

- The app is exposed beyond private staging.
- Real user data, private trading data, or real-money workflows are introduced.
- Broker integration or automatic execution is proposed.
- VPS firewall, reverse proxy, Docker networking, storage, or backup strategy materially changes.
- The unrelated `staging` project is affected or begins sharing routing, storage, ports, or operational procedures with this app.
- Smoke tests, backups, restores, or monitoring checks fail.

## Final Gate Statement

Private VPS staging is accepted with known risks for controlled owner/operator use only. Broader production-like use remains blocked until a separate operational readiness decision addresses security hardening, deploy-user posture, backup automation, monitoring automation, and data-handling requirements.

# VPS Staging Plan

## Purpose

This document defines the non-disruptive private VPS staging deployment plan for this project.

It is based on the sanitized read-only inventory in `docs/VPS_INVENTORY.md`. It is a planning artifact only and does not approve production readiness, real-money trading, broker integration, automatic execution, or public SaaS operation.

## Safety Boundaries

- The app remains decision-support only.
- No broker integration.
- No automatic order execution.
- No profitability, production-readiness, or real-money readiness claim.
- Existing VPS projects must not be modified, restarted, rebuilt, or reconfigured by this plan.
- Secrets, `.env` contents, tokens, cookies, private keys, database URLs, backup dumps, logs with sensitive data, and private trading data must not be committed or pasted into issues, PRs, docs, or screenshots.

## Current VPS Constraints

Source: `docs/VPS_INVENTORY.md`.

- Existing Compose project: `staging`.
- Existing localhost-bound API port: `127.0.0.1:18000->8000/tcp`.
- Public web ports `80` and `443` were not observed as listening.
- No Caddy, Nginx, or Traefik systemd service was observed.
- Docker is already installed and running.
- `ufw` and `firewalld` were not found.
- iptables default `INPUT` policy is `ACCEPT`.
- Existing project data uses bind mounts under `/srv/cilly/staging`.
- Existing backup directories `/srv/backups` and `/srv/backups/manual` exist.

## Deployment Shape

Use this repository's Docker Compose stack with the `proxy` profile so Caddy owns the public web entrypoint for this app.

Planned services:

- `postgres`: app-specific PostgreSQL database.
- `api`: FastAPI backend.
- `web`: Next.js frontend.
- `caddy`: HTTPS reverse proxy for this app.

Routing model:

- Public `https://<app-domain>/` routes to `web:3000` through Caddy.
- Public `https://<app-domain>/api/*` routes to `api:8000` through Caddy.
- Direct API and web host ports stay localhost-only.
- No public access is planned for PostgreSQL.

## Paths

Repository checkout:

```text
/root/repos/cilly-trading-signal
```

Runtime data and backups must stay outside the repository checkout.

Recommended app-specific paths:

```text
/srv/cilly-trading-signal/
/srv/cilly-trading-signal/postgres/
/srv/cilly-trading-signal/caddy-data/
/srv/cilly-trading-signal/caddy-config/
/srv/backups/cilly-trading-signal/postgres/
```

The exact runtime paths can be implemented with Docker named volumes or bind mounts in a later implementation issue. Do not store PostgreSQL data, backups, `.env` copies, logs, or dump files under `/root/repos/cilly-trading-signal`.

Paths that must not be reused or modified:

- `/srv/cilly/staging`
- Existing `trading-engine` app, data, log, and backup paths
- Existing `staging` Compose project files

## Compose Project And Ports

Recommended Compose project name:

```text
cilly-trading-signal
```

Reserved / avoided host ports:

- Do not use `18000`; it is already used by an existing localhost-bound API.

Expected public ports:

- `80/tcp`: Caddy HTTP challenge / redirect path.
- `443/tcp`: Caddy HTTPS.

Expected private/local-only ports:

- `127.0.0.1:8000->8000/tcp` for API operator checks if retained.
- `127.0.0.1:3000->3000/tcp` for web operator checks if retained.

PostgreSQL should remain internal to Docker networking and must not publish a host port unless a separate approved issue explicitly requires it.

## Domain And DNS

Choose a dedicated subdomain for this app in #158 before deployment commands are run.

Recommended shape:

```text
trading.<domain>
```

DNS requirements:

- `A` record points to the VPS public IPv4 address.
- Optional `AAAA` only if IPv6 routing and firewall posture are intentionally supported.
- DNS should be confirmed before starting Caddy with the proxy profile.

Do not commit private domain details if they should remain confidential.

## Environment Strategy

The VPS `.env` file must be created on the server only and must not be committed.

Required staging posture:

- `ENVIRONMENT=staging` or `production` for production-like config guards.
- `AUTH_COOKIE_SECURE=true` for HTTPS.
- `CORS_ORIGINS` uses the exact HTTPS app origin.
- `NEXT_PUBLIC_API_BASE_URL=/api` for same-origin Caddy routing.
- `SECRET_KEY`, `ADMIN_INITIAL_PASSWORD`, `POSTGRES_PASSWORD`, and `TRADINGVIEW_WEBHOOK_SECRET` must be strong unique values.
- `DATABASE_URL` must use non-default PostgreSQL credentials.
- Telegram values remain optional until alert routing is explicitly implemented and approved.

Detailed environment checklist: `docs/VPS_ENVIRONMENT_CHECKLIST.md`.

## Firewall Decision Gate

Current inventory found no `ufw` or `firewalld`, and iptables default `INPUT` policy is `ACCEPT`.

Before starting any public service, choose one of these options explicitly:

1. Add a minimal host firewall policy that allows only required ports such as SSH, `80`, and `443`.
2. Keep the current provider/iptables posture and accept the risk for private staging with explicit documentation.

Recommended professional path: add a minimal firewall policy in a separate approved operations issue before public exposure, while preserving SSH access and existing Docker behavior.

Do not change firewall rules as part of this planning issue.

## Deployment Procedure Draft

This is a planned sequence, not an instruction to run now.

1. Confirm PRs for #158 and #159 are merged.
2. Confirm domain/subdomain and DNS.
3. Confirm firewall decision.
4. SSH to the VPS.
5. Create or confirm repository parent path `/root/repos`.
6. Clone repository to `/root/repos/cilly-trading-signal`.
7. Create `.env` on the VPS from `.env.example` and replace all unsafe placeholders.
8. Confirm `.env` is not tracked and not copied into logs or issues.
9. Start stack with the Caddy proxy profile:

```bash
docker compose -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy up --build -d
```

10. Check services:

```bash
docker compose -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy ps
```

11. Check public API health through HTTPS:

```bash
curl -fsS https://<app-domain>/api/health
```

12. Continue with the VPS smoke test from #163.

## Rollback / Stop Procedure Draft

Stop only this app's Compose project:

```bash
docker compose -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy down
```

Do not run:

```bash
docker compose down --volumes
docker volume prune
docker system prune
```

Do not stop, restart, or modify the existing `staging` Compose project.

If public routing fails, stop this app's Compose project and verify the existing `staging` project remains healthy.

## Go / No-Go Criteria

Go for first private VPS staging deployment only when:

- Existing `staging` project remains untouched.
- Domain/subdomain is chosen and DNS points to the VPS.
- Firewall posture is explicitly accepted or improved.
- `.env` checklist from #159 is complete.
- Strong non-default secrets are prepared outside the repo.
- Runtime data and backup paths are separated from the repository checkout.
- Rollback command is known and scoped to `cilly-trading-signal` only.
- No unresolved port conflict exists on `80`, `443`, `3000`, `8000`, or `18000`.

No-go if:

- Any command would affect the existing `staging` project.
- SSH access could be locked out by firewall changes.
- Secrets would need to be copied into docs, issues, PRs, screenshots, or logs.
- Caddy cannot own `80`/`443` safely.
- Backup and restore expectations are unclear for any non-disposable data.

## Open Decisions

- Exact app domain/subdomain.
- Whether to add host firewall hardening before first staging deployment.
- Whether to create a non-root deploy user before first staging deployment.
- Whether to change Docker volumes to app-specific bind mounts under `/srv/cilly-trading-signal` in a later implementation issue.
- Whether to configure swap before adding the app stack.

## Follow-Ups

- #159: prepare VPS staging environment checklist.
- #161: define minimum monitoring checks in `docs/DEPLOYMENT_RUNBOOK.md`.
- #162: verify PostgreSQL backup and restore path on VPS-like staging. Evidence is recorded in `docs/MVP_RELEASE_CHECKLIST.md`.
- #163: run first private VPS smoke test after deployment approval.
- #164: document private VPS go/no-go decision gate.

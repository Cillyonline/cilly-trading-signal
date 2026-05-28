# VPS Staging Smoke Test

## Purpose

This document tracks the first private VPS staging smoke test for the single-user trading cockpit.

It is a controlled staging validation artifact. It is not a production-readiness statement, profitability claim, trading advice, broker-readiness claim, public SaaS readiness claim, or approval for automatic execution.

## Safety Scope

- Decision-support only.
- Manual trade execution only.
- No broker integration.
- No automatic order execution.
- No real-money trading validation.
- Use sample or paper data only.
- Do not commit or paste secrets, `.env` contents, cookies, database URLs, private keys, backup dumps, logs with sensitive data, screenshots with sensitive data, or private trading data.
- Do not modify, restart, or stop unrelated VPS projects.

## Preconditions

Completed:

- VPS inventory documented in `docs/VPS_INVENTORY.md`.
- Non-disruptive deployment plan documented in `docs/VPS_STAGING_PLAN.md`.
- Staging environment checklist documented in `docs/VPS_ENVIRONMENT_CHECKLIST.md`.
- Login rate limiting merged for single-admin auth.
- Minimum monitoring checks documented in `docs/DEPLOYMENT_RUNBOOK.md`.
- VPS-like disposable backup/restore verification documented in `docs/MVP_RELEASE_CHECKLIST.md`.
- Disposable backup/restore test stack `cilly_br_verify` was stopped after verification.
- Existing unrelated Compose project `staging` remained separate and running during preparation.

Pending / gated:

- DNS `A` record for the selected app subdomain must resolve to the VPS.
- The real app domain is intentionally not recorded in this document unless explicitly approved.
- VPS `.env` must be prepared from `docs/VPS_ENVIRONMENT_CHECKLIST.md` on the server only.
- Firewall posture must be explicitly accepted or hardened before public binding.

## Current Status

- Issue: #163
- Status: Blocked on DNS propagation and staging `.env` preparation
- App domain: `<app-domain>`
- VPS repository path: `/root/repos/cilly-trading-signal`
- Compose project: `cilly-trading-signal`
- Existing unrelated project to preserve: `staging`

## DNS Gate

Before starting the Caddy proxy profile, confirm DNS resolves to the VPS.

PowerShell from operator machine:

```powershell
nslookup <app-domain>
```

Linux/VPS:

```bash
getent hosts <app-domain>
```

Expected:

- The app domain resolves to the VPS public IPv4 address.
- If an `AAAA` record exists, IPv6 routing and firewall posture are intentional.

No-go:

- DNS does not resolve.
- DNS resolves to a different host.
- DNS is still propagating and Caddy cannot obtain a certificate.

## Staging Environment Gate

Create `.env` only on the VPS from `.env.example`, then replace all unsafe placeholders. Do not commit or paste the file.

Required checks from `/root/repos/cilly-trading-signal`:

```bash
test -f .env
git status --short -- .env .env.example
grep -nE 'change-this|change-me|admin@example.com|postgres:postgres|AUTH_COOKIE_SECURE=false|CORS_ORIGINS=.*\*' .env && echo 'UNSAFE_PLACEHOLDER_FOUND' || echo 'No known unsafe placeholders found'
for key in APP_DOMAIN ENVIRONMENT DATABASE_URL SECRET_KEY ADMIN_EMAIL ADMIN_INITIAL_PASSWORD AUTH_COOKIE_SECURE TRADINGVIEW_WEBHOOK_SECRET CORS_ORIGINS NEXT_PUBLIC_API_BASE_URL POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB; do grep -q "^${key}=" .env && echo "${key}=present" || echo "${key}=missing"; done
```

Expected:

- `.env` exists and remains untracked.
- No known unsafe placeholders are found.
- Required keys are present.
- `ENVIRONMENT=staging` or a consciously approved production-like value.
- `AUTH_COOKIE_SECURE=true`.
- `NEXT_PUBLIC_API_BASE_URL=/api`.

## Pre-Start Checks

Run before starting this app's stack:

```bash
cd /root/repos/cilly-trading-signal
git status --short --branch
git pull --ff-only origin main
docker compose ls
ss -tulpen | grep -E ':(3000|8000|18000|80|443)\b' || true
```

Expected:

- Repo checkout is clean on `main`.
- Existing `staging` project remains running.
- Port `18000` remains reserved for the existing project.
- Ports `80` and `443` are available before Caddy starts.
- Ports `3000` and `8000` are available or only used by this app after startup.

## Start Procedure

Run only after DNS, environment, and pre-start checks pass.

```bash
docker compose -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy up --build -d
```

Check status:

```bash
docker compose -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy ps
docker compose ls
```

Expected:

- `postgres`, `api`, `web`, and `caddy` are running.
- Existing `staging` project remains running.
- No unrelated project state changed.

## Health Checks

Direct local checks on the VPS:

```bash
curl -fsS http://localhost:8000/api/health
curl -fsSI http://localhost:3000
```

Caddy/HTTPS checks:

```bash
curl -fsS https://<app-domain>/api/health
curl -fsSI https://<app-domain>/
```

Expected:

- API health returns `status: ok`.
- Web responds through Caddy over HTTPS.
- Browser-facing API uses same-origin `/api` routing.

## Browser Workflow

Use sample or paper data only.

1. Open `https://<app-domain>/`.
2. Log in with the staging admin credentials from the password manager.
3. Verify dashboard loads.
4. Verify protected routes redirect or block unauthenticated access after logout.
5. Create or verify a clearly fake sample watchlist item.
6. Import sample CSV fixtures from `test-data/csv/` for `1W`, `1D`, and `4H`.
7. Run analysis.
8. Review signals list and signal detail.
9. Verify manual trade logging page loads; use sample/paper values only if a trade record is created.
10. Verify performance page loads.
11. Log out.
12. Confirm protected API data is denied after logout.

## Evidence To Record

Record sanitized outcomes only:

- Date/time.
- DNS resolution status.
- Compose project status.
- Direct API health result.
- HTTPS API health result.
- Web load result.
- Browser workflow pass/fail notes.
- Logout/protected-data behavior.
- Existing `staging` project remained unaffected.
- Known gaps.

Do not record:

- Real domain if it should remain private.
- Secrets or `.env` values.
- Cookies.
- Private trading data.
- Screenshots with sensitive data.
- Backup dump contents.

## Rollback / Stop

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

Do not stop or restart the existing unrelated `staging` project.

## Current Result

Status: Not run.

Reason: DNS record has been created at the provider but may take up to 48 hours to propagate. The HTTPS/Caddy smoke test is blocked until the selected app domain resolves to the VPS.

## Follow-Ups

- Complete this smoke test after DNS propagation.
- Then document the private VPS go/no-go decision in #164.

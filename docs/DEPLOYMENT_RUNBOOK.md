# Deployment Runbook

## Purpose

This runbook describes a repeatable VPS deployment path for the single-user MVP using Docker Compose, PostgreSQL, and Caddy.

It is an operational guide, not a production-readiness guarantee. Before real operation, backups, monitoring, restore tests, secret rotation, and a security review still need to be completed.

For the private VPS staging plan based on the current server inventory, see `docs/VPS_STAGING_PLAN.md`. The staging plan must be reviewed before changing the existing VPS because other projects already run on that server. For the sanitized staging environment checklist, see `docs/VPS_ENVIRONMENT_CHECKLIST.md`.

## Safety Boundaries

- The app is decision-support only.
- Signals and alerts are review prompts, not buy or sell instructions.
- The app does not place orders and has no broker integration.
- Use sample or paper-trading data when validating a fresh deployment.

## Prerequisites

VPS:

- Linux VPS with a supported Docker installation.
- SSH access with a non-root deploy user where possible.
- Public ports `80` and `443` open when using Caddy/HTTPS.
- Direct API and web service ports must not be publicly exposed for Caddy/prod-like deployments. In the provided Compose file they are bound to localhost only for operator checks and local development.
- Sufficient disk space for Docker images, PostgreSQL volume data, and backups.

Local/operator machine:

- Git.
- SSH client.
- Access to the repository.
- Secure password/secret generator.

DNS:

- A domain or subdomain, for example `trading.example.com`.
- DNS `A` record pointing to the VPS public IP.

Repository files used by this runbook:

- `infra/docker-compose.yml`
- `infra/caddy/Caddyfile`
- `.env.example`

## Environment File

Create `.env` on the VPS from `.env.example` and replace every local placeholder before starting a staging or production-like environment.

Local defaults in `.env.example` are intentionally unsafe outside `development` and `test`. When `ENVIRONMENT` is any other value, the API fails fast if protected settings still use known local placeholders or unsafe values.

Required values:

- `APP_DOMAIN`: public domain used by Caddy, for example `trading.example.com`.
- `ENVIRONMENT`: use `staging` or `production` outside local development.
- `DATABASE_URL`: PostgreSQL URL used by the API.
- `SECRET_KEY`: strong random session signing secret.
- `ADMIN_EMAIL`: single admin login email.
- `ADMIN_INITIAL_PASSWORD`: strong initial admin password.
- `AUTH_COOKIE_SECURE`: `true` for HTTPS deployments.
- `CORS_ORIGINS`: exact web origin list, not wildcard.
- `POSTGRES_USER`: PostgreSQL user.
- `POSTGRES_PASSWORD`: strong PostgreSQL password.
- `POSTGRES_DB`: PostgreSQL database name.
- `NEXT_PUBLIC_API_BASE_URL`: browser-facing API base URL. Use `/api` for same-origin Caddy routing, or an explicit `https://<APP_DOMAIN>/api` URL when needed.

Optional values for later alert work:

- `TRADINGVIEW_WEBHOOK_SECRET`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Do not commit `.env` or paste secrets into issues, PRs, logs, or screenshots.

## Production Secrets And Config Guards

Use a secret generator for `SECRET_KEY`, `ADMIN_INITIAL_PASSWORD`, `POSTGRES_PASSWORD`, and `TRADINGVIEW_WEBHOOK_SECRET`. Prefer at least 32 random characters for secrets and unique values per environment.

For `staging` and `production`, the API rejects unsafe configuration at startup when any of these checks fail:

- `SECRET_KEY` is empty or a known placeholder such as `change-this-secret-key`.
- `TRADINGVIEW_WEBHOOK_SECRET` is empty or a known placeholder such as `change-this-webhook-secret`.
- `ADMIN_EMAIL` is empty or the local default `admin@example.com`.
- `ADMIN_INITIAL_PASSWORD` is empty or a known placeholder such as `change-this-password`.
- `AUTH_COOKIE_SECURE` is not `true`.
- `DATABASE_URL` is empty or uses default PostgreSQL credentials such as `postgres:postgres`.
- `CORS_ORIGINS` contains wildcard origins.

Recommended production-style values:

```dotenv
APP_DOMAIN=trading.example.com
ENVIRONMENT=production
DATABASE_URL=postgresql+psycopg://cilly_app:<strong-db-password>@postgres:5432/cilly_trading_signal
SECRET_KEY=<strong-random-secret>
ADMIN_EMAIL=<your-admin-email>
ADMIN_INITIAL_PASSWORD=<strong-random-password>
AUTH_COOKIE_SECURE=true
TRADINGVIEW_WEBHOOK_SECRET=<strong-random-webhook-secret>
CORS_ORIGINS=["https://trading.example.com"]
NEXT_PUBLIC_API_BASE_URL=/api
POSTGRES_USER=cilly_app
POSTGRES_PASSWORD=<strong-db-password>
POSTGRES_DB=cilly_trading_signal
```

Rotation expectations:

- Rotate `ADMIN_INITIAL_PASSWORD` immediately if it was shared through an unsafe channel.
- Rotate `SECRET_KEY` only with awareness that existing sessions may become invalid.
- Rotate `POSTGRES_PASSWORD` together in both `POSTGRES_PASSWORD` and `DATABASE_URL`.
- Rotate `TRADINGVIEW_WEBHOOK_SECRET` when webhook URLs or payload examples may have leaked.
- After any secret change, restart the stack and confirm login and API health.

Do not store production secrets in shell history, screenshots, issue comments, PR descriptions, or copied terminal output.

## Login Brute-Force Hardening

The single-admin login flow applies a basic in-process failed-login throttle. By default, repeated failed attempts for the same normalized email are temporarily locked after five failures for 60 seconds.

Notes:

- The response remains generic for invalid credentials.
- A throttled login returns HTTP `429`.
- A successful login clears prior failed attempts for that email.
- The throttle is process-local and resets when the API process restarts; it is MVP hardening, not a full intrusion-prevention system.
- The default values can be overridden with `AUTH_LOGIN_MAX_FAILED_ATTEMPTS` and `AUTH_LOGIN_LOCKOUT_SECONDS` if a future deployment needs a different posture.

## First Deployment

1. Connect to the VPS.

```bash
ssh deploy@your-vps
```

2. Install Docker and the Docker Compose plugin using the operating system's documented package source.

3. Clone the repository.

```bash
git clone https://github.com/Cillyonline/cilly-trading-signal.git
cd cilly-trading-signal
```

4. Create the environment file.

```bash
cp .env.example .env
```

5. Edit `.env` and replace local defaults with deployment-safe values.

6. Confirm DNS points to the VPS before starting the Caddy profile.

```bash
dig +short trading.example.com
```

7. Build and start the stack with Caddy.

```bash
docker compose -f infra/docker-compose.yml --profile proxy up --build -d
```

8. Check container state.

```bash
docker compose -f infra/docker-compose.yml --profile proxy ps
```

9. Check API health through the public route.

```bash
curl -fsS https://trading.example.com/api/health
```

10. Open the web app and log in with `ADMIN_EMAIL` and `ADMIN_INITIAL_PASSWORD`.

After first login, rotate the initial password flow if the app supports it in a later issue. Until then, keep the initial password unique and stored securely.

## Caddy And HTTPS

Caddy reads `APP_DOMAIN` from `.env` through Docker Compose interpolation and uses `infra/caddy/Caddyfile`.

Current routing:

- `/api/*` reverse proxies to `api:8000`.
- all other routes reverse proxy to `web:3000`.

For public HTTPS:

- `APP_DOMAIN` must be a real domain, not `localhost`.
- DNS must point at the VPS before Caddy can obtain a certificate.
- Ports `80` and `443` must be reachable from the internet.
- Public browser and API access should use the Caddy HTTPS route, not the direct API or web service ports.
- Direct API and web host ports are intended only for localhost operator checks or local development. If a deployment overrides these bindings, keep them bound to `127.0.0.1` or protect them with firewall rules so they are not internet-reachable.
- Do not treat `http://localhost:8000` or `http://localhost:3000` as public deployment endpoints.

## Updates And Migrations

1. Connect to the VPS and enter the repository.

```bash
ssh deploy@your-vps
cd cilly-trading-signal
```

2. Fetch and update the deployment branch.

```bash
git fetch origin
git switch main
git pull --ff-only origin main
```

3. Rebuild and restart services.

```bash
docker compose -f infra/docker-compose.yml --profile proxy up --build -d
```

4. Run database migrations from the API container.

```bash
docker compose -f infra/docker-compose.yml exec api uv run --with alembic --with pydantic-settings --with sqlalchemy --with "psycopg[binary]" alembic upgrade head
```

5. Re-check health and login.

```bash
curl -fsS https://trading.example.com/api/health
```

## Restart And Stop

Restart all services:

```bash
docker compose -f infra/docker-compose.yml --profile proxy restart
```

Stop services without deleting volumes:

```bash
docker compose -f infra/docker-compose.yml --profile proxy down
```

Do not run `down --volumes` on a VPS unless you intentionally want to remove PostgreSQL data and have a verified backup.

## Disposable Demo Data Reset

### Purpose

Use this procedure only to return a local, disposable demo or validation stack to a clean sample state after smoke tests, CSV imports, signal review, manual trade logging, journal/performance checks, or backup/restore tests.

This is a documentation-only reset path. It does not add automation and it must not be used as a shortcut for staging, production-like, or real data operations.

### Preconditions

Before removing any Docker volume, confirm all of the following:

- You are working in a local or explicitly disposable environment.
- The stack contains only sample, paper-trading, smoke-test, or backup/restore marker data.
- No real trading journal, credentials, user data, production data, or staging evidence must be preserved.
- The Compose project is the intended disposable project, not a VPS staging or production-like deployment.
- Any backup dump you need to keep has already been created, verified, and stored outside the repository working tree.
- `.env`, backup dumps, logs, screenshots, database URLs, credentials, cookies, and secrets have been reviewed and will not be committed or pasted into issues/PRs.

### Safety Classification

Safe only for local disposable demo data:

- Local Docker Desktop stacks started from this repository for smoke-test or demo validation.
- Temporary Compose projects created only for backup/restore verification.
- Environments where the operator can intentionally recreate all data from sample fixtures or manual demo steps.

Unsafe unless explicitly approved:

- Staging or VPS environments that are used for release evidence, handoff, or shared review.
- Production-like environments, even if they currently contain only a small amount of data.
- Any database that may contain real trades, personal journal notes, credentials, private imports, or customer/user data.

If the environment classification is unclear, stop and do not remove volumes.

### What Gets Deleted

For this Compose stack, `docker compose ... down --volumes` removes the named Docker volumes for the selected Compose project. That includes:

- `postgres-data`: PostgreSQL database files, including watchlist items, imports, indicators, signals, manual trades, journal entries, settings, and auth data.
- `caddy-data`: local Caddy state such as local certificates or ACME data for that Compose project.
- `caddy-config`: Caddy runtime configuration state for that Compose project.

It also stops and removes the project's containers and network. It does not delete committed repository files, but it can permanently delete unbacked database state.

### What Must Never Be Deleted Accidentally

Do not remove Docker volumes for:

- Production, staging, or production-like PostgreSQL data.
- VPS Caddy volumes that hold real certificate/account state unless a separate approved operations plan covers it.
- Backup storage such as `/var/backups/cilly-trading-signal/postgres`.
- Any dump that is the only copy of data you may need to restore.
- `.env` files or secret material as part of a shared PR, issue, screenshot, or log bundle.

Do not run broad Docker cleanup commands such as `docker volume prune` for this task. They can remove unrelated volumes from other projects.

### PowerShell Example

Use this only from the repository root on a local disposable stack after the preconditions above are true.

```powershell
git status --short
docker compose -f .\infra\docker-compose.yml --profile proxy ps
docker compose -f .\infra\docker-compose.yml --profile proxy down --volumes
```

The smoke-test runner also exposes an explicit disposable cleanup path:

```powershell
.\scripts\smoke_test.ps1 -Cleanup -PurgeVolumes
```

Run the `-PurgeVolumes` form only when the stack contains disposable demo data. Use `.\scripts\smoke_test.ps1 -Cleanup` when you want to stop containers while preserving volumes.

### Linux/VPS Example

Use this only for a disposable local or temporary Compose project. Do not use it on a staging or production VPS unless an approved operation explicitly says the target data may be destroyed.

```bash
git status --short
docker compose -f infra/docker-compose.yml --profile proxy ps
docker compose -f infra/docker-compose.yml --profile proxy down --volumes
```

For production-like VPS maintenance, prefer stopping without deleting volumes:

```bash
docker compose -f infra/docker-compose.yml --profile proxy down
```

### Backup Warning

PostgreSQL dumps can contain watchlist symbols, imported candles, signals, trades, journal text, auth data, and settings. Treat dumps as sensitive operational data.

- Store backups outside the repository working tree. Do not use repository-relative backup paths for staging, VPS, production-like, or real-data environments.
- Set `BACKUP_DIR` explicitly for operational backups and point it to a directory outside this checkout, for example `/var/backups/cilly-trading-signal/postgres`.
- Do not commit backups, dumps, `.sql`, `.dump`, `.backup`, `.bak`, `.env` files, database URLs, credentials, cookies, logs, screenshots with secrets, or private trading data.
- Do not paste backup contents, database URLs, credentials, cookies, or secret-bearing logs into issues, PRs, screenshots, or support threads.
- Verify a backup before relying on it as the reason a volume can be deleted.
- Do not call a reset safe just because a dump exists; confirm the dump belongs to the same environment and can be restored into a non-production copy.

### Verification After Reset

After removing disposable volumes, recreate and verify the stack before recording new smoke-test evidence.

PowerShell:

```powershell
Copy-Item .env.example .env
docker compose -f .\infra\docker-compose.yml --profile proxy up --build -d
docker compose -f .\infra\docker-compose.yml --profile proxy ps
curl.exe -fsS http://localhost:8000/api/health
curl.exe -k -fsS https://localhost/api/health
```

Linux/VPS-style shell for a disposable project:

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml --profile proxy up --build -d
docker compose -f infra/docker-compose.yml --profile proxy ps
curl -fsS http://localhost:8000/api/health
curl -k -fsS https://localhost/api/health
```

If the stack was started from a fresh database and migrations are not applied by the startup path, run the migration command from the [Updates And Migrations](#updates-and-migrations) section, then re-check health.

### How To Recreate Demo State

After the reset:

1. Log in with local disposable admin credentials from `.env`.
2. Create a clearly fake sample watchlist item, for example `SMOKE-PAPER-001`.
3. Import deterministic sample CSV fixtures from `test-data/csv/` for the required timeframes.
4. Run analysis and review conservative signal output, including `No Setup` or `No Trade` outcomes where applicable.
5. Create manual trade and journal records only with sample or paper values.
6. For backup/restore validation, create a fresh backup from the disposable state and restore it only into another disposable target.

### References

- [Deployment Smoke Test Checklist](#deployment-smoke-test-checklist)
- [PostgreSQL Backups](#postgresql-backups)
- [PostgreSQL Restore](#postgresql-restore)
- [MVP Smoke Test](MVP_SMOKE_TEST.md)

## Healthchecks And Logs

Use these checks after deploys, restarts, restores, and configuration changes. Do not paste full logs into issues or chat without reviewing them for secrets, cookies, tokens, database URLs, email addresses, and trade/journal content.

Container status:

```bash
docker compose -f infra/docker-compose.yml --profile proxy ps
```

API health through Caddy:

```bash
curl -fsS https://trading.example.com/api/health
```

API health directly on the VPS:

```bash
curl -fsS http://localhost:8000/api/health
```

Web response through Caddy:

```bash
curl -I https://trading.example.com
```

PostgreSQL health from the Compose service:

```bash
docker compose -f infra/docker-compose.yml exec postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Recent logs:

```bash
docker compose -f infra/docker-compose.yml --profile proxy logs --tail=200 api
docker compose -f infra/docker-compose.yml --profile proxy logs --tail=200 web
docker compose -f infra/docker-compose.yml --profile proxy logs --tail=200 postgres
docker compose -f infra/docker-compose.yml --profile proxy logs --tail=200 caddy
```

Follow logs while reproducing an issue:

```bash
docker compose -f infra/docker-compose.yml --profile proxy logs -f api
docker compose -f infra/docker-compose.yml --profile proxy logs -f web
```

Expected healthy signals after restart or deploy:

- `postgres` is `healthy` in `docker compose -f infra/docker-compose.yml --profile proxy ps`.
- `api`, `web`, and `caddy` are running or restarting only briefly.
- `/api/health` returns successfully through the public domain.
- The web route returns an HTTP success or redirect response through Caddy.
- Admin login page loads over HTTPS.
- No service repeatedly exits.

## Failure Triage

API does not start:

- Check `docker compose -f infra/docker-compose.yml --profile proxy logs --tail=200 api`.
- Look for unsafe production configuration errors first.
- Confirm `.env` exists on the VPS and does not use local placeholder secrets.
- Confirm `DATABASE_URL` matches `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`.
- Confirm migrations were run after pulling new code.

Web does not load:

- Check `docker compose -f infra/docker-compose.yml --profile proxy logs --tail=200 web`.
- Confirm `NEXT_PUBLIC_API_BASE_URL` uses `/api` for same-origin Caddy routing, or points to `https://<APP_DOMAIN>/api` for an explicit public API URL.
- Confirm the web container is running in `docker compose -f infra/docker-compose.yml --profile proxy ps`.
- Check Caddy logs if the web container is healthy but the public domain fails.

Database is unhealthy:

- Check `docker compose -f infra/docker-compose.yml --profile proxy logs --tail=200 postgres`.
- Confirm the PostgreSQL volume exists and disk space is available.
- Confirm `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` are consistent with `.env`.
- Do not remove volumes while troubleshooting unless a verified restore path is ready.

Caddy or HTTPS fails:

- Check `docker compose -f infra/docker-compose.yml --profile proxy logs --tail=200 caddy`.
- Confirm `APP_DOMAIN` is a real domain and DNS points to the VPS public IP.
- Confirm ports `80` and `443` are open to the internet.
- Confirm `infra/caddy/Caddyfile` routes `/api/*` to `api:8000` and all other traffic to `web:3000`.

Login fails:

- Confirm API health succeeds first.
- Confirm the browser is using HTTPS when `AUTH_COOKIE_SECURE=true`.
- Confirm `ADMIN_EMAIL` is the configured admin email.
- Check API logs for authentication errors, but do not paste credentials or cookies into support channels.

CSV import or analysis fails after deploy:

- Confirm API health and database health first.
- Check API logs around the failed request.
- Confirm the uploaded CSV uses the selected timeframe and is below upload limits.
- Treat signal output as decision-support only; failed analysis should not trigger any trading action.

## Deployment Smoke Test Checklist

Run this checklist after first deployment, restart, restore, or a production-like configuration change. Use sample or paper-trading data only. Do not place real orders, connect a broker, or treat signals as buy/sell instructions.

| Step | Check | Expected Result | If It Fails |
| --- | --- | --- | --- |
| 1 | `docker compose -f infra/docker-compose.yml --profile proxy ps` | `postgres` is healthy and `api`, `web`, `caddy` are running. | Inspect service logs before retrying. |
| 2 | `curl -fsS https://<APP_DOMAIN>/api/health` | API health returns successfully. | Check API, Caddy, DNS, and database health. |
| 3 | Open `https://<APP_DOMAIN>` | Web app loads over HTTPS. | Check web and Caddy logs. |
| 4 | Log in with configured admin credentials. | Login succeeds and a secure session cookie is set. | Confirm `ADMIN_EMAIL`, password, API health, HTTPS, and `AUTH_COOKIE_SECURE`. |
| 5 | Open the watchlist page. | Existing watchlist items load, or the empty state is shown. | Check API logs and authenticated API requests. |
| 6 | Create or verify a sample watchlist item. | Sample stock or crypto symbol is visible. | Confirm watchlist API access and database state. |
| 7 | Open CSV import page. | Import form loads with symbol and timeframe controls. | Check web logs and authenticated API calls. |
| 8 | Upload a small sample CSV for a selected timeframe. | Import succeeds or returns a clear validation error. | Review structured CSV errors; do not bypass validation. |
| 9 | Run analysis for the imported sample data. | Analysis completes or returns a conservative `No Setup`/data-quality result. | Check API logs and confirm required timeframe data exists. |
| 10 | Open signals list/detail. | Signal card is visible with reasoning, risk flags, No-Trade reasons, and next action where applicable. | Confirm analysis persisted a signal and user owns the data. |
| 11 | Create a sample manual trade record only if using paper/sample data. | Trade is logged as documentation of an external manual action. | Check risk settings, trade validation errors, and API logs. |
| 12 | Open trade detail and add a sample note/event if appropriate. | Manual event or note is saved. | Check trade ownership and trade API logs. |
| 13 | Log out. | Session ends and protected routes require login again. | Check auth API logs and cookie behavior. |

Pass criteria:

- Health, login, watchlist, import page, signal visibility, and logout checks pass.
- CSV import and analysis either succeed with sample data or fail with clear conservative validation/data-quality messages.
- Any manual trade check uses paper/sample data only.
- No step implies automatic execution, broker integration, profitability, or trading advice.

Fail criteria:

- Health endpoint fails through the public domain.
- Login cannot complete over HTTPS.
- Protected pages expose data without login.
- Database-backed pages fail broadly after API health passes.
- Logs show repeated service restarts or unsafe production configuration errors.

Record smoke-test findings outside committed secrets. If logs are needed for a follow-up issue, redact cookies, tokens, database URLs, email addresses, journal text, and trade details before sharing.

## PostgreSQL Backups

The MVP database stores watchlist items, imported candles, indicator snapshots, signals, trades, journal entries, settings, and auth data. Treat backups as sensitive data.

Backup files must not be committed to the repository or attached to issues/PRs. Store them outside the repo working tree, for example under `/var/backups/cilly-trading-signal/postgres` with restrictive permissions.

Create a backup with the helper script:

```bash
BACKUP_DIR=/var/backups/cilly-trading-signal/postgres ./scripts/backup_postgres.sh
```

Set `BACKUP_DIR` explicitly for staging, VPS, production-like, or real-data backups. If `BACKUP_DIR` is not set, the helper uses a repository-external default next to the checkout:

```text
../cilly-postgres-backups/postgres
```

The helper refuses to write a backup inside the repository working tree unless `ALLOW_REPO_BACKUP_DIR=true` is set. Use that override only for clearly disposable local tests, and delete the test dump after verification.

The script creates a PostgreSQL custom-format dump using the running `postgres` Compose service. It reads these optional environment variables:

- `COMPOSE_FILE`, default `infra/docker-compose.yml`.
- `BACKUP_DIR`, default `../cilly-postgres-backups/postgres` resolved outside the repository checkout.
- `ALLOW_REPO_BACKUP_DIR`, default unset. Set to `true` only for disposable local tests that intentionally write inside the repository working tree.
- `POSTGRES_DB`, default `cilly_trading_signal`.
- `POSTGRES_USER`, default `postgres`.

Minimum retention guidance:

- Keep at least one known-good backup before each deployment.
- Keep several recent daily backups while operating the MVP.
- Move important backups off the VPS or to encrypted storage when handling real user data.
- Periodically delete old backups intentionally; do not let disk usage grow without review.

Storage risks:

- PostgreSQL dumps can contain trade notes, journal text, auth data, and market data.
- Anyone with a backup may be able to inspect or restore sensitive app data.
- Do not store backups in public buckets, synced folders, screenshots, or support tickets.
- Keep local disposable backup tests separate from staging, VPS, production-like, and real-data backups.

## PostgreSQL Restore

Restore only after confirming the target database can be replaced and the selected backup file is the intended source. A restore should be tested on a non-production copy before relying on it operationally.

Restore with the helper script:

```bash
./scripts/restore_postgres.sh /var/backups/cilly-trading-signal/postgres/cilly_trading_signal_YYYYMMDDTHHMMSSZ.dump
```

The restore script:

- Stops the `api` and `web` services before replacing the database.
- Copies the selected dump into the running `postgres` container.
- Drops and recreates the configured database.
- Runs `pg_restore` into the new database.
- Removes the temporary dump from the container.
- Starts the `api` and `web` services again.

Verify a restore:

```bash
curl -fsS https://trading.example.com/api/health
```

Then log in and check a small sample of user-owned data:

- Watchlist item exists.
- Recent import history or signals are present.
- Trades and journal entries expected in the backup are visible.

Safe local verification path:

1. Start a local Docker Compose stack with a disposable `.env`.
2. Restore a consciously selected dump from outside the repository working tree into that local stack.
3. Run the API health check.
4. Log in and confirm sample data exists.
5. Stop the local stack and remove disposable volumes only after confirming the test is complete.

## Basic Rollback

Rollback assumes the previous commit is still available and the database schema is compatible with the previous app version.

1. Identify the previous known-good commit.

```bash
git log --oneline -10
```

2. Switch to that commit or branch.

```bash
git switch --detach <commit-sha>
```

3. Rebuild and restart.

```bash
docker compose -f infra/docker-compose.yml --profile proxy up --build -d
```

4. Check health and core manual workflow.

```bash
curl -fsS https://trading.example.com/api/health
```

If a migration has already changed the database, do not assume code rollback is enough. Confirm whether a database restore is required before continuing.

## Post-Deploy Checks

Minimum checks after first deploy or update:

- `docker compose -f infra/docker-compose.yml --profile proxy ps` shows expected services running.
- `https://<APP_DOMAIN>/api/health` returns a healthy response.
- Web app loads over HTTPS.
- Admin login succeeds.
- Watchlist page loads.
- CSV import page loads.
- No secrets appear in logs or screenshots.
- UI wording still frames signals as manual decision-support only.

## Known Gaps

- Automated deployment smoke tests are not implemented; the checklist above is manual.

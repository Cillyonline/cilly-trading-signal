# Deployment Runbook

## Purpose

This runbook describes a repeatable VPS deployment path for the single-user MVP using Docker Compose, PostgreSQL, and Caddy.

It is an operational guide, not a production-readiness guarantee. Before real operation, backups, monitoring, restore tests, secret rotation, and a security review still need to be completed.

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
- `NEXT_PUBLIC_API_BASE_URL`: public API base URL, normally `https://<APP_DOMAIN>/api`.

Optional values for later alert work:

- `TRADINGVIEW_WEBHOOK_SECRET`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Do not commit `.env` or paste secrets into issues, PRs, logs, or screenshots.

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

## PostgreSQL Backups

The MVP database stores watchlist items, imported candles, indicator snapshots, signals, trades, journal entries, settings, and auth data. Treat backups as sensitive data.

Backup files must not be committed to the repository or attached to issues/PRs. Store them outside the repo working tree when possible, for example under `/var/backups/cilly-trading-signal/postgres` with restrictive permissions.

Create a backup with the helper script:

```bash
BACKUP_DIR=/var/backups/cilly-trading-signal/postgres ./scripts/backup_postgres.sh
```

The script creates a PostgreSQL custom-format dump using the running `postgres` Compose service. It reads these optional environment variables:

- `COMPOSE_FILE`, default `infra/docker-compose.yml`.
- `BACKUP_DIR`, default `backups/postgres`.
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

## PostgreSQL Restore

Restore only after confirming the target database can be replaced. A restore should be tested on a non-production copy before relying on it operationally.

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
2. Restore the dump into that local stack.
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

- Production secret and environment hardening docs are tracked separately in `#79`.
- Operational healthcheck and logging guidance is tracked separately in `#80`.
- Deployment smoke test checklist is tracked separately in `#81`.

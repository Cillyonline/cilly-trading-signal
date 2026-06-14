# Deployment Runbook

## Purpose

This runbook describes a repeatable VPS deployment path for the single-user MVP using Docker Compose, PostgreSQL, and Caddy.

It is an operational guide, not a production-readiness guarantee. Before real operation, backups, monitoring, restore tests, secret rotation, and a security review still need to be completed.

For the private VPS staging plan based on the current server inventory, see `docs/VPS_STAGING_PLAN.md`. The staging plan must be reviewed before changing the existing VPS because other projects already run on that server. For the sanitized staging environment checklist, see `docs/VPS_ENVIRONMENT_CHECKLIST.md`. For the private VPS smoke-test procedure and evidence template, see `docs/VPS_STAGING_SMOKE_TEST.md`. For the minimal host firewall plan and rollback procedure, see `docs/VPS_FIREWALL_HARDENING_PLAN.md`. For the non-root deploy-user procedure, see `docs/VPS_DEPLOY_USER_RUNBOOK.md`. For local, staging, and production-like monitoring expectations, see `docs/APPLICATION_MONITORING_CHECKLIST.md`. For incident response covering import, provider sync, migration, Telegram, database, and stale-data incidents, see `docs/OPERATIONAL_INCIDENT_RUNBOOK.md`.
For v1.3 alert-routing smoke-test evidence and the remaining operator-run Telegram provider check, see `docs/V1_3_ALERT_ROUTING_SMOKE_TEST.md`.

## Safety Boundaries

- The app is decision-support only.
- Signals and alerts are review prompts, not buy or sell instructions.
- The app does not place orders and has no broker integration.
- Use sample or paper-trading data when validating a fresh deployment.

## Prerequisites

VPS:

- Linux VPS with a supported Docker installation.
- SSH access with the non-root deploy user from `docs/VPS_DEPLOY_USER_RUNBOOK.md` where possible.
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

## VPS Deploy User

Routine private VPS staging operations should use the app-specific non-root deploy
user documented in `docs/VPS_DEPLOY_USER_RUNBOOK.md`.

Target routine checkout path:

```text
/srv/apps/cilly-trading-signal
```

Use root only for one-time host setup, firewall changes, emergency recovery, or
repairs that cannot be performed by the deploy user. Root emergency access must be
preserved.

The deploy user can run Docker Compose through the `docker` group. This is practical
for single-operator private staging, but Docker group membership is root-equivalent
host access and must not be treated as strong multi-user isolation.

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
- `TELEGRAM_ALERT_ROUTING_ENABLED`: keep `false` unless automatic Telegram alert routing has been deliberately enabled for the environment.

Automatic Telegram alert routing fails closed. If `TELEGRAM_ALERT_ROUTING_ENABLED=true`, the API requires non-empty, non-placeholder `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` values at startup. Do not infer production readiness from a successful Telegram test message.

Automatic Telegram delivery is deduplicated by `symbol + alert_type + timeframe` for 30 minutes and rate-limited to 10 Telegram deliveries per user within 5 minutes. Deduped or rate-limited webhook events remain stored for manual review and are marked skipped rather than silently deleted.

Optional values for manual market data provider sync:

- `MARKET_DATA_PROVIDER_SYNC_ENABLED`: keep `false` unless provider sync has been deliberately enabled for the environment.
- `MARKET_DATA_PROVIDER`: provider identifier. Implemented paths include
  `alpha_vantage` and `twelve_data`.
- `MARKET_DATA_API_KEY`: provider API key. Store only in the environment file or
  secret store, never in git, issues, PRs, logs, screenshots, or chat.

Market data provider sync is manual and fails closed. If `MARKET_DATA_PROVIDER_SYNC_ENABLED=false`, manual sync requests return a safe skipped state. If `MARKET_DATA_PROVIDER_SYNC_ENABLED=true`, the API requires a supported `MARKET_DATA_PROVIDER` and a non-empty, non-placeholder `MARKET_DATA_API_KEY` at startup. Twelve Data is the clean provider path for guarded manual `1W`, `1D`, and `4H` stored-data sync. These settings do not enable scheduling, automatic analysis, broker execution, live/realtime signals, or production readiness.

Do not commit `.env` or paste secrets into issues, PRs, logs, or screenshots.

### Provider Secret And VPS Operation Checklist

Provider keys are operational secrets. Adding, rotating, testing, or removing a
provider key on a VPS is a server operation and must not be performed by an agent
or script without explicit owner/operator approval for that specific environment.

Before enabling provider sync on a VPS:

- Confirm the target environment, branch or commit, and Compose project name.
- Confirm the provider identifier and timeframe scope. The clean Twelve Data path
  targets guarded manual `1W`, `1D`, and `4H` stored-data sync.
- Confirm that TradingView CSV remains the fallback if the provider plan, entitlement,
  symbol mapping, or rate limit blocks a symbol/timeframe.
- Confirm that the operator owns the provider account/key and accepts the provider
  terms, rate limits, and storage/licensing assumptions.
- Confirm the rollback plan: set `MARKET_DATA_PROVIDER_SYNC_ENABLED=false`, restart
  the API/stack, and verify `/api/health` plus a skipped manual sync response.
- Confirm evidence rules: record only status enums, sanitized error codes, timeframe,
  environment class, and commit SHA; never record the key, request URL, raw payload,
  account/subscription details, cookies, database URLs, or private symbols.

When changing provider settings on a VPS:

- Edit only the VPS-local `.env` or approved secret store; do not change `.env.example`
  with real values.
- Do not print `.env`, shell history, or provider request URLs into terminal captures
  that may be pasted into chat, issues, PRs, screenshots, or docs.
- Restart only after explicit approval because restarts may interrupt the cockpit.
- After restart, verify API health and the disabled, failure, or success path using
  `docs/PROVIDER_SYNC_SMOKE_TEST.md` with sample-only evidence.
- If the API fails startup after a provider change, roll back by disabling provider
  sync or restoring the previous secret value, then restart and record sanitized
  status only.

Provider-key handling does not approve live/realtime data, automatic refresh,
automatic signal generation, alerts, broker integration, order execution, public
production readiness, strategy validation, or profitability claims.

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
ssh cillydeploy@your-vps
```

2. Install Docker and the Docker Compose plugin using the operating system's documented package source.

3. Clone the repository.

```bash
cd /srv/apps
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
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy up --build -d
```

8. Check container state.

```bash
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy ps
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

## VPS Host Firewall

The private VPS staging firewall posture is documented in `docs/VPS_FIREWALL_HARDENING_PLAN.md`.

Before applying firewall rules on the VPS:

- Keep an active SSH session and open a second SSH session for verification.
- Preserve SSH, public Caddy ports `80` and `443`, Docker networking, and the existing unrelated `staging` Compose project.
- Keep direct app ports `3000` and `8000` localhost-only.
- Keep existing localhost-bound `18000` private to the host.
- Use the documented rollback timer and record only sanitized evidence.

Firewall changes are operator-run server changes. Do not claim they are applied until sanitized VPS evidence has been recorded.

## Updates And Migrations

Before production-like reconsideration or any target with private-data risk, use
`docs/ROLLBACK_MIGRATION_SAFETY_CHECKLIST.md` to record migration, rollback,
backup, restore, and stop-condition decisions. The checklist is guidance only and
does not approve service-impacting action without operator approval.

1. Connect to the VPS and enter the repository.

```bash
ssh cillydeploy@your-vps
cd /srv/apps/cilly-trading-signal
```

2. Fetch and update the deployment branch.

```bash
git fetch origin
git switch main
git pull --ff-only origin main
```

3. Rebuild and restart services.

```bash
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy up --build -d
```

4. Run database migrations from the API container.

```bash
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml exec api uv run --with alembic --with pydantic-settings --with sqlalchemy --with "psycopg[binary]" alembic upgrade head
```

5. Re-check health and login.

```bash
curl -fsS https://trading.example.com/api/health
```

## Restart And Stop

Restart all services:

```bash
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy restart
```

Stop services without deleting volumes:

```bash
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy down
```

Do not run `down --volumes` on a VPS unless you intentionally want to remove PostgreSQL data and have a verified backup.

## Minimum VPS Monitoring Checks

These checks define the minimum manual monitoring baseline for private VPS staging. They are not a full observability stack and do not create a production-readiness claim.

For the environment-level monitoring checklist covering local, private staging, and production-like operation, use `docs/APPLICATION_MONITORING_CHECKLIST.md` before relying more heavily on the app.

Run commands from `/srv/apps/cilly-trading-signal` unless stated otherwise. Do not paste output that contains secrets, cookies, `.env` values, database URLs, private trading data, or backup contents into issues, PRs, docs, screenshots, or chat.

### Automated VPS Health Check

Use `scripts/vps_health_check.sh` for a minimal automated private staging check. The
script emits sanitized `PASS` / `FAIL` lines only and does not read `.env` contents,
container logs, database rows, cookies, tokens, or private trading data.

It checks:

- API health through `https://<app-domain>/api/health`.
- HTTPS web route through `https://<app-domain>/`.
- Expected Compose services are running: `postgres`, `api`, `web`, and `caddy`.
- Root filesystem usage is below the configured threshold.
- A recent PostgreSQL dump exists in the configured backup directory.

Run manually as `cillydeploy`:

```bash
cd /srv/apps/cilly-trading-signal
APP_DOMAIN=trading.cillyonline.de \
COMPOSE_ENV_FILE=.env \
COMPOSE_PROJECT_NAME=cilly-trading-signal \
BACKUP_DIR=/srv/backups/cilly-trading-signal/postgres \
bash ./scripts/vps_health_check.sh
```

Configuration:

- `APP_DOMAIN`, default `trading.cillyonline.de`.
- `COMPOSE_FILE`, default `infra/docker-compose.yml`.
- `COMPOSE_ENV_FILE`, default `.env`.
- `COMPOSE_PROJECT_NAME`, default `cilly-trading-signal`.
- `BACKUP_DIR`, default `/srv/backups/cilly-trading-signal/postgres`.
- `BACKUP_MAX_AGE_HOURS`, default `30`.
- `DISK_PATH`, default `/`.
- `DISK_MAX_USED_PERCENT`, default `85`.

Expected successful output shape:

```text
PASS api_health
PASS https_route
PASS compose_postgres_running
PASS compose_api_running
PASS compose_web_running
PASS compose_caddy_running
PASS disk_usage_percent=<number>
PASS backup_freshness_hours=<number>
SUMMARY failed_checks=0
```

Create `/etc/systemd/system/cilly-vps-health-check.service`:

```ini
[Unit]
Description=Cilly Trading Signal private VPS health check
Wants=docker.service
After=docker.service network-online.target

[Service]
Type=oneshot
User=cillydeploy
Group=cillydeploy
WorkingDirectory=/srv/apps/cilly-trading-signal
Environment=APP_DOMAIN=trading.cillyonline.de
Environment=COMPOSE_ENV_FILE=.env
Environment=COMPOSE_PROJECT_NAME=cilly-trading-signal
Environment=BACKUP_DIR=/srv/backups/cilly-trading-signal/postgres
Environment=BACKUP_MAX_AGE_HOURS=30
Environment=DISK_MAX_USED_PERCENT=85
ExecStart=/usr/bin/env bash scripts/vps_health_check.sh
```

Create `/etc/systemd/system/cilly-vps-health-check.timer`:

```ini
[Unit]
Description=Run Cilly Trading Signal private VPS health check

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min
Persistent=true
RandomizedDelaySec=2min

[Install]
WantedBy=timers.target
```

Enable and run once:

```bash
systemctl daemon-reload
systemctl enable --now cilly-vps-health-check.timer
systemctl start cilly-vps-health-check.service
systemctl status cilly-vps-health-check.service --no-pager
systemctl list-timers cilly-vps-health-check.timer
```

Review recent sanitized output:

```bash
journalctl -u cilly-vps-health-check.service -n 80 --no-pager
```

If the service fails:

1. Do not paste raw logs until they have been reviewed for secrets or private data.
2. Run the manual checks below to isolate API, HTTPS, Compose, disk, or backup freshness.
3. Confirm the unrelated `staging` Compose project remains running and separate.
4. Fix only the failing boundary for this app; do not restart unrelated services.
5. Record sanitized evidence with PASS/FAIL status and the follow-up issue if needed.

This timer is a private staging safety net, not a paging system, SLA, SLO, public
status page, production observability platform, trading alert, or trading advice.

Browser route checks remain manual unless a future opt-in dry-run script is
implemented under the contract in
`docs/POST_DEPLOY_BROWSER_SMOKE_AUTOMATION_EVALUATION.md#safe-dry-run-browser-smoke-contract`.
That contract forbids credential capture, cookies/tokens, private data,
screenshots with sensitive data, VPS remediation, and service-impacting actions.

### Check Frequency

- After every deployment or restart: run all checks.
- Daily during active staging use: health, containers, disk, and backup freshness.
- Before and after any backup/restore test: containers, PostgreSQL, disk, and app health.
- After DNS, firewall, or Caddy changes: HTTPS and public API health.

### API Health

```bash
curl -fsS https://<app-domain>/api/health
```

Success:

- Returns a healthy JSON response.
- Completes without TLS, DNS, or connection errors.

Investigate if:

- The command fails or times out.
- TLS certificate errors appear.
- DNS resolves to the wrong server.
- The response is not the expected health payload.

### Docker Containers

```bash
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy ps
```

Success:

- `postgres`, `api`, `web`, and `caddy` are running.
- PostgreSQL reports healthy if the health status is shown.
- Containers are not restarting repeatedly.

Investigate if:

- Any app container is exited, unhealthy, or restarting.
- The existing unrelated `staging` Compose project changed state unexpectedly.

### Container Logs

Use logs only for short troubleshooting windows and review output for sensitive data before sharing.

```bash
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy logs --tail=100 api
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy logs --tail=100 web
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy logs --tail=100 caddy
```

Investigate if:

- Config guard failures appear.
- Authentication, database, Caddy, DNS, or certificate errors repeat.
- Logs contain unexpected stack traces.

### PostgreSQL Health

```bash
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml exec postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Success:

- PostgreSQL accepts connections for the configured database.

Investigate if:

- `pg_isready` reports no response or rejects connections.
- The API is healthy but database-dependent pages fail.
- Disk usage is high.

### HTTPS / Caddy Route

```bash
curl -fsSI https://<app-domain>/
curl -fsS https://<app-domain>/api/health
```

Success:

- HTTPS responds through Caddy.
- `/api/health` routes to the API.
- No direct public API or web service ports are required.

Investigate if:

- `80` or `443` are not reachable after DNS propagation.
- Caddy cannot obtain or renew certificates.
- Browser calls bypass `/api` same-origin routing.

### Disk Space

```bash
df -h /
docker system df
```

Success:

- Root filesystem has enough free space for Docker images, PostgreSQL data, logs, and backups.
- Docker usage is expected for the current deployment.

Investigate if:

- Root filesystem usage exceeds 80%.
- Docker image, container, or build cache usage grows unexpectedly.
- Backup files are stored inside the repository checkout.

Do not run cleanup commands such as `docker system prune`, `docker volume prune`, or broad `rm` commands without a separate approved operations plan.

### Memory And Load

```bash
free -h
uptime
```

Success:

- Available memory remains sufficient for the app and existing projects.
- Load average is reasonable for the VPS size.

Investigate if:

- Memory pressure is persistent.
- The app is killed or restarts unexpectedly.
- Load is elevated during normal usage.

### Backup Freshness

```bash
systemctl list-timers cilly-postgres-backup.timer
systemctl status cilly-postgres-backup.service --no-pager
find /srv/backups/cilly-trading-signal/postgres -maxdepth 1 -type f -name 'cilly_trading_signal_*.dump' -printf '%TY-%Tm-%Td %TH:%TM %s %f\n' | sort
```

Success:

- The `cilly-postgres-backup.timer` exists and has a next run time.
- The latest service run succeeded or any failure is understood and tracked.
- Recent expected non-zero backup artifacts exist after backup automation or manual backup is approved.
- Backup files are outside the repository checkout.

Investigate if:

- The timer is missing, disabled, or has no next run time.
- The service failed.
- No recent backup exists after backup procedures are enabled.
- Backups are stored under the repository checkout, such as `/srv/apps/cilly-trading-signal` or the earlier root-owned checkout path.
- Backup file sizes are unexpectedly zero or much smaller than expected.

### Restart Behavior

Restart only this app's Compose project when needed:

```bash
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy restart
```

Stop only this app's Compose project when rollback is needed:

```bash
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy down
```

Do not restart or stop the existing unrelated `staging` Compose project as part of this app's monitoring or rollback workflow.

### Investigation Checklist

If a check fails:

1. Confirm the failing command targets `cilly-trading-signal`, not another project.
2. Check container status.
3. Check short logs for the failing service.
4. Check disk space and PostgreSQL health.
5. If public access fails, check Caddy logs, DNS, and HTTPS route.
6. If rollback is needed, stop only the `cilly-trading-signal` Compose project.
7. Document sanitized evidence and do not include secrets or private data.

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
docker compose --env-file .env -f infra/docker-compose.yml --profile proxy ps
docker compose --env-file .env -f infra/docker-compose.yml --profile proxy down --volumes
```

For production-like VPS maintenance, prefer stopping without deleting volumes:

```bash
docker compose --env-file .env -f infra/docker-compose.yml --profile proxy down
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
docker compose --env-file .env -f infra/docker-compose.yml --profile proxy up --build -d
docker compose --env-file .env -f infra/docker-compose.yml --profile proxy ps
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
docker compose --env-file .env -f infra/docker-compose.yml --profile proxy ps
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
docker compose --env-file .env -f infra/docker-compose.yml exec postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Recent logs:

```bash
docker compose --env-file .env -f infra/docker-compose.yml --profile proxy logs --tail=200 api
docker compose --env-file .env -f infra/docker-compose.yml --profile proxy logs --tail=200 web
docker compose --env-file .env -f infra/docker-compose.yml --profile proxy logs --tail=200 postgres
docker compose --env-file .env -f infra/docker-compose.yml --profile proxy logs --tail=200 caddy
```

Follow logs while reproducing an issue:

```bash
docker compose --env-file .env -f infra/docker-compose.yml --profile proxy logs -f api
docker compose --env-file .env -f infra/docker-compose.yml --profile proxy logs -f web
```

Expected healthy signals after restart or deploy:

- `postgres` is `healthy` in `docker compose --env-file .env -f infra/docker-compose.yml --profile proxy ps`.
- `api`, `web`, and `caddy` are running or restarting only briefly.
- `/api/health` returns successfully through the public domain.
- The web route returns an HTTP success or redirect response through Caddy.
- Admin login page loads over HTTPS.
- No service repeatedly exits.

## Failure Triage

API does not start:

- Check `docker compose --env-file .env -f infra/docker-compose.yml --profile proxy logs --tail=200 api`.
- Look for unsafe production configuration errors first.
- Confirm `.env` exists on the VPS and does not use local placeholder secrets.
- Confirm `DATABASE_URL` matches `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`.
- Confirm migrations were run after pulling new code.

Web does not load:

- Check `docker compose --env-file .env -f infra/docker-compose.yml --profile proxy logs --tail=200 web`.
- Confirm `NEXT_PUBLIC_API_BASE_URL` uses `/api` for same-origin Caddy routing, or points to `https://<APP_DOMAIN>/api` for an explicit public API URL.
- Confirm the web container is running in `docker compose --env-file .env -f infra/docker-compose.yml --profile proxy ps`.
- Check Caddy logs if the web container is healthy but the public domain fails.

Database is unhealthy:

- Check `docker compose --env-file .env -f infra/docker-compose.yml --profile proxy logs --tail=200 postgres`.
- Confirm the PostgreSQL volume exists and disk space is available.
- Confirm `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` are consistent with `.env`.
- Do not remove volumes while troubleshooting unless a verified restore path is ready.

Caddy or HTTPS fails:

- Check `docker compose --env-file .env -f infra/docker-compose.yml --profile proxy logs --tail=200 caddy`.
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
| 1 | `docker compose --env-file .env -f infra/docker-compose.yml --profile proxy ps` | `postgres` is healthy and `api`, `web`, `caddy` are running. | Inspect service logs before retrying. |
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

Backup files must not be committed to the repository or attached to issues/PRs. Store them outside the repo working tree. The private VPS staging path is:

```text
/srv/backups/cilly-trading-signal/postgres
```

Create a backup with the helper script:

```bash
BACKUP_DIR=/srv/backups/cilly-trading-signal/postgres \
COMPOSE_ENV_FILE=.env \
RETENTION_DAYS=14 \
RETENTION_MIN_KEEP=7 \
./scripts/backup_postgres.sh
```

Set `BACKUP_DIR` explicitly for staging, VPS, production-like, or real-data backups. If `BACKUP_DIR` is not set, the helper uses a repository-external default next to the checkout:

```text
../cilly-postgres-backups/postgres
```

The helper refuses to write a backup inside the repository working tree unless `ALLOW_REPO_BACKUP_DIR=true` is set. Use that override only for clearly disposable local tests, and delete the test dump after verification.

The script creates a PostgreSQL custom-format dump using the running `postgres` Compose service. It reads these optional environment variables:

- `COMPOSE_FILE`, default `infra/docker-compose.yml`.
- `COMPOSE_PROJECT_NAME`, optional Docker Compose variable. Set to `cilly-trading-signal` for private VPS staging.
- `COMPOSE_ENV_FILE`, default unset. Set to `.env` for private VPS staging so Compose uses the intended server-local environment file.
- `BACKUP_DIR`, default `../cilly-postgres-backups/postgres` resolved outside the repository checkout.
- `ALLOW_REPO_BACKUP_DIR`, default unset. Set to `true` only for disposable local tests that intentionally write inside the repository working tree.
- `POSTGRES_DB`, default `cilly_trading_signal`.
- `POSTGRES_USER`, default `postgres`.
- `RETENTION_DAYS`, default unset. When set, old matching dump files are removed after a successful backup.
- `RETENTION_MIN_KEEP`, default `7`. Retention never deletes below this number of matching dump files.

Private VPS staging retention policy:

- Keep at least one known-good backup before each deployment.
- Run one automated backup per day.
- Keep backups for 14 days.
- Always keep at least seven matching dumps, even if older than 14 days.
- Move important backups off the VPS or to encrypted storage when handling real user data.
- Periodically delete old backups intentionally; do not let disk usage grow without review.

Private-data or production-like reliance additionally requires offsite encrypted
backup storage and a restore drill from that offsite path. Local VPS dumps alone
are acceptable only for controlled private staging with sample or paper data.

Storage risks:

- PostgreSQL dumps can contain trade notes, journal text, auth data, and market data.
- Anyone with a backup may be able to inspect or restore sensitive app data.
- Do not store backups in public buckets, synced folders, screenshots, or support tickets.
- Keep local disposable backup tests separate from staging, VPS, production-like, and real-data backups.

### Private VPS Backup Automation

Use a systemd timer on the VPS to run daily backups as the non-root deploy user from
`docs/VPS_DEPLOY_USER_RUNBOOK.md`. This avoids storing a long shell command in a user
crontab and keeps logs visible through `journalctl`.

Create the backup directory as root:

```bash
install -d -o cillydeploy -g cillydeploy -m 750 /srv/backups/cilly-trading-signal/postgres
```

Create `/etc/systemd/system/cilly-postgres-backup.service`:

```ini
[Unit]
Description=Cilly Trading Signal PostgreSQL backup
Wants=docker.service
After=docker.service

[Service]
Type=oneshot
User=cillydeploy
Group=cillydeploy
WorkingDirectory=/srv/apps/cilly-trading-signal
Environment=BACKUP_DIR=/srv/backups/cilly-trading-signal/postgres
Environment=COMPOSE_PROJECT_NAME=cilly-trading-signal
Environment=COMPOSE_ENV_FILE=.env
Environment=RETENTION_DAYS=14
Environment=RETENTION_MIN_KEEP=7
ExecStart=/usr/bin/env bash ./scripts/backup_postgres.sh
```

Create `/etc/systemd/system/cilly-postgres-backup.timer`:

```ini
[Unit]
Description=Run Cilly Trading Signal PostgreSQL backup daily

[Timer]
OnCalendar=*-*-* 03:15:00
Persistent=true
RandomizedDelaySec=15m

[Install]
WantedBy=timers.target
```

Enable and start the timer:

```bash
systemctl daemon-reload
systemctl enable --now cilly-postgres-backup.timer
systemctl list-timers cilly-postgres-backup.timer
```

Trigger one backup manually after enabling the unit:

```bash
systemctl start cilly-postgres-backup.service
systemctl status cilly-postgres-backup.service --no-pager
```

Verify backup freshness without exposing dump contents:

```bash
find /srv/backups/cilly-trading-signal/postgres -maxdepth 1 -type f -name 'cilly_trading_signal_*.dump' -printf '%TY-%Tm-%Td %TH:%TM %s %f\n' | sort
curl -fsS https://trading.cillyonline.de/api/health
```

Expected:

- A non-zero `.dump` file exists under `/srv/backups/cilly-trading-signal/postgres`.
- No dump files exist inside `/srv/apps/cilly-trading-signal`.
- API health still passes after the backup.
- The unrelated `staging` Compose project remains separate and running.

Record only sanitized evidence: date/time, service/timer status PASS/FAIL, backup
directory path, non-zero artifact PASS/FAIL, API health PASS/FAIL, and whether a
restore test was performed or intentionally deferred.

### Offsite Encrypted Backups

Use offsite encrypted backups before private trading data, stronger operational
reliance, or production-like exposure is introduced. This procedure defines the
expected operating model; it is not a production-readiness statement, SLA,
security certification, or approval to handle private data without a separate
gate.

For the offsite backup and restore acceptance checklist, see
`docs/OFFSITE_BACKUP_RESTORE_ACCEPTANCE_CHECKLIST.md`. That checklist defines
required evidence and operator-required actions; it does not execute or approve
backup, restore, private-data, or production-like reliance by itself.

For the v5.8 offsite encrypted backup configuration status, see
`docs/reviews/v5-8-offsite-encrypted-backups.md`.

Recommended default:

- Use `restic` for client-side encrypted backups.
- Store the repository on an operator-controlled offsite target such as SFTP,
  S3-compatible object storage, or another provider-approved private backup
  target.
- Use `docs/OFFSITE_BACKUP_TARGET_EVALUATION.md` to choose the target category
  and record tradeoffs before relying on it for private-data or production-like
  decisions.
- Keep the existing local VPS dump path as the source:
  `/srv/backups/cilly-trading-signal/postgres`.
- Store restic repository credentials and `RESTIC_PASSWORD` only in a root-only
  or deploy-user-only environment file outside the repository, such as
  `/etc/cilly-trading-signal/offsite-backup.env` with mode `600`.
- Store the restic password or recovery key in the operator password manager.
  Do not store it only on the VPS.
- Do not paste repository URLs containing credentials, access keys, secret keys,
  `RESTIC_PASSWORD`, dump filenames with sensitive context, or restored data
  contents into issues, PRs, docs, screenshots, or chat.

Example root-only environment file shape:

```ini
RESTIC_REPOSITORY=sftp:backup-user@backup-host:/private/cilly-trading-signal/restic
RESTIC_PASSWORD=<stored-in-password-manager>
RESTIC_COMPRESSION=auto
```

For S3-compatible storage, use provider-specific environment variables in the
same root-only file and keep the repository private. Do not commit or paste the
file.

The v3.6 selected first target category is private S3-compatible object storage.
This selects the target class only; it does not configure a provider, create
credentials, initialize Restic, run a backup, or prove restore readiness. Use
`docs/OFFSITE_BACKUP_TARGET_EVALUATION.md#v36-target-category-and-credential-path`
before any operator-run setup.

One-time setup after choosing the offsite target:

```bash
install -d -m 700 /etc/cilly-trading-signal
install -m 600 /dev/null /etc/cilly-trading-signal/offsite-backup.env
# Edit the file locally on the VPS. Do not paste its contents into evidence.
set -a
. /etc/cilly-trading-signal/offsite-backup.env
set +a
restic init
restic check
```

Create an encrypted offsite backup after the local PostgreSQL dump has run:

```bash
set -a
. /etc/cilly-trading-signal/offsite-backup.env
set +a
restic backup /srv/backups/cilly-trading-signal/postgres --tag cilly-postgres --tag private-staging
restic forget --tag cilly-postgres --keep-daily 14 --keep-weekly 8 --prune
restic snapshots --tag cilly-postgres
```

Routine repeat procedure for the current operator-controlled encrypted target:

1. Run the normal PostgreSQL dump first and confirm the latest dump is non-zero
   without printing its contents.
2. Load the restic environment from the private env file or operator password
   manager. Do not paste `RESTIC_PASSWORD`, repository credentials, or access
   keys into terminal evidence, issues, PRs, docs, screenshots, or chat.
3. Run `restic backup` against the PostgreSQL backup directory with the
   `cilly-postgres` and environment tags.
4. Run `restic snapshots --tag cilly-postgres` and record only sanitized
   evidence: timestamp, target category, snapshot count, and latest snapshot ID
   prefix if needed.
5. Run `restic check` and record pass/fail only.
6. Periodically restore the latest snapshot into a disposable directory and
   disposable database project, then verify only non-sensitive evidence such as
   non-zero dump size, Alembic version, row counts for sample data, and cleanup
   completion.

Minimum recurrence before private-data reliance is reconsidered:

- Encrypted restic backup: after each successful PostgreSQL dump, normally daily
  when the VPS backup timer is active.
- `restic check`: at least weekly, and after changing the repository target,
  password, credentials, timer, source path, or backup host.
- Restore drill from the encrypted restic repository: at least monthly, before
  any private-data approval decision, and after changing backup target class,
  retention policy, repository password, restore procedure, database major
  version, or deployment host.
- Evidence review: before any private-data readiness gate is changed from No Go.

Minimum retention expectation before private-data reliance is reconsidered:

- Keep at least 14 daily snapshots and 8 weekly snapshots for the PostgreSQL
  backup tag unless a later owner/operator decision records a stricter policy.
- Keep at least one recent restore-drill evidence record for the active backup
  target class.
- Do not delete the only known-good snapshot after a failed backup, failed
  `restic check`, failed restore drill, password rotation, or target migration
  until a new backup and restore drill pass.
- If local Windows encrypted restic is the only target, record it explicitly as
  local-only encrypted redundancy, not geographic or ransomware-resistant backup
  coverage.

Sanitized recurring evidence format:

```text
Date/time UTC:
Repository category: local Windows encrypted / offsite SFTP / offsite S3-compatible / other private target
Latest snapshot ID prefix: <prefix only>
Snapshot count for cilly-postgres tag: <number>
Retention policy observed: keep-daily 14, keep-weekly 8, pass/fail
restic check: pass/fail
Restore drill target: disposable, yes/no
Restored dump non-zero: pass/fail/not run
Restored schema version: <version only>/not run
Cleanup completed: yes/no/not run
Secrets, repository URL credentials, dump contents, restored rows, DB URLs, private trade notes included: no
Residual risk: local-only target is not geographic or ransomware-resistant, if applicable
```

Do not record full repository URLs, usernames if they identify private
infrastructure, access keys, `RESTIC_PASSWORD`, dump filenames with private
context, restored row contents, private symbols, private journal content,
provider payloads, screenshots of private records, or raw command output that
contains sensitive paths or credentials.

For the local Windows encrypted restic repository accepted during private
staging validation, the same evidence rules apply. The local target is useful as
operator-controlled encrypted redundancy, but it is not geographic or
ransomware-resistant backup coverage by itself. Treat stronger private-data or
production-like reliance as gated by a later decision issue.

Suggested systemd service after the local backup timer succeeds:

```ini
[Unit]
Description=Cilly Trading Signal offsite encrypted backup
Wants=network-online.target cilly-postgres-backup.service
After=network-online.target cilly-postgres-backup.service

[Service]
Type=oneshot
User=root
Group=root
WorkingDirectory=/root/repos/cilly-trading-signal
EnvironmentFile=/etc/cilly-trading-signal/offsite-backup.env
ExecStart=/usr/bin/restic backup /srv/backups/cilly-trading-signal/postgres --tag cilly-postgres --tag private-staging
ExecStart=/usr/bin/restic forget --tag cilly-postgres --keep-daily 14 --keep-weekly 8 --prune
```

Suggested timer:

```ini
[Unit]
Description=Run Cilly Trading Signal offsite encrypted backup daily

[Timer]
OnCalendar=*-*-* 04:05:00
Persistent=true
RandomizedDelaySec=15m

[Install]
WantedBy=timers.target
```

Verify offsite backup freshness with sanitized output only:

```bash
set -a
. /etc/cilly-trading-signal/offsite-backup.env
set +a
restic snapshots --tag cilly-postgres --json | jq length
restic check
```

Record only pass/fail, timestamp, repository category, snapshot count, and
whether `restic check` passed. Do not record repository credentials or snapshot
contents.

#### Offsite Restore Drill

Run an offsite restore drill before relying on offsite backups. The restore
target must be disposable and must not be `cilly-trading-signal`, `staging`, or
any production-like database.

1. Choose a disposable restore directory outside the repository.

```bash
export OFFSITE_RESTORE_DIR=/srv/restore-drills/cilly-offsite-restore-YYYYMMDD
install -d -m 700 "$OFFSITE_RESTORE_DIR"
```

2. Restore the latest offsite backup snapshot into that directory.

```bash
set -a
. /etc/cilly-trading-signal/offsite-backup.env
set +a
restic restore latest --target "$OFFSITE_RESTORE_DIR" --tag cilly-postgres
find "$OFFSITE_RESTORE_DIR" -type f -name 'cilly_trading_signal_*.dump' -printf '%s %f\n' | sort | tail -1
```

3. Select the restored dump path without printing contents.

```bash
export RESTORE_DUMP="$(find "$OFFSITE_RESTORE_DIR" -type f -name 'cilly_trading_signal_*.dump' | sort | tail -1)"
test -s "$RESTORE_DUMP"
```

4. Restore into a disposable Compose project using the same rules as the backup
restore drill. Create required roles in the disposable database before restore
when the source dump contains owner metadata.

```bash
export DRILL_PROJECT=cilly_offsite_restore_drill
docker compose -p "$DRILL_PROJECT" -f infra/docker-compose.yml up -d postgres
docker compose -p "$DRILL_PROJECT" -f infra/docker-compose.yml exec -T postgres \
  psql --username postgres --dbname postgres -c "DO \$\$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'cilly_app') THEN CREATE ROLE cilly_app LOGIN; END IF; END \$\$;"
docker cp "$RESTORE_DUMP" "${DRILL_PROJECT}-postgres-1:/tmp/restore.dump"
docker compose -p "$DRILL_PROJECT" -f infra/docker-compose.yml exec -T postgres \
  pg_restore --username postgres --dbname cilly_trading_signal --clean --if-exists /tmp/restore.dump
docker compose -p "$DRILL_PROJECT" -f infra/docker-compose.yml exec -T postgres \
  psql --username postgres --dbname cilly_trading_signal --tuples-only --no-align -c "select version_num from alembic_version;"
```

5. Clean up only the disposable restore project and restore directory after
recording sanitized evidence.

```bash
docker compose -p "$DRILL_PROJECT" -f infra/docker-compose.yml down --volumes
rm -rf -- "$OFFSITE_RESTORE_DIR"
```

Sanitized evidence to record:

- Offsite target category: SFTP / S3-compatible / other private target.
- Encryption: restic client-side encryption configured, pass/fail.
- Snapshot count: non-zero, pass/fail.
- `restic check`: pass/fail.
- Restore target: disposable project name.
- Restored dump non-zero: pass/fail.
- Restored schema version: version only.
- Cleanup completed: yes/no.
- Secrets, repository credentials, dump contents, DB URLs, and private data included: no.

## PostgreSQL Restore

Restore only after confirming the target database can be replaced and the selected backup file is the intended source. A restore should be tested on a non-production copy before relying on it operationally.

Restore with the helper script:

```bash
./scripts/restore_postgres.sh /srv/backups/cilly-trading-signal/postgres/cilly_trading_signal_YYYYMMDDTHHMMSSZ.dump
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

## Backup Restore Drill

Use this drill to verify that backup files can be restored without touching private staging, production-like, real-user, or real-trading data. This is an operator practice procedure, not a real production restore and not a production-readiness claim.

### Drill Safety Rules

- Restore only into an explicitly disposable Compose project, never into the private staging project, production-like project, or a real-data database.
- Use a dedicated Compose project name such as `cilly_restore_drill`; do not use `cilly-trading-signal`, `staging`, or any existing project name.
- Store source dumps outside the repository checkout.
- Do not commit, upload, screenshot, or paste dump contents, `.env` values, database URLs, credentials, cookies, logs with private data, trade notes, journal notes, or restored row contents.
- Use sample-only marker data for the drill when possible. If a real backup must be tested later, get separate approval and record only sanitized metadata.
- If the target environment is unclear, stop before running the restore command.

### Preconditions

- Docker and Docker Compose are available on the operator machine or VPS.
- The repository checkout is clean except for known local line-ending artifacts.
- A backup dump exists outside the repository checkout.
- The disposable project name, backup path, database name, and database user are written down before starting.
- The operator has confirmed the restore target can be destroyed after the drill.

### Step-by-Step Drill

1. Choose a disposable project name.

```bash
export COMPOSE_PROJECT_NAME=cilly_restore_drill
```

2. Choose a source dump outside the repository checkout.

```bash
export RESTORE_DUMP=/srv/backups/cilly-trading-signal/postgres/cilly_trading_signal_YYYYMMDDTHHMMSSZ.dump
test -f "$RESTORE_DUMP"
```

3. Start a disposable stack only for the drill. The restore helper stops and starts `api` and `web`, so create those disposable containers before running the restore.

```bash
docker compose -p "$COMPOSE_PROJECT_NAME" -f infra/docker-compose.yml up -d postgres api web
docker compose -p "$COMPOSE_PROJECT_NAME" -f infra/docker-compose.yml ps
```

4. Restore the selected dump into the disposable project.

```bash
COMPOSE_PROJECT_NAME="$COMPOSE_PROJECT_NAME" \
COMPOSE_FILE=infra/docker-compose.yml \
POSTGRES_USER=postgres \
POSTGRES_DB=cilly_trading_signal \
./scripts/restore_postgres.sh "$RESTORE_DUMP"
```

5. Confirm app services restarted for smoke verification.

```bash
docker compose -p "$COMPOSE_PROJECT_NAME" -f infra/docker-compose.yml ps
```

6. Verify sanitized health only.

```bash
curl -fsS http://localhost:8000/api/health
```

7. Optionally verify sample marker data without exposing sensitive contents.

```bash
docker compose -p "$COMPOSE_PROJECT_NAME" -f infra/docker-compose.yml exec postgres \
  psql -U postgres -d cilly_trading_signal -c "select count(*) from watchlist_items;"
```

8. Record sanitized evidence using the template below.

9. Clean up only the disposable project.

```bash
docker compose -p "$COMPOSE_PROJECT_NAME" -f infra/docker-compose.yml down --volumes
```

10. Confirm no dump files were created inside the repository checkout.

```bash
find . -name '*.dump' -o -name '*.sql' -o -name '*.backup' -o -name '*.bak'
```

### Sanitized Evidence Template

```markdown
## Backup Restore Drill Evidence

- Date/time:
- Operator:
- Environment level: local disposable / VPS disposable
- Disposable Compose project:
- Source backup path category: outside repository / external backup directory
- Source backup filename timestamp only:
- Restore target confirmed disposable: yes/no
- Restore command completed: pass/fail
- Container health after restore: pass/fail
- API health after restore: pass/fail
- Optional sample-count check: pass/fail/not run
- Cleanup completed with `down --volumes` on disposable project only: yes/no
- Repository contains no dump/env artifacts after drill: yes/no
- Secrets/private data/raw logs included in this evidence: no
- Follow-up issue if failed:
```

### Cleanup Rules

- Remove only the disposable project created for the drill.
- Do not run broad Docker cleanup commands such as `docker system prune` or `docker volume prune` as part of this drill.
- Keep the source backup unless retention policy separately says it can be removed.
- If cleanup fails, record the disposable project name and inspect it before trying destructive commands.

### Stop Conditions

Stop the drill and create a follow-up issue if:

- The selected Compose project is not clearly disposable.
- The selected dump path is inside the repository checkout.
- The restore command would target private staging, production-like, or real data.
- The backup file is missing, zero bytes, or unexpectedly small.
- API health fails after restore.
- Evidence cannot be recorded without exposing secrets or private trading data.

## Basic Rollback

Rollback assumes the previous commit is still available and the database schema is compatible with the previous app version.

For the rollback and migration decision matrix, use
`docs/ROLLBACK_MIGRATION_SAFETY_CHECKLIST.md` before relying on rollback as
production-like evidence.

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
docker compose --env-file .env -f infra/docker-compose.yml --profile proxy up --build -d
```

4. Check health and core manual workflow.

```bash
curl -fsS https://trading.example.com/api/health
```

If a migration has already changed the database, do not assume code rollback is enough. Confirm whether a database restore is required before continuing.

## Post-Deploy Checks

Minimum checks after first deploy or update:

- `docker compose --env-file .env -f infra/docker-compose.yml --profile proxy ps` shows expected services running.
- `https://<APP_DOMAIN>/api/health` returns a healthy response.
- Web app loads over HTTPS.
- Admin login succeeds.
- Watchlist page loads.
- CSV import page loads.
- No secrets appear in logs or screenshots.
- UI wording still frames signals as manual decision-support only.

For a compact browser spot-check after deploying current `main` to private
staging, record sanitized pass/fail evidence for these routes:

| Route or workflow | Expected result |
| --- | --- |
| `/login` | Login succeeds over HTTPS with the configured operator account. |
| `/` | Dashboard loads and exposes the authenticated logout action. |
| `/watchlist` | Fake/sample watchlist state loads or can be created manually. |
| `/screener` | Sample screener upload path remains manual review only. |
| `/import` | Sample CSV import controls load without private data. |
| `/signals` | Signal cards remain decision support with No-Trade/data-quality context. |
| `/reviews` | Paper/historical review wording remains evidence-only. |
| `/trades` | Trade logging remains manual documentation of external actions only. |
| `/performance` | R-multiple summaries remain historical/paper documentation only. |
| `/alerts` | Alert events remain review prompts, not trade instructions. |
| `/settings` | Settings load without exposing secrets and logout remains visible. |
| Logout/protected route | Logout succeeds and protected pages require login again. |

Use `docs/FINAL_BROWSER_CLICKTHROUGH_CHECKLIST.md` for the full 20-step
browser workflow. Do not reset private staging volumes, restore backups, rotate
secrets, or restart VPS services as part of a browser spot-check without
explicit operator approval.

## Known Gaps

- Automated deployment smoke tests are not implemented; the checklist above is
  manual. The current evaluation keeps browser smoke manual for now and records
  future implementation constraints in
  `docs/POST_DEPLOY_BROWSER_SMOKE_AUTOMATION_EVALUATION.md`.

# Staging Deploy And Migration Recovery Runbook

## Purpose

This runbook defines the repeatable private-staging deploy and migration recovery
path for the owner/operator VPS after v6.0. It captures the operational lessons
from the v5.9 staging update and the sanitized DB credential recovery evidence in
`docs/reviews/v6-0-staging-database-credential-recovery.md`.

This is private-staging operations guidance only. It is not production readiness,
private trading data readiness, broker readiness, live/realtime market-data
evidence, profitability evidence, strategy validation, trading advice, real-money
readiness, or approval for automatic execution.

## Fixed Staging Context

Use these values for the current private-staging app unless a later issue changes
the environment explicitly:

| Item | Value |
| --- | --- |
| Deploy user | `cillydeploy` |
| Repository path | `/srv/apps/cilly-trading-signal` |
| Compose project | `cilly-trading-signal` |
| Compose file | `infra/docker-compose.yml` |
| Env file | `.env` on the VPS only, never in git or shared evidence |
| Public app URL | `https://trading.cillyonline.de` |
| API health URL | `https://trading.cillyonline.de/api/health` |

Keep the unrelated `staging` Compose project separate and untouched.

## Evidence And Privacy Rules

- Record command names, pass/fail status, environment class, commit SHA, route
  names, and sanitized failure categories only.
- Do not paste `.env`, `DATABASE_URL`, passwords, API keys, provider keys, cookies,
  database rows, SQL query output with private records, raw logs, screenshots with
  sensitive data, private symbols, broker/account data, or backup contents.
- Do not claim production readiness, private-data readiness, broker readiness,
  profitability, strategy validation, real-money readiness, live/realtime data, or
  automatic execution from a successful staging deploy.

## Standard Deploy

Run from a trusted operator machine. Do not include prompts, secrets, or raw logs in
shared evidence.

```powershell
$Server = "159.195.46.99"
$User = "cillydeploy"
$AppDir = "/srv/apps/cilly-trading-signal"
```

Update the checkout and confirm the deployed commit:

```powershell
ssh "$User@$Server" "cd $AppDir && git fetch origin && git switch main && git pull --ff-only origin main && git rev-parse HEAD"
git rev-parse origin/main
```

Build and restart the intended Compose project. Always include `-p
cilly-trading-signal`; omitting it can create a conflicting default project.

```powershell
ssh "$User@$Server" "cd $AppDir && docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy up -d --build"
```

Run migrations from the API container:

```powershell
ssh "$User@$Server" "cd $AppDir && docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy exec -T api alembic upgrade head"
```

Verify API and web:

```powershell
Invoke-RestMethod https://trading.cillyonline.de/api/health
$response = Invoke-WebRequest https://trading.cillyonline.de -UseBasicParsing
$response.StatusCode
```

Expected sanitized evidence:

- Commit on VPS matches `origin/main`: pass
- Compose project `cilly-trading-signal` rebuild/restart: pass
- Alembic `upgrade head`: pass
- API health: pass
- Web load: pass, HTTP 200
- Secrets/private data/raw logs/screenshots included: no

## Compose Stack Checks

List running containers and Compose projects before destructive cleanup:

```powershell
ssh "$User@$Server" "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}'"
ssh "$User@$Server" "docker compose ls"
```

Expected app containers use the `cilly-trading-signal-` prefix. If containers use
the `infra-` prefix after an accidental deploy command, treat them as a mistaken
partial stack from this repository and inspect before stopping:

```powershell
ssh "$User@$Server" "cd $AppDir && docker compose -p infra -f infra/docker-compose.yml ps"
```

If the `infra` project is the mistaken partial stack for this app, stop it without
deleting volumes:

```powershell
ssh "$User@$Server" "cd $AppDir && docker compose -p infra -f infra/docker-compose.yml down --remove-orphans"
```

Do not use `--volumes` during routine cleanup. Do not run `docker volume rm`,
`docker volume prune`, `docker system prune`, or commands against unrelated
Compose projects without a separate explicit approval and backup/restore decision.

## Port Conflict Triage

If `up -d --build` fails with a localhost port conflict, identify the owner before
stopping anything:

```powershell
ssh "$User@$Server" "docker ps --filter publish=8000 --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}'"
ssh "$User@$Server" "docker ps --filter publish=3000 --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}'"
```

Only stop the mistaken partial app stack if it is clearly the accidental `infra`
project for this repository. Keep the intended `cilly-trading-signal` stack and the
unrelated `staging` project separate unless the operator explicitly approves a
maintenance action.

## Alembic Failure Triage

If Alembic fails, classify the failure without dumping secrets or database rows:

| Category | Meaning | Handling |
| --- | --- | --- |
| `db_auth_failed` | API database user/password cannot authenticate. | Use the DB credential mismatch section below. |
| `db_unreachable` | API cannot reach the Postgres service or network. | Check Compose project and container health. |
| `migration_error` | Alembic connects but migration fails. | Stop and create a focused issue with sanitized traceback category only. |
| `unknown` | Failure does not fit a known category. | Stop and record sanitized command/result only. |

Do not paste full stack traces if they include database URLs, private paths, row
data, `.env` values, or credentials. Prefer the category and final pass/fail state.

## DB Credential Mismatch Triage

Use this only when Alembic or API startup indicates database authentication failure.

First inspect redacted environment shape only:

```powershell
ssh "$User@$Server" "cd $AppDir && docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy exec -T api env | grep -E '^(DATABASE_URL)=' | sed -E 's#://([^:]+):[^@]+@#://\1:REDACTED@#'"
ssh "$User@$Server" "cd $AppDir && docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy exec -T postgres env | grep -E '^(POSTGRES_USER|POSTGRES_DB|POSTGRES_PASSWORD)=' | sed -E 's#POSTGRES_PASSWORD=.*#POSTGRES_PASSWORD=REDACTED#'"
```

Safe conclusions from the redacted output:

- `DATABASE_URL` exists or is missing.
- API database user, host, and database name are visible without revealing the
  password.
- Postgres container env variable names are visible without revealing the password.

Unsafe conclusions:

- Do not assume changing `POSTGRES_USER` or `POSTGRES_PASSWORD` updates an already
  initialized PostgreSQL volume. PostgreSQL init env is applied only when the data
  directory is first created.
- Do not delete the Postgres volume to resolve a password mismatch.

Preferred recovery paths:

1. If the current DB password is known through the operator's password manager,
   update the VPS-local `.env` so `DATABASE_URL` matches the initialized DB role,
   restart the API, then run Alembic and health checks.
2. If rotating the DB password is required, perform it during an explicit
   maintenance window. Generate the new password in a trusted shell or password
   manager, set the PostgreSQL role password, update the VPS-local `.env`, restart
   the API, and verify Alembic/API/web. Do not paste the password into chat, docs,
   issues, PRs, screenshots, or reusable scripts committed to git.
3. If the old password is unknown and PostgreSQL local client auth must be
   temporarily relaxed, use a one-time operator-owned maintenance script on the VPS
   only. The script must back up `pg_hba.conf`, prepend `local all all trust`, reload
   Postgres, set the role password, restore `pg_hba.conf`, reload Postgres again,
   update the VPS-local `.env`, restart the API, verify final checks, and delete the
   temporary script. Confirm `pg_hba.conf` is restored before continuing.

Required final checks after DB credential recovery:

```powershell
ssh "$User@$Server" "cd $AppDir && docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy exec -T -u root postgres sh -lc 'head -5 /var/lib/postgresql/data/pg_hba.conf; ls -l /var/lib/postgresql/data/pg_hba.conf.bak 2>/dev/null || true'"
ssh "$User@$Server" "cd $AppDir && docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy exec -T api alembic upgrade head"
Invoke-RestMethod https://trading.cillyonline.de/api/health
$response = Invoke-WebRequest https://trading.cillyonline.de -UseBasicParsing
$response.StatusCode
```

Expected final evidence:

- `pg_hba.conf` temporary trust state left active: no
- `pg_hba.conf.bak` leftover: no, or explicitly removed/restored during maintenance
- Database volume deleted: no
- Alembic `upgrade head`: pass
- API health: pass
- Web load: pass
- Secrets/private data/raw logs/screenshots included: no

## Rollback

For a failed deploy where the previous stack is still running, do not run broad
cleanup. Record the failure category and stop.

For a failed deploy after containers were recreated:

1. Confirm whether the current failure is code, config, database, or host-level.
2. If a known previous Git commit must be restored, use `git switch main`, `git
   reset` only with explicit operator approval, or a reviewed revert PR. Do not run
   destructive Git commands ad hoc.
3. Re-run Compose with the intended project name and current VPS-local `.env`.
4. Verify Alembic only when database compatibility is understood.

If rollback would require database volume deletion or restore from backup, stop and
open a dedicated backup/restore decision issue. Offsite backup/restore remains
deferred unless a later gate changes that decision.

## Sanitized Evidence Template

```markdown
- Date/time UTC:
- Operator or role:
- Environment class: private staging
- Repository path checked: /srv/apps/cilly-trading-signal
- Compose project checked: cilly-trading-signal
- Commit SHA:
- Git fetch/pull: pass / fail / skipped
- Mistaken partial stack present: no / yes, stopped without volumes / not checked
- Compose rebuild/restart: pass / fail / skipped
- Alembic upgrade head: pass / fail / skipped
- API health: pass / fail / skipped
- Web load: pass / fail / skipped
- DB credential mismatch encountered: no / yes, recovered / yes, blocked
- pg_hba.conf restored after maintenance: yes / not applicable / blocked
- Database volume deleted: no
- Follow-up issue:
- Secrets, .env values, DATABASE_URL, DB passwords, raw logs, database rows, backups, screenshots with sensitive data, private symbols, broker data, or private trading records included: no
- Production-readiness, private-data-readiness, broker-readiness, profitability, strategy-validation, live/realtime, real-money-readiness, or automatic-execution claim made: no
```

## Final Boundary

A passing staging deploy proves only that the tested private-staging app stack is
reachable and migrations completed for the checked commit. It does not approve
private trading data, production-like/public exposure, broker integration,
automatic execution, live/realtime data reliance, profitability, strategy
validation, or real-money use.

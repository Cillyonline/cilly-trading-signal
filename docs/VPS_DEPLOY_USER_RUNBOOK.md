# VPS Deploy User Runbook

## Purpose

This runbook defines a non-root deploy-user path for routine private VPS staging
operations.

This is an operational hardening step for controlled private staging. It is not a
production-readiness statement, public SaaS approval, broker-readiness claim,
profitability claim, trading advice, or approval for automatic execution.

## Status

- Issue: #178.
- Procedure status: documented.
- Server application status: pending operator-run on the VPS.
- Reason application is pending: user creation, SSH setup, group membership, and
  file ownership changes require live VPS access and must not be simulated from a
  repository-only session.

## Target User Model

Use an app-specific deploy user for routine operations:

```text
cillydeploy
```

Routine operations for `cillydeploy`:

- Pull the repository.
- Manage only this app's Docker Compose project, `cilly-trading-signal`.
- Run health and status checks.
- Read this app's local `.env` only as needed for Compose startup.
- Record sanitized pass/fail evidence.

Do not use `cillydeploy` for:

- Managing unrelated projects.
- Editing unrelated project files.
- Storing SSH private keys in the repository checkout.
- Running broad system administration tasks.
- Removing root emergency access.

## Sudo Boundary

Do not grant `cillydeploy` passwordless broad `sudo` as part of this procedure.

Expected routine privilege model:

- `cillydeploy` can run Git, Docker Compose, and health checks without `sudo`.
- One-time host administration remains a root or administrator task.
- Firewall, package, Docker daemon, systemd, user, and ownership repairs remain root
  or administrator tasks.
- If a future task needs a narrow sudo rule, document and review that rule in a
  separate issue before applying it.

## Security Boundary

Membership in the `docker` group grants root-equivalent control of the host through
the Docker socket. For this single-operator private staging VPS, this is the minimal
practical path for non-root Docker Compose operations, but it is not strong
multi-user isolation.

If the VPS becomes multi-user or public-production infrastructure, replace this with
a separate hardening review before relying on it.

## Target Paths

Use a non-root-owned app checkout for routine operations:

```text
/srv/apps/cilly-trading-signal
```

Keep runtime data, backups, logs, and secrets outside the Git repository. The app's
local `.env` may live in the checkout because the current Compose file reads
`../.env` from `infra/docker-compose.yml`, but it must remain untracked and readable
only by the deploy user and root.

Do not move or modify the existing unrelated `staging` project or its files.

## One-Time Root Setup

Run only from root or another authorized administrative account on the VPS. Do not
paste SSH public keys, private keys, passwords, `.env` contents, or raw server output
into issues, PRs, docs, screenshots, or chat.

Create the user:

```bash
adduser --disabled-password --gecos "" cillydeploy
usermod -aG docker cillydeploy
```

Install the operator's SSH public key without recording the key material in this
repository:

```bash
install -d -o cillydeploy -g cillydeploy -m 700 /home/cillydeploy/.ssh
editor /home/cillydeploy/.ssh/authorized_keys
chown cillydeploy:cillydeploy /home/cillydeploy/.ssh/authorized_keys
chmod 600 /home/cillydeploy/.ssh/authorized_keys
```

Create the checkout parent:

```bash
install -d -o root -g root -m 755 /srv/apps
install -d -o cillydeploy -g cillydeploy -m 750 /srv/apps/cilly-trading-signal
```

Log out and back in as `cillydeploy` so group membership is refreshed.

## Initial Checkout Or Migration

If this app has no checkout yet:

```bash
ssh cillydeploy@<vps-host>
cd /srv/apps/cilly-trading-signal
git clone https://github.com/Cillyonline/cilly-trading-signal.git .
```

If a root-owned checkout already exists at `/root/repos/cilly-trading-signal`, migrate
only after confirming the app is stopped or after a maintenance window:

```bash
docker compose --env-file /root/repos/cilly-trading-signal/.env -p cilly-trading-signal -f /root/repos/cilly-trading-signal/infra/docker-compose.yml --profile proxy ps
```

Then copy the repository and local `.env` with ownership preserved for the deploy
user. Do not copy logs, backup dumps, database files, or unrelated project files into
the repository checkout.

```bash
rsync -a --exclude '.git' /root/repos/cilly-trading-signal/ /srv/apps/cilly-trading-signal/
rsync -a /root/repos/cilly-trading-signal/.git /srv/apps/cilly-trading-signal/.git
chown -R cillydeploy:cillydeploy /srv/apps/cilly-trading-signal
chmod 600 /srv/apps/cilly-trading-signal/.env
```

If `.env` does not exist yet, create it as `cillydeploy` from `.env.example` and
replace every unsafe placeholder with staging-safe values. Do not paste the values
into docs, issues, PRs, screenshots, or chat.

## Routine Deploy Commands

Run as `cillydeploy` from `/srv/apps/cilly-trading-signal`:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy up --build -d
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy ps
curl -fsS https://trading.cillyonline.de/api/health
curl -fsSI https://trading.cillyonline.de/
```

Do not use `docker compose down --volumes`, `docker volume prune`, `docker system
prune`, or commands targeting the unrelated `staging` project during routine deploys.

## Routine Status Checks

Run as `cillydeploy`:

```bash
cd /srv/apps/cilly-trading-signal
id
groups
sudo -n true
docker compose ls
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy ps
curl -fsS https://trading.cillyonline.de/api/health
curl -fsSI https://trading.cillyonline.de/
```

Expected:

- `cillydeploy` belongs to the `docker` group.
- `sudo -n true` fails unless a separately approved narrow sudo boundary exists.
- `cilly-trading-signal` Compose checks work without `sudo`.
- The unrelated `staging` project is visible only as a separate Compose project and is
  not modified.
- HTTPS app and API health checks pass.
- Direct app ports remain localhost-only, per `docs/VPS_FIREWALL_HARDENING_PLAN.md`.

## Root Emergency Access

Do not remove root emergency access as part of this issue. Root remains the
break-glass path for:

- Repairing SSH access.
- Rolling back firewall mistakes.
- Repairing Docker daemon or host package problems.
- Fixing file ownership if `cillydeploy` cannot access the app checkout.

Root should not be used for routine app deploys once `cillydeploy` is verified.

## Rollback

If the deploy user setup causes problems, stop using `cillydeploy` and revert to the
previous root-run workflow temporarily.

Optional cleanup, only after confirming no running process depends on the user-owned
checkout:

```bash
gpasswd -d cillydeploy docker
passwd -l cillydeploy
```

Do not delete `/srv/apps/cilly-trading-signal` until `.env`, Git state, and any local
operator notes have been reviewed for safe retention or removal.

## Sanitized Evidence To Record

Record only sanitized pass/fail summaries:

- Date/time.
- SSH login as `cillydeploy`: PASS/FAIL.
- `cillydeploy` group membership includes `docker`: PASS/FAIL.
- This app's Compose `ps` works without `sudo`: PASS/FAIL.
- HTTPS app route: PASS/FAIL.
- HTTPS API health: PASS/FAIL.
- Existing unrelated `staging` project remained running and separate: PASS/FAIL.
- Root emergency access preserved: YES/NO.
- Secrets or SSH key material avoided in evidence: YES/NO.
- Known gaps or follow-ups.

Do not record SSH keys, `.env` values, private domains if sensitive, public IPs if
private, cookies, database URLs, tokens, raw logs, or raw Docker output containing
sensitive context.

## Final Gate

The non-root deploy-user path is not considered applied until the operator records
sanitized VPS evidence showing SSH login, Docker Compose access, app health checks,
unrelated project preservation, and root emergency access preservation.

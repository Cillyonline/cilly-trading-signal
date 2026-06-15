# v5.8 Deploy-User Routine Operations Evidence

Date: 2026-06-15

## Scope

This file records the v5.8 deploy-user routine-operations verification procedure
and current evidence status for issue #755.

This is a private-staging operations artifact only. It is not production-readiness
evidence, public SaaS readiness, broker-readiness evidence, profitability
evidence, strategy-validation evidence, trading advice, real-money readiness, or
approval for automatic execution.

## Existing Context

`docs/VPS_STAGING_DECISION_GATE.md` records earlier private-staging hardening
evidence that `cillydeploy` could SSH with the operator key, authenticate to
GitHub with the read-only deploy key, run Git fetch/pull, and run Docker Compose
status checks without broad passwordless sudo.

The 2026-06-14 post-refresh VPS validation was performed as `root`. The
2026-06-15 re-verification below confirms the deploy user can perform routine
status, Git, Compose, and health checks without broad passwordless sudo.

## Re-Verification Procedure

Run as the owner/operator from a trusted machine. Do not paste SSH keys,
passwords, `.env` contents, cookies, tokens, private paths that reveal account
context, raw logs, or screenshots.

```bash
ssh cillydeploy@<vps-host> 'hostname && whoami && date -u'
```

Then, as `cillydeploy` on the VPS:

```bash
cd /srv/apps/cilly-trading-signal
git status --short --branch
git fetch origin
git switch main
git pull --ff-only origin main
id
groups
sudo -n true && echo UNEXPECTED_PASSWORDLESS_SUDO || echo NO_BROAD_PASSWORDLESS_SUDO
docker compose ls
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy ps
curl -fsS https://trading.cillyonline.de/api/health
curl -fsSI https://trading.cillyonline.de/ | head -n 1
```

Expected results:

- `whoami` returns `cillydeploy`.
- Git status/fetch/pull can run from the deploy-user checkout.
- `groups` includes `docker`.
- Broad passwordless sudo is not available unless a separately approved narrow sudo
  rule exists.
- `cilly-trading-signal` Compose status works without `sudo`.
- The unrelated `staging` Compose project remains separate and unaffected.
- HTTPS API and web health pass.

## Sanitized Evidence

- Date/time UTC: 2026-06-15
- Operator or role: owner/operator
- Environment class: private staging
- Target domain: `trading.cillyonline.de`
- Deploy user: `cillydeploy`
- Checkout path: `/srv/apps/cilly-trading-signal`
- SSH login as deploy user: pass
- Git fetch/pull as deploy user: pass; checkout fast-forwarded to `105b6222263e02126cc8ce0eba09f444f4310ccf`
- `docker` group membership: pass; `groups` includes `docker`
- Broad passwordless sudo absent or narrowly justified: pass; `sudo -n true` required a password and returned `NO_BROAD_PASSWORDLESS_SUDO`
- Compose status without `sudo`: pass
- Existing unrelated `staging` project unaffected: pass; visible as separate `running(1)` Compose project
- HTTPS API health as part of deploy-user check: pass; returned `status=ok` and `environment=staging`
- HTTPS web health as part of deploy-user check: pass; returned HTTP 200
- Root emergency access preserved: not changed by this issue
- Running Compose project config path: currently listed as `/root/repos/cilly-trading-signal/infra/docker-compose.yml` because the active stack was last started from the root checkout
- Failed or blocked steps: none for routine status/health re-verification
- Follow-up issues or PRs: consider a later deploy-user-only restart if the owner/operator wants the active Compose project metadata to point at `/srv/apps/cilly-trading-signal`
- Secrets, SSH key material, `.env` values, database URLs, cookies, tokens, raw
  logs, private symbols, broker data, screenshots with sensitive data, or private
  trading records included: no
- Production-readiness, live/realtime, broker-readiness, profitability,
  strategy-validation, trading-advice, real-money-readiness, or
  automatic-execution claim made: no

## Current Status

Status: pass for deploy-user routine status/health re-verification.

The owner/operator verified SSH login, Git fetch/pull, Docker group membership,
absence of broad passwordless sudo, Compose status, HTTPS API health, HTTPS web
health, and unrelated-project separation as `cillydeploy`.

The active Compose project still reports the root checkout path because the stack
was previously started from `/root/repos/cilly-trading-signal`. That does not block
routine status/health checks, but a future deploy-user-only restart can align the
active Compose metadata with `/srv/apps/cilly-trading-signal` if desired.

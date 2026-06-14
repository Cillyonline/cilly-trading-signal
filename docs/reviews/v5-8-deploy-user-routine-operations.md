# v5.8 Deploy-User Routine Operations Evidence

Date: 2026-06-14

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

The 2026-06-14 post-refresh VPS validation was performed as `root`, so v5.8 still
needs a current deploy-user re-verification before treating routine operations as
fresh readiness evidence.

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

- Date/time UTC: not run in v5.8
- Operator or role: owner/operator
- Environment class: private staging
- Target domain: `trading.cillyonline.de`
- Deploy user: `cillydeploy`
- Checkout path: `/srv/apps/cilly-trading-signal`
- SSH login as deploy user: not run in v5.8
- Git fetch/pull as deploy user: not run in v5.8
- `docker` group membership: not run in v5.8
- Broad passwordless sudo absent or narrowly justified: not run in v5.8
- Compose status without `sudo`: not run in v5.8
- Existing unrelated `staging` project unaffected: not run in v5.8
- HTTPS API health as part of deploy-user check: not run in v5.8
- HTTPS web health as part of deploy-user check: not run in v5.8
- Root emergency access preserved: not changed by this issue
- Failed or blocked steps: owner/operator deploy-user re-verification not yet run
- Follow-up issues or PRs: required if v5.8 review needs a fresh pass result
- Secrets, SSH key material, `.env` values, database URLs, cookies, tokens, raw
  logs, private symbols, broker data, screenshots with sensitive data, or private
  trading records included: no
- Production-readiness, live/realtime, broker-readiness, profitability,
  strategy-validation, trading-advice, real-money-readiness, or
  automatic-execution claim made: no

## Current Status

Status: blocked / not re-run in v5.8.

The safe re-verification procedure is documented. Do not use this file as fresh
private-data readiness pass evidence until an owner/operator runs the deploy-user
checks and updates the sanitized evidence fields from `not run in v5.8` to concrete
pass/fail values.

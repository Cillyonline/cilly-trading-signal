# VPS Firewall Hardening Plan

## Purpose

This document defines a minimal, reversible host firewall hardening plan for the
private VPS staging environment.

This is an operations plan. It is not a production-readiness statement, public SaaS
approval, broker-readiness claim, profitability claim, trading advice, or approval
for automatic execution.

## Status

- Issue: #177.
- Plan status: documented.
- Application status: pending operator-run on the VPS.
- Reason application is pending: applying firewall rules requires live SSH/root access
  to the VPS and must not be simulated or claimed from a repository-only session.

## Safety Boundaries

- Preserve SSH access.
- Preserve this app's public Caddy access on `80/tcp` and `443/tcp`.
- Preserve Docker networking for this app and the existing unrelated `staging` project.
- Do not modify unrelated project files, data, containers, or Compose configuration.
- Do not expose direct app ports `3000` or `8000` publicly.
- Do not expose existing localhost-bound port `18000` publicly.
- Do not paste raw firewall dumps, public IPs if private, `.env` values, tokens,
  private keys, database URLs, cookies, or logs with sensitive data into docs, issues,
  PRs, screenshots, or chat.

## Current Known Posture

From `docs/VPS_INVENTORY.md` and the private staging decision gate:

- VPS OS: Debian 13.
- SSH listens on public `22/tcp`.
- `ufw` and `firewalld` were not found during inventory.
- iptables default `INPUT` policy was `ACCEPT`.
- Docker-managed forwarding rules exist.
- Existing unrelated Compose project: `staging`.
- Existing unrelated API binding: `127.0.0.1:18000->8000/tcp`.
- This app should expose public HTTPS only through Caddy on `80/tcp` and `443/tcp`.
- This app's direct API/web ports should remain localhost-only on `127.0.0.1:8000`
  and `127.0.0.1:3000` if retained for operator checks.

## Chosen Approach

Use a minimal host-level `nftables` input filter, applied first as a runtime rule with
an automatic rollback timer. This avoids installing a new firewall frontend such as
`ufw` and avoids flushing Docker-managed tables.

The rule allows only:

- loopback traffic
- established and related connections
- SSH on `22/tcp`
- HTTP on `80/tcp`
- HTTPS on `443/tcp`
- basic ICMP and ICMPv6 for network diagnostics

Everything else inbound to the host is dropped by the custom input chain. Docker
forwarding behavior is not intentionally changed by this plan.

## Preflight Checks

Run from an active SSH session on the VPS. Keep a second SSH session open before
applying rules.

Do not paste full output if it includes sensitive data.

```bash
cd /root/repos/cilly-trading-signal
git status --short --branch
docker compose ls
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy ps
ss -tulpen | grep -E ':(22|80|443|3000|8000|18000)\b' || true
command -v nft
nft --version
```

Expected:

- Repository checkout is clean on the intended branch.
- Existing unrelated `staging` project remains running.
- `cilly-trading-signal` services are running if staging is active.
- SSH is reachable.
- Public `80` and `443` are intentionally used by this app's Caddy when staging is active.
- Direct `3000` and `8000` are not bound to public interfaces.
- Existing `18000` remains localhost-bound.
- `nft` is available.

## Runtime Apply With Automatic Rollback

Run this only from the VPS console or an SSH session with a second SSH session open.
The rollback removes the custom table after two minutes unless cancelled.

```bash
systemd-run --unit=cilly-fw-rollback --on-active=2min /usr/sbin/nft delete table inet cilly_host_filter
```

Apply the runtime rules:

```bash
nft add table inet cilly_host_filter
nft 'add chain inet cilly_host_filter input { type filter hook input priority 0; policy drop; }'
nft add rule inet cilly_host_filter input iif lo accept
nft add rule inet cilly_host_filter input ct state established,related accept
nft add rule inet cilly_host_filter input tcp dport 22 accept
nft add rule inet cilly_host_filter input tcp dport 80 accept
nft add rule inet cilly_host_filter input tcp dport 443 accept
nft add rule inet cilly_host_filter input ip protocol icmp accept
nft add rule inet cilly_host_filter input ip6 nexthdr ipv6-icmp accept
```

## Verification Before Cancelling Rollback

From a separate operator machine, verify SSH remains available before cancelling the
rollback timer.

From the VPS:

```bash
curl -fsS https://trading.cillyonline.de/api/health
curl -fsSI https://trading.cillyonline.de/
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy ps
docker compose ls
ss -tulpen | grep -E ':(22|80|443|3000|8000|18000)\b' || true
```

From the operator machine:

```powershell
ssh <deploy-or-root-user>@<vps-host> "echo ssh-ok"
Invoke-WebRequest -UseBasicParsing https://trading.cillyonline.de/api/health
Invoke-WebRequest -UseBasicParsing https://trading.cillyonline.de/
Test-NetConnection <vps-host> -Port 3000
Test-NetConnection <vps-host> -Port 8000
Test-NetConnection <vps-host> -Port 18000
```

Expected:

- SSH works from a new session.
- `https://trading.cillyonline.de/api/health` returns successfully.
- `https://trading.cillyonline.de/` returns successfully.
- `cilly-trading-signal` containers remain running.
- Existing unrelated `staging` project remains running and separate.
- Direct `3000` and `8000` remain localhost-only if present.
- Existing `18000` remains localhost-only.
- The external port checks for `3000`, `8000`, and `18000` report `TcpTestSucceeded: False`.

If any check fails, let the rollback timer remove the custom table or run:

```bash
nft delete table inet cilly_host_filter
```

## Cancel Rollback After Successful Verification

Only after SSH and HTTPS checks pass:

```bash
systemctl cancel cilly-fw-rollback.timer || true
systemctl cancel cilly-fw-rollback.service || true
```

## Persistence

Persist only after runtime verification passes. The exact Debian nftables include
layout must be checked on the VPS before writing persistent config.

Recommended safe path:

1. Back up current nftables config if present.
2. Confirm whether `/etc/nftables.conf` includes `/etc/nftables.d/*.nft`.
3. If includes are configured, write this app's host filter to
   `/etc/nftables.d/cilly-host-filter.nft`.
4. Run `nft -c -f /etc/nftables.conf` before restarting `nftables`.
5. Keep an automatic rollback timer active while testing persistence.

Do not overwrite an existing `/etc/nftables.conf` without reviewing it first.

## Rollback

Runtime rollback:

```bash
nft delete table inet cilly_host_filter
```

Persistent rollback, if persistence was configured:

```bash
rm -f /etc/nftables.d/cilly-host-filter.nft
nft -c -f /etc/nftables.conf
systemctl reload nftables
```

After rollback, re-check SSH, HTTPS health, Compose status, and unrelated `staging`
project status.

## Sanitized Evidence To Record

Record only sanitized pass/fail summaries:

- Date/time.
- Operator confirms second SSH session worked after rules were applied.
- `cilly-trading-signal` Compose project status: PASS/FAIL.
- Existing unrelated `staging` project remained running: PASS/FAIL.
- HTTPS app route: PASS/FAIL.
- HTTPS API health: PASS/FAIL.
- Direct `3000` and `8000` public exposure check: PASS/FAIL.
- Existing `18000` remains localhost-bound: PASS/FAIL.
- Rollback timer cancelled only after verification: YES/NO.
- Persistence applied: YES/NO.
- Known gaps or follow-ups.

Do not record raw firewall rule dumps if they expose sensitive host context.

## Final Gate

Firewall hardening is not considered applied until the operator records sanitized VPS
evidence showing the runtime apply, SSH verification, HTTPS checks, Compose isolation,
and rollback or persistence outcome.

# VPS Inventory

## Purpose

This document records a sanitized, read-only inventory of the existing VPS before any deployment or configuration changes are made for this project.

The VPS already hosts other projects. The goal is to understand the current server state and deployment constraints without disrupting existing services.

## Safety Rules

- Read-only inventory first.
- Do not restart services or containers during inventory.
- Do not change firewall, reverse proxy, Docker, DNS, certificates, volumes, or application config during inventory.
- Do not run destructive cleanup commands such as `docker system prune`, `docker volume prune`, `rm`, or `down --volumes`.
- Do not copy secrets, tokens, private keys, cookies, `.env` contents, database URLs, backup dump contents, or sensitive application data into this document.
- Redact public IPs, private domains, project names, user names, and paths when needed.
- If a command may expose secrets or change state, stop and decide before running it.

## Inventory Status

- Issue: #157
- Status: Completed for initial read-only deployment planning
- Inventory date: 2026-05-28
- Operator machine: Windows PowerShell over SSH
- VPS access method: SSH as root, target redacted
- Data classification: Sanitized summary only

## Server Overview

- Provider / VPS type: netcup KVM VPS, model VPS 1000 G12
- OS / distribution: Debian GNU/Linux 13 (trixie)
- Kernel: Linux 6.12.74+deb13+1-amd64
- CPU / memory: CPU count not recorded in this pass, 7.8 GiB RAM
- Disk layout and free space: root filesystem 251 GB total, 15 GB used, 226 GB available, 7% used
- Timezone: not recorded in this pass
- Active users relevant to deployment: root access observed; deploy-user status TBD
- Uptime at first inventory: 60 days, low load average
- Swap: none configured

## Network And Exposure

- Public web ports: none observed listening on `80` or `443`
- SSH port: `22` listening on IPv4 and IPv6
- Listening services: SSH on public interfaces; existing Docker API proxy on `127.0.0.1:18000`
- Firewall tool and status: `ufw` and `firewalld` not installed; iptables default `INPUT ACCEPT`, Docker-managed forward rules present
- Reverse proxy in use: none observed as a running systemd service for Caddy, Nginx, or Traefik
- TLS / certificate owner: none observed for this app; no reverse proxy service was running
- Existing domains / subdomains: not recorded in this pass; decide in #158

## Docker State

- Docker version: 29.3.1
- Docker Compose version: v5.1.1
- Running containers: one observed container for an existing staging project
- Compose projects: `staging`, running, config path under an existing project directory in `/root/...`
- Docker networks: default `bridge`, `host`, `none`, and one project network for `staging`
- Docker volumes: none listed by `docker volume ls`
- Published ports: existing staging API binds `127.0.0.1:18000->8000/tcp`
- Restart policies: existing staging container uses `unless-stopped`

## Existing Projects

| Project | Runtime | Domains / Ports | Data Volumes | Notes / Constraints |
| --- | --- | --- | --- | --- |
| Existing staging project | Docker Compose | API bound to `127.0.0.1:18000->8000/tcp`; external routing TBD | Bind mounts under `/srv/cilly/staging/...`; no named Docker volumes listed | Do not reuse port `18000`; do not modify `/root/...` existing project files or `/srv/cilly/staging`. |

## Reverse Proxy Notes

- Proxy service: none observed as a running systemd service for Caddy, Nginx, or Traefik
- Config location: none observed for Caddy, Nginx, or Traefik systemd services
- Current routing model: existing API is localhost-bound on port `18000`; public routing not yet observed
- Potential integration path for this app: likely safe to run this repo's Caddy profile on `80`/`443` if firewall and existing project constraints allow it
- Known conflicts: no listener conflict observed on `80` or `443`; avoid existing localhost port `18000`

## Backup And Storage Notes

- Existing backup approach: no root crontab output observed; system cron directory shows only system/default entries from the read-only listing
- Backup locations: `/srv/backups` and `/srv/backups/manual` exist
- Available disk space for PostgreSQL data and backups: root filesystem has 226 GB available at inventory time
- Restore evidence for existing projects: not inspected in this issue
- Constraints for this app: keep this app's future data and backups separate from `/srv/cilly/staging`

## Storage Layout Notes

- `/srv/apps/trading-engine` exists and appears to contain the existing project checkout.
- `/srv/apps/trading-engine_pre_repo_backup` exists.
- `/srv/data/trading-engine` exists.
- `/srv/cilly/staging` contains existing bind-mount data for the running staging container.
- `/srv/logs/trading-engine` exists.
- Future repository checkout for this project should follow the existing project pattern under `/root/repos/`, for example `/root/repos/cilly-trading-signal`.
- Future runtime data and backups for this project should remain outside the repository checkout and use separate paths that do not reuse existing trading-engine paths.

## Candidate Deployment Constraints

- Safe repository checkout path: `/root/repos/cilly-trading-signal`
- Safe Docker Compose project name: recommend `cilly-trading-signal`, to be confirmed in #158
- Candidate subdomain: decide in #158
- Required public ports: `80`, `443`
- Direct app ports must remain private / localhost-only: `8000`, `3000`
- Avoid host port `18000`, currently used by an existing staging API.
- PostgreSQL must not conflict with existing databases or volumes.
- Deployment must not modify unrelated projects.
- Do not reuse existing bind-mount paths under `/srv/cilly/staging`.
- Do not store PostgreSQL data, backups, `.env` copies, logs, or dump files inside `/root/repos/cilly-trading-signal`.

## Read-Only Command Checklist

Run only commands that are safe for the specific server. Record sanitized summaries, not raw secret-bearing output.

```bash
hostnamectl
uname -a
uptime
df -h
free -h
docker --version
docker compose version
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
docker compose ls
docker network ls
docker volume ls
ss -tulpen
systemctl list-units --type=service --state=running
```

Potentially privileged checks. Run only after confirming they are safe and expected for this VPS:

```bash
sudo ufw status verbose
sudo systemctl status caddy --no-pager
sudo systemctl status nginx --no-pager
sudo systemctl status traefik --no-pager
```

## Findings

- Initial host inventory completed. The server has substantial free disk capacity and low current load.
- Docker is installed and one existing Compose project is running.
- The existing project exposes an API on localhost port `18000`, which suggests reverse proxy routing may already be used or planned.
- No named Docker volumes are currently listed, but bind mounts may still be used by the existing project.
- No public listeners were observed on `80` or `443`.
- No Caddy, Nginx, or Traefik systemd service was found.
- `ufw` and `firewalld` were not found. iptables default INPUT policy is ACCEPT, with Docker-managed forwarding chains present.
- Existing Docker project uses bind mounts under `/srv/cilly/staging` for database, artifacts, journal, logs, and runtime state.
- Existing Docker restart policy is `unless-stopped`.
- `/srv/backups` exists, but no automated backup schedule was observed from the read-only cron checks.
- No restore evidence for existing projects was inspected.

## Risks And Unknowns

- No swap is configured. This may be acceptable for current load, but should be considered before running additional services.
- Root SSH access is currently used for inventory. A non-root deploy user should be evaluated before private VPS staging deployment.
- Docker appears to use `/var/lib/docker`.
- Existing project details are not fully known because reverse proxy config, bind mounts, environment files, and service logs were not inspected.
- Host port `18000` is already reserved by an existing localhost-bound API.
- Public SSH is open on port `22`; SSH hardening and non-root deploy access should be considered before staging use.
- If no reverse proxy is currently running, introducing this repo's Caddy stack on `80`/`443` may be straightforward but still requires DNS/firewall validation and confirmation that no external service depends on those ports.
- No host firewall frontend is installed. Before private VPS staging, decide whether to add a minimal firewall policy or accept the current provider/iptables posture.
- Because iptables INPUT defaults to ACCEPT, any future service bound to `0.0.0.0` becomes publicly reachable unless otherwise protected.
- Backup automation and restore evidence are not confirmed.

## Initial Go / No-Go Notes

- No-go for deployment until the non-disruptive deployment plan explicitly covers firewall posture, data paths, backup path, restore expectations, DNS, and Caddy ownership of `80`/`443`.

Based on the current read-only inventory, a private VPS staging deployment appears feasible if it:

- Keeps the existing `staging` Compose project untouched.
- Avoids host port `18000`.
- Uses `/root/repos/cilly-trading-signal` for the repository checkout, analogous to the existing project layout.
- Uses separate runtime data and backup paths outside the repository checkout.
- Uses only intentional public bindings on `80`/`443` through Caddy.
- Addresses the current no-firewall-frontend posture before or during the deployment plan.

## Follow-Ups

- #158 should define the non-disruptive VPS deployment plan.
- #159 should define the sanitized staging environment checklist.
- #161 should define minimum monitoring checks.
- #162 should verify backup and restore mechanics for this app's future data path.
- Consider a non-root deploy user before private staging deployment.
- Decide whether to introduce a minimal firewall policy or explicitly accept the current provider/iptables posture before binding public services.

# v4.2 VPS Trigger Radar Smoke

Date: 2026-06-04

Scope: Controlled private VPS smoke for deployment health, Import page, Signal Radar,
and Trigger Radar after the v3.8-v4.2 radar/import/provider updates.

## Summary

The private VPS deployment updated to current `main`, rebuilt the Docker Compose
stack, and passed API/web health checks after the services finished restarting. The
operator browser smoke passed for login, `/import`, CSV mapping/import UI,
`/signals`, Signal Radar, Trigger Radar, and manual-only wording.

This evidence is private owner/operator staging evidence only. It is not a
production-readiness claim, live/realtime data claim, broker-readiness claim,
trading advice, strategy-validation claim, profitability claim, or approval for
automatic execution.

## Deployment Evidence

Sanitized operator-run VPS steps:

- `git fetch origin`: pass.
- `git switch main`: pass.
- `git pull --ff-only origin main`: pass, updated to current `main`.
- `docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy up --build -d`: pass.
- Compose services after restart: `postgres` healthy; `api`, `web`, and `caddy` up.

Initial public HTTPS health check returned `502` immediately after restart. After a
short wait, all health checks passed:

- `http://127.0.0.1:8000/api/health`: pass.
- `http://127.0.0.1:3000`: pass.
- `https://trading.cillyonline.de/api/health`: pass.

No `.env` values, cookies, secrets, database URLs, provider keys, raw logs, private
symbols, broker data, account values, or screenshots were recorded in this evidence.

## Browser Smoke Evidence

Operator-reported browser checks:

```text
Login: PASS
/import loads: PASS
CSV mapping/import UI visible: PASS
/signals loads: PASS
Signal Radar visible: PASS
Trigger Radar visible: PASS
Manual-only wording: PASS
```

## Acceptance Criteria

- VPS health and web load pass: PASS.
- Trigger Radar wording remains conservative in the browser: PASS.
- Follow-up issues for discovered defects: NOT NEEDED; no defect was reported in
  this smoke.

## Boundaries Checked

- No provider decision was made.
- No provider key was configured or requested.
- No Telegram routing change was made.
- No broker integration, order execution, automatic trade creation, or automatic
  analysis was added.
- No production-readiness, live/realtime, profitability, or strategy-validation claim
  is made.

## Residual Risk

- This was a manual private VPS browser smoke, not automated browser coverage.
- Provider real-key Daily/EOD smoke remains separate under #614 and requires explicit
  provider-key approval.
- Production-like/public exposure remains gated by existing readiness and private-data
  decision gates.

## Decision

#605 is satisfied for the current private VPS Trigger Radar smoke. The workflow is
validated as controlled owner/operator staging evidence only, with manual execution
and decision-support boundaries preserved.

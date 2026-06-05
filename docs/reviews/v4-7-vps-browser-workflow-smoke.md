# v4.7 VPS Browser Workflow Smoke

Date: 2026-06-05

Scope: Controlled private VPS smoke for the v4.6 guided workflow hierarchy changes:
Dashboard `Heute starten` panel, `/import` CSV-Arbeitsplan first with collapsed
Provider-Sync, `/signals` Active Review/Trigger Radar primary with collapsed
Radar-Rangliste.

## Summary

VPS smoke pass/fail summary:

- Deployment update: PASS
- Health checks: PASS
- Dashboard `/` guided workflow: PASS
- Import `/import` hierarchy: PASS
- Signals `/signals` hierarchy: PASS
- Safety wording: PASS
- Follow-up issues needed: No

This evidence is private owner/operator staging evidence only. It is not a
production-readiness claim, live/realtime data claim, broker-readiness claim,
trading advice, strategy-validation claim, profitability claim, or approval for
automatic execution.

## Deployment Evidence

Sanitized operator-run VPS steps:

- `git fetch origin`: PASS
- `git switch main`: PASS
- `git pull --ff-only origin main`: PASS, commit: `ca30e3a`
- `docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy up --build -d`: PASS
- Compose services after restart: postgres healthy; api up; web up; caddy up

Health checks:

- `http://127.0.0.1:8000/api/health`: PASS
- `http://127.0.0.1:3000`: PASS
- `https://trading.cillyonline.de/api/health`: PASS

No `.env` values, cookies, secrets, database URLs, provider keys, raw logs, private
symbols, broker data, account values, or screenshots were recorded in this evidence.

## Browser Smoke Evidence

Operator-reported browser checks:

```text
/ loads without error: PASS
"Heute starten" panel visible: PASS
  Step 1 "Daten pruefen" with count and link: PASS
  Step 2 "Aktive Kandidaten pruefen" with count and link: PASS
  Step 3 "Trigger-Liste pruefen" with count and link: PASS
  Step 4 "Nacharbeit pruefen" with count and link: PASS
No buy/sell/live/broker wording on dashboard: PASS

/import loads without error: PASS
CSV-Arbeitsplan is the FIRST section after header: PASS
  Wochenupdate 1W card visible: PASS
  Tagesupdate 1D card visible: PASS
  Triggerupdate 4H card visible: PASS
Upload form below CSV-Arbeitsplan: PASS
Provider-Sync collapsed under "Provider-Sync (erweitert)": PASS
Provider-Sync expands on click: PASS
Import Readiness visible after file selection: PASS
Analyze-All section visible: PASS
Import History visible: PASS
No automatic/broker/live wording: PASS

/signals loads without error: PASS
Active Review Shortlist visible (primary): PASS
Trigger Radar visible (primary): PASS
Radar-Rangliste collapsed under "Radar-Rangliste (alle Signale)": PASS
Radar-Rangliste expands on click: PASS
Full signal list with filters visible when expanded: PASS
No buy/sell/live/broker wording: PASS
```

## Acceptance Criteria

- VPS health and web load pass: PASS
- Dashboard guided flow visible: PASS
- Import hierarchy matches v4.6 design: PASS
- Signals hierarchy matches v4.6 design: PASS
- Safety wording remains conservative: PASS
- Follow-up issues discovered: NOT NEEDED

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
- Production-like/public exposure remains gated by existing readiness and private-data
  decision gates.

## Follow-Up Issues

- None.

# v4.7 VPS Browser Workflow Smoke

Date: \_\_ (fill in)

Scope: Controlled private VPS smoke for the v4.6 guided workflow hierarchy changes:
Dashboard `Heute starten` panel, `/import` CSV-Arbeitsplan first with collapsed
Provider-Sync, `/signals` Active Review/Trigger Radar primary with collapsed
Radar-Rangliste.

## Summary

VPS smoke pass/fail summary:

- Deployment update: \_\_ (PASS | FAIL | BLOCKED)
- Health checks: \_\_ (PASS | FAIL | BLOCKED)
- Dashboard `/` guided workflow: \_\_ (PASS | FAIL | BLOCKED)
- Import `/import` hierarchy: \_\_ (PASS | FAIL | BLOCKED)
- Signals `/signals` hierarchy: \_\_ (PASS | FAIL | BLOCKED)
- Safety wording: \_\_ (PASS | FAIL | BLOCKED)
- Follow-up issues needed: \_\_ (Yes / No)

This evidence is private owner/operator staging evidence only. It is not a
production-readiness claim, live/realtime data claim, broker-readiness claim,
trading advice, strategy-validation claim, profitability claim, or approval for
automatic execution.

## Deployment Evidence

Sanitized operator-run VPS steps:

- `git fetch origin`: \_\_ (PASS | FAIL)
- `git switch main`: \_\_ (PASS | FAIL)
- `git pull --ff-only origin main`: \_\_ (PASS | FAIL), commit: \_\_
- `docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy up --build -d`: \_\_ (PASS | FAIL)
- Compose services after restart: postgres \_\_ ; api \_\_ ; web \_\_ ; caddy \_\_ (healthy / up / failed)

Health checks:

- `http://127.0.0.1:8000/api/health`: \_\_ (PASS | FAIL)
- `http://127.0.0.1:3000`: \_\_ (PASS | FAIL)
- `https://trading.cillyonline.de/api/health`: \_\_ (PASS | FAIL)

No `.env` values, cookies, secrets, database URLs, provider keys, raw logs, private
symbols, broker data, account values, or screenshots were recorded in this evidence.

## Browser Smoke Evidence

Operator-reported browser checks:

```text
/ loads without error: PASS | FAIL | BLOCKED
"Heute starten" panel visible: PASS | FAIL | BLOCKED
  Step 1 "Daten pruefen" with count and link: PASS | FAIL | BLOCKED
  Step 2 "Aktive Kandidaten pruefen" with count and link: PASS | FAIL | BLOCKED
  Step 3 "Trigger-Liste pruefen" with count and link: PASS | FAIL | BLOCKED
  Step 4 "Nacharbeit pruefen" with count and link: PASS | FAIL | BLOCKED
No buy/sell/live/broker wording on dashboard: PASS | FAIL | BLOCKED

/import loads without error: PASS | FAIL | BLOCKED
CSV-Arbeitsplan is the FIRST section after header: PASS | FAIL | BLOCKED
  Wochenupdate 1W card visible: PASS | FAIL | BLOCKED
  Tagesupdate 1D card visible: PASS | FAIL | BLOCKED
  Triggerupdate 4H card visible: PASS | FAIL | BLOCKED
Upload form below CSV-Arbeitsplan: PASS | FAIL | BLOCKED
Provider-Sync collapsed under "Provider-Sync (erweitert)": PASS | FAIL | BLOCKED
Provider-Sync expands on click: PASS | FAIL | BLOCKED
Import Readiness visible after file selection: PASS | FAIL | BLOCKED
Analyze-All section visible: PASS | FAIL | BLOCKED
Import History visible: PASS | FAIL | BLOCKED
No automatic/broker/live wording: PASS | FAIL | BLOCKED

/signals loads without error: PASS | FAIL | BLOCKED
Active Review Shortlist visible (primary): PASS | FAIL | BLOCKED
Trigger Radar visible (primary): PASS | FAIL | BLOCKED
Radar-Rangliste collapsed under "Radar-Rangliste (alle Signale)": PASS | FAIL | BLOCKED
Radar-Rangliste expands on click: PASS | FAIL | BLOCKED
Full signal list with filters visible when expanded: PASS | FAIL | BLOCKED
No buy/sell/live/broker wording: PASS | FAIL | BLOCKED
```

## Acceptance Criteria

- VPS health and web load pass: \_\_ (PASS | FAIL)
- Dashboard guided flow visible: \_\_ (PASS | FAIL)
- Import hierarchy matches v4.6 design: \_\_ (PASS | FAIL)
- Signals hierarchy matches v4.6 design: \_\_ (PASS | FAIL)
- Safety wording remains conservative: \_\_ (PASS | FAIL)
- Follow-up issues discovered: \_\_ (NOT NEEDED / see below)

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

- \#??: \_\_

# v4.7 Browser Workflow Smoke Checklist

## Purpose

This checklist validates the v4.6 guided workflow hierarchy in the browser. It
focuses on whether the new page structure makes the daily operator sequence
obvious before reading advanced or secondary sections.

This checklist is not trading advice, a live/realtime market-data claim,
production-readiness evidence, broker-readiness evidence, strategy-validation
evidence, profitability evidence, or approval for automatic execution.

Use `docs/BROWSER_SMOKE_EVIDENCE_FORMAT.md` for the canonical sanitized evidence
fields and forbidden evidence rules.

## Default Scope

Run locally first; VPS is optional after explicit approval.

Do not touch VPS, deployment state, `.env`, provider keys, secrets, DNS, Caddy,
Docker volumes, database backups, or private staging services unless the
owner/operator separately approves that exact operation.

## Preconditions

- Current branch is `main` with v4.6 changes merged (commits up to `193f02f`).
- The app can be built and accessed in a browser locally.
- Test data is public, synthetic, or redacted.
- Browser screenshots are optional and must not contain secrets, cookies, private
  symbols, account data, broker data, or private notes.
- No provider key, request URL, raw provider payload, `.env` value, cookie, database
  URL, or private trading data is copied into evidence.

## Dashboard `/` Validation

Validate the guided entry point.

```text
/ loads without error: PASS | FAIL | BLOCKED
"Heute starten" panel visible: PASS | FAIL | BLOCKED
  Step 1 "Daten pruefen" with count and link: PASS | FAIL | BLOCKED
  Step 2 "Aktive Kandidaten pruefen" with count and link: PASS | FAIL | BLOCKED
  Step 3 "Trigger-Liste pruefen" with count and link: PASS | FAIL | BLOCKED
  Step 4 "Nacharbeit pruefen" with count and link: PASS | FAIL | BLOCKED
No buy/sell/live/broker wording on dashboard: PASS | FAIL | BLOCKED
```

Expected operator interpretation:

- The panel guides the daily sequence before status cards.
- Each step links to the correct workflow page.

## `/import` Validation

Validate the restructured import hierarchy.

```text
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
Import History visible (below Analyze-All): PASS | FAIL | BLOCKED
No automatic analysis/signal/alert/trade/order wording: PASS | FAIL | BLOCKED
No live/realtime/provider-reliance claim: PASS | FAIL | BLOCKED
```

Expected operator interpretation:

- The CSV-Arbeitsplan is the first thing read, not hidden inside the form.
- Provider-Sync is intentionally secondary (collapsed).
- The upload form, Analyze-All, and History remain accessible.

## `/signals` Validation

Validate the restructured signals hierarchy.

```text
/signals loads without error: PASS | FAIL | BLOCKED
Active Review Shortlist visible (primary): PASS | FAIL | BLOCKED
  Cards show symbol, Ampel label, reason, action: PASS | FAIL | BLOCKED
Trigger Radar visible (primary): PASS | FAIL | BLOCKED
  Cards show symbol, proximity state, action: PASS | FAIL | BLOCKED
Radar-Rangliste collapsed under "Radar-Rangliste (alle Signale)": PASS | FAIL | BLOCKED
Radar-Rangliste expands on click: PASS | FAIL | BLOCKED
Full signal list with filters visible when expanded: PASS | FAIL | BLOCKED
No buy/sell/live/broker wording on signals page: PASS | FAIL | BLOCKED
```

Expected operator interpretation:

- Active Review and Trigger Radar are the primary daily worklists.
- The full list is intentionally secondary (collapsed).
- All signals remain accessible via the expandable section.

## Safety Wording Validation

Validate that no v4.6 change introduced unsafe wording.

```text
No "Kauf", "Verkauf", "Order", "Ausfuehrung" on dashboard: PASS | FAIL | BLOCKED
No "Live", "Echtzeit", "Realtime" claims on any page: PASS | FAIL | BLOCKED
No broker or automatic-execution wording: PASS | FAIL | BLOCKED
No profitability or strategy-validation claim: PASS | FAIL | BLOCKED
```

## Evidence Record

Record only sanitized evidence. For the canonical field list and forbidden
evidence policy, use `docs/BROWSER_SMOKE_EVIDENCE_FORMAT.md`.

| Check | Result | Notes |
|-------|--------|-------|
| Dashboard `/` | | |
| Import `/import` | | |
| Signals `/signals` | | |
| Safety wording | | |

Date: \_\_
Environment: \_\_ (local / VPS)
Branch/Commit: \_\_ (main at \_\_)
Screenshots attached: Yes / No (none contain secrets)
Follow-up issues needed: Yes / No (if Yes, list below)

## Follow-Up Issues

- \#??: \_\_

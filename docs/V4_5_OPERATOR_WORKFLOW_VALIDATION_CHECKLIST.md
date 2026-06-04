# v4.5 Operator Workflow Validation Checklist

## Purpose

This checklist validates the v4.4 practical operator workflow in a safe, repeatable
way. It focuses on whether the owner/operator can understand what to update and what
to review next.

This checklist is not trading advice, a live/realtime market-data claim,
production-readiness evidence, broker-readiness evidence, strategy-validation
evidence, profitability evidence, or approval for automatic execution.

## Default Scope

Default validation is local-only.

Do not touch VPS, deployment state, `.env`, provider keys, secrets, DNS, Caddy,
Docker volumes, database backups, or private staging services unless the
owner/operator separately approves that exact operation.

## Preconditions

- Current branch or commit is known.
- The app can be built locally, or a blocker is recorded.
- Test data is public, synthetic, or redacted.
- Browser screenshots are optional and must not contain secrets, cookies, private
  symbols, account data, broker data, or private notes.
- No provider key, request URL, raw provider payload, `.env` value, cookie, database
  URL, or private trading data is copied into evidence.

## `/import` Validation

Validate the CSV-first import workflow.

Record pass/fail/blocked only:

```text
/import loads: PASS | FAIL | BLOCKED
CSV-Arbeitsplan visible: PASS | FAIL | BLOCKED
Weekly universe guidance visible: PASS | FAIL | BLOCKED
Daily active-review guidance visible: PASS | FAIL | BLOCKED
Targeted 4H trigger guidance visible: PASS | FAIL | BLOCKED
CSV mapping table still manual: PASS | FAIL | BLOCKED
Import Readiness visible or empty-state understandable: PASS | FAIL | BLOCKED
Analyze-All wording manual-only: PASS | FAIL | BLOCKED
No automatic analysis/signal/alert/trade/order: PASS | FAIL | BLOCKED
No live/realtime/provider-reliance claim: PASS | FAIL | BLOCKED
```

Expected operator interpretation:

- `1W` is for weekly universe preparation.
- `1D` is for active review candidates.
- `4H` is for a small trigger shortlist.
- Import mapping remains manual and explicit.
- Analyze-All remains an intentional operator action.

Stop and file a follow-up if:

- The UI suggests refreshing all 200 symbols intraday.
- The UI implies live data or realtime trigger monitoring.
- Any copy sounds like a buy/sell/entry instruction.
- The workflow appears to create analysis, alerts, trades, orders, or broker actions
  automatically from import.

## `/signals` Validation

Validate the Active Review and Trigger Radar workflow.

Record pass/fail/blocked only:

```text
/signals loads: PASS | FAIL | BLOCKED
Active Review shortlist visible: PASS | FAIL | BLOCKED
Active Review reasons understandable: PASS | FAIL | BLOCKED
Active Review detail links visible: PASS | FAIL | BLOCKED
Trigger Radar visible: PASS | FAIL | BLOCKED
Trigger Radar workflow steps visible: PASS | FAIL | BLOCKED
At/Near/Far trigger counts visible: PASS | FAIL | BLOCKED
Trigger Radar capped worklist wording visible when applicable: PASS | FAIL | NOT APPLICABLE | BLOCKED
No buy/sell/entry wording: PASS | FAIL | BLOCKED
No automatic analysis/signal/alert/trade/order: PASS | FAIL | BLOCKED
```

Expected operator interpretation:

- Active Review is today's worklist, not a recommendation engine.
- Trigger Radar is a review-priority queue, not an execution queue.
- `Nah dran` and `Am Trigger` mean review stored context and refresh `4H` only when
  appropriate.
- Detail review is required before any external manual decision.

Stop and file a follow-up if:

- Active Review hides blockers that should remain visible.
- Trigger Radar encourages expanding the trigger list beyond practical size.
- Any UI copy implies orders, broker execution, live/realtime monitoring, or trading
  advice.

## Evidence Template

Use this template for #638 or later validation issues:

```text
Date:
Environment: local | private staging
Branch or commit:
Browser/viewport: desktop | mobile | not run
Data scope: public | synthetic | redacted | no data

/import loads:
CSV-Arbeitsplan visible:
Weekly universe guidance visible:
Daily active-review guidance visible:
Targeted 4H trigger guidance visible:
CSV mapping table still manual:
Import Readiness visible or empty-state understandable:
Analyze-All wording manual-only:

/signals loads:
Active Review shortlist visible:
Active Review reasons understandable:
Active Review detail links visible:
Trigger Radar visible:
Trigger Radar workflow steps visible:
At/Near/Far trigger counts visible:
Trigger Radar capped worklist wording visible when applicable:

No automatic analysis/signal/alert/trade/order:
No buy/sell/entry wording:
No live/realtime/provider-reliance claim:
Secrets/private data redacted:

Notes:
Follow-up needed: yes | no
Follow-up issue:
```

## Final Boundary

A passing v4.5 validation means only that the practical operator workflow is
understandable in the tested environment. It does not prove live data, realtime
signals, provider reliance, trading readiness, broker readiness, production readiness,
strategy validity, or profitability.

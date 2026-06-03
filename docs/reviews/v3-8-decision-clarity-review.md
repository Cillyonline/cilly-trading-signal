# v3.8 Decision Clarity Review

## Scope

Milestone: `v3.8 - Decision Clarity Radar`

Reviewed issues:

- #559 `web: add German signal decision model`
- #560 `web: redesign import analysis result as traffic-light decision card`
- #561 `web: turn signals page into radar-style overview`
- #562 `docs: document German decision labels and radar interpretation`

## Result

Status: PASS with one non-blocking follow-up.

The milestone delivered a reusable German decision layer and surfaced it on the
Import analysis result and Signals overview. The UI now prioritizes the operator
decision before technical backend fields:

- `Paper-Kandidat` / green
- `Beobachten` / yellow
- `Kein Trade` / red
- `Datenproblem` / gray

The wording remains decision-support only. No strategy scoring, backend trading
logic, broker integration, automatic order execution, or profitability claim was
introduced.

## Verification

- `npm run build` in `apps/web`: PASS
- PR #583 checks: PASS
- PR #584 checks: PASS
- PR #585 checks: PASS
- PR #586 checks: PASS
- Open PR review before this review: none
- v3.8 issue state before this review: #559-#562 closed, #563 open

## Review Checks

- Scope stayed within v3.8 issues: PASS
- Tests or explicit test gap documented: PASS
- Security impact considered: PASS
- Docs updated when behavior/workflow changed: PASS
- Trading logic checked against `docs/STRATEGY_AND_ALERTS.md`: PASS
- No automatic order execution language introduced: PASS
- No broker integration introduced: PASS
- No real-money or profitability claim introduced: PASS

## Findings

1. Non-blocking follow-up: Signal detail still presents the older technical-first
   detail layout. The list and import flow now have Ampel-first UX, but detail
   review would be more consistent if `/signals/[id]` reused the same decision
   model near the top of the page.

## Follow-Up Decision

Create one follow-up issue for Signal Detail decision-card consistency. This is
not a blocker for v3.8 because the primary radar and import decision workflows
are complete and documented.

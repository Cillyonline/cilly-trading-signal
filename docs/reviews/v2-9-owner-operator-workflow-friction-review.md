# v2.9 Owner/Operator Workflow Friction Review

## Purpose

This review records sample-only owner/operator workflow friction after the v2.9
current-state rebaseline. It is planning evidence for future polish only.

It is not a strategy validation, profitability claim, trading advice,
production-readiness statement, broker-readiness statement, live/realtime market
data claim, private-data approval, or approval for automatic execution.

## Review Scope

Date reviewed: 2026-06-02.

Evidence source: documentation walkthrough of the current owner/operator flow in
`docs/OWNER_OPERATOR_COCKPIT_MANUAL.md`, `docs/COCKPIT_REVIEW_WORKFLOW.md`, and
`docs/FINAL_BROWSER_CLICKTHROUGH_CHECKLIST.md`, supported by the v2.9 local
smoke evidence in `docs/MVP_SMOKE_TEST.md#v29-current-main-local-validation-evidence`.

Data scope: sample, synthetic, or paper workflow only. No private watchlists,
broker data, account data, fills, provider credentials, cookies, screenshots,
database dumps, raw logs, private notes, or production data were used.

Implementation scope: none. This review creates prioritization evidence only;
each accepted follow-up must be a separate issue and PR.

## Workflow Sequence Reviewed

| Step | Route or workflow | Review focus | Friction observed |
| --- | --- | --- | --- |
| 1 | `/login` | Single-admin entry and logout boundary | No immediate polish gap from docs. |
| 2 | `/` dashboard | Triage order and safety wording | Dashboard is broad; future review may need clearer next-best-action hierarchy after sample browser pass. |
| 3 | `/watchlist` | Symbol universe, data freshness, benchmark context | Data context is central but spread across Watchlist, import, and signal review. |
| 4 | `/screener` | Candidate import, review, explicit Watchlist conversion | Mobile density and candidate prioritization remain likely friction. |
| 5 | `/import` | Stored OHLCV import and analysis action | Operator must coordinate symbol/timeframe/sample fixtures manually. |
| 6 | `/signals` and `/signals/[id]` | Reviewable setup cards and detail reasoning | No new strategy gap; stale/missing context must remain visible stop points. |
| 7 | `/reviews` and `/reviews/[id]` | Batch evidence, repeated findings, follow-up drafts | Follow-up disposition is documented but not structured in-app. |
| 8 | `/trades` and `/trades/[id]` | Manual trade log, management, close, journal | Mobile grouping and distinction between routine management and final close remain likely friction. |
| 9 | `/performance` | R-multiple and risk review | Output is useful, but must continue to avoid forecast/profit framing. |
| 10 | `/alerts` | Alert event audit | No new polish gap from docs; keep Telegram/external delivery separately scoped. |
| 11 | `/settings` | Risk settings | No immediate polish gap from docs. |
| 12 | Logout | Protected-data boundary | No immediate polish gap from docs. |

## Top Friction Points

| Priority | Area | Severity | Friction | Proposed follow-up direction |
| --- | --- | --- | --- | --- |
| 1 | Review follow-up workflow | Medium | The docs now distinguish repeated patterns, dispositions, and follow-up status, but the app still relies on notes and manual draft text for disposition tracking. | Add a small review follow-up/disposition polish issue before considering automation. |
| 2 | Mobile Screener review | Medium | Screener candidates are safe and explicit, but dense candidate review and prioritization can be slow on mobile. | Add mobile Screener candidate density/prioritization polish scoped to UI only. |
| 3 | Mobile Trade workflow | Medium | Trade management, close documentation, and journal review are distinct concepts that can feel crowded in mobile review. | Add mobile Trade Detail grouping polish for management/close/journal sections. |
| 4 | Data-context handoff | Low | Watchlist, Import, and Signals all carry parts of freshness/source/benchmark context; the operator must mentally stitch them together. | Consider a later docs/UI copy issue after browser walkthrough confirms actual friction. |
| 5 | Browser clickthrough evidence | Low | Current v2.9 validation covered stack/API/web load but not the visual browser checklist. | Keep as operator-run evidence; do not automate until the dry-run contract is implemented in a separate approved issue. |

## Accepted For Next Prioritization

- Review follow-up/disposition workflow polish.
- Mobile Screener candidate review polish.
- Mobile Trade Detail workflow grouping polish.

These should become small, template-conformant follow-up issues only if accepted
in the v2.9 prioritization issue. They should not include strategy rule changes,
private data, browser automation, broker integration, production-like exposure,
profitability claims, or automatic execution.

## Deferred

- Data-context handoff UI changes are deferred until a real sample browser
  walkthrough confirms the friction in the app, not just in docs.
- Browser smoke automation remains deferred. The safe dry-run contract exists, but
  implementation would require a separate issue, explicit scope, and dependency
  review.

## Safety Review

- `No Trade`, stale data, failed/partial/unknown provider state, missing context,
  ignored screener candidates, and unclear review outcomes remain valid stop
  points.
- Follow-up findings are planning evidence only and do not request automatic rule
  changes.
- No private data, secrets, logs, cookies, screenshots, provider payloads, broker
  data, or account data are included.
- No finding implies production readiness, real-money readiness, profitability,
  broker readiness, live/realtime data, trading advice, or automatic execution.

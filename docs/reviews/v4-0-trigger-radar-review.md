# v4.0 Trigger Radar Review

Date: 2026-06-04

Scope: Review v4.0 trigger proximity logic, Signals-page Trigger Radar UI,
trigger/alert interpretation docs, safety wording, and follow-up planning.

## Summary

v4.0 adds a conservative trigger-review layer without adding execution behavior.
The backend can classify trigger proximity from stored candles for analysis
responses, the Signals page now exposes a German Trigger Radar section for manual
review prioritization, and the docs explicitly define trigger/alert states as
review prompts rather than buy/sell instructions.

The milestone is directionally sound and remains inside decision-support
boundaries. The largest gap is that backend-calculated trigger proximity is not
yet exposed through Signal list/detail endpoints, so the current Signals-page
Trigger Radar uses stored signal status and trigger levels as a conservative UI
proxy until the signal-read API is extended.

## Evidence

- #571 / PR #600 added deterministic analysis-response proximity states:
  `not_available`, `far_from_trigger`, `near_trigger`, and `at_trigger`.
- #571 keeps No-Trade/No-Setup, missing trigger data, and unavailable trigger
  context at `not_available`.
- #571 documented stored-data-only trigger proximity in `docs/STRATEGY_AND_ALERTS.md`.
- #572 / PR #601 added a German Trigger Radar section to `/signals`.
- #572 excludes No-Trade, data-problem, stale, and missing-trigger signals from
  Trigger Radar promotion.
- #573 / PR #602 documented Trigger Radar and alert interpretation policy across
  strategy, review workflow, owner/operator manual, and roadmap docs.

## Review Findings

No release-blocking defects were found in the merged v4.0 scope.

Important non-blocking gaps:

- The Web Trigger Radar cannot yet consume backend-calculated `trigger_proximity_state`
  from `GET /signals` or `GET /signals/{id}`. It currently uses a conservative
  status-derived proxy. This is acceptable for v4.0 review, but should be closed
  before relying on Trigger Radar as the primary trigger-ranking surface.
- Target-environment browser evidence is still needed after an approved VPS update.
  CI and local checks passed, but the operator-facing workflow should be smoked on
  the private VPS before calling it operationally validated.
- There is no Telegram routing in v4.0. That is intentional; alert wording is
  policy-only and should not be interpreted as delivery implementation.

## Safety Boundaries Checked

- No automatic order execution was added.
- No broker integration was added.
- No Telegram routing was added.
- No automatic trade creation was added.
- No live/realtime data claim was added; trigger proximity is based on stored data.
- No profitability claim or buy/sell instruction language was added.
- No-Trade, No-Setup, data-problem, stale, and missing-trigger states remain
  conservative blockers rather than trigger candidates.

## Follow-Up Issues

Created from this review:

- #603 `api: expose trigger proximity on signal read endpoints` - priority p1.
- #604 `web: use backend trigger proximity in Trigger Radar` - priority p1.
- #605 `review: VPS smoke trigger radar after next deployment` - priority p2.

Recommended order:

1. Complete #603 so signal reads expose the backend-calculated state.
2. Complete #604 so the UI uses that state instead of status-derived labels.
3. Complete #605 after the next approved VPS deployment.

## Verification

- `git diff --check -- docs/reviews/v4-0-trigger-radar-review.md docs/DELIVERY_ROADMAP.md`

Skipped:

- Frontend and backend builds were not run for this review-only documentation
  change. The implementation PRs documented their relevant checks and passed CI.

## Decision

v4.0 is conservative enough to proceed, provided follow-ups #603 and #604 are
handled before treating Trigger Radar as fully aligned with backend proximity
logic. A controlled VPS smoke should follow the next approved deployment.

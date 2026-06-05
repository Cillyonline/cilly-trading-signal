# v4.6 Guided Operator Workflow Decision

Date: 2026-06-05

## Decision

v4.6 will make the cockpit easier to use by turning the current CSV-first workflow
into a guided daily operator flow.

The problem is not missing functionality. The current cockpit has the right building
blocks, but too many panels compete for attention. The next increment should make the
operator's path obvious before adding browser smoke or new product surface area.

## Goal

The operator should be able to answer these questions in the first 10 seconds:

- What needs attention today?
- Which data should be refreshed first?
- Which symbols are active review candidates?
- Which symbols are trigger candidates?
- Where do I go next?

## Guided Flow

The intended flow is:

1. Dashboard: start with `Heute starten`.
2. Import: choose the update mode before reading technical details.
3. Signals: review Active Review before the full signal list.
4. Trigger Radar: keep a small focused trigger worklist.
5. Detail pages: inspect full context only after a symbol is relevant.

## Page Hierarchy

### Dashboard

Primary:

- `Heute starten` with a clear sequence:
  1. Daten pruefen.
  2. Aktive Kandidaten pruefen.
  3. Trigger-Liste pruefen.
  4. Manuelle Nacharbeit pruefen.
- Each step should show a concise count, a practical next action, and one link.

Secondary:

- Broad status cards.
- Market data quality details.
- Cockpit snapshot.

### `/import`

Primary:

- CSV-first update modes:
  - `Wochenupdate 1W` for universe preparation.
  - `Tagesupdate 1D` for active review candidates.
  - `Triggerupdate 4H` for the small trigger shortlist.
- CSV upload and mapping.
- Import Readiness and Analyze-All guidance.

Secondary or advanced:

- Provider sync.
- Provider sync result.
- Import history.

### `/signals`

Primary:

- `Heute pruefen` / Active Review shortlist.
- Trigger Radar as the focused trigger worklist.

Secondary or advanced:

- Full Radar-Rangliste.
- Filters.
- Technical card details.

## Progressive Disclosure Rules

- Start with task intent, then show details.
- Put common daily actions above diagnostics and history.
- Keep advanced/provider/history sections available but visually secondary.
- Prefer one clear next action per workflow card.
- Avoid showing every available metric as equal priority.

## Wording Rules

Use operator workflow language:

- `Pruefen`
- `Aktualisieren`
- `Datenproblem beheben`
- `Detail pruefen`
- `Beobachten`

Avoid execution language:

- No buy/sell wording.
- No entry instruction wording.
- No live/realtime claim.
- No broker/order wording except to state that it does not exist.

## v4.6 Work Package

Planned issues:

- #643: define this guided operator workflow decision.
- #644: add the Dashboard `Heute starten` workflow panel.
- #645: simplify `/import` workflow hierarchy.
- #646: simplify `/signals` workflow hierarchy.
- #647: update operator guides for guided workflow.
- #648: review v4.6 and decide whether a gap issue is needed.

Recommended order:

1. Decision record.
2. Dashboard guided entry point.
3. Import hierarchy.
4. Signals hierarchy.
5. Operator docs.
6. Review and gap decision.

## Safety Boundaries

- No broker integration.
- No automatic order execution.
- No automatic trade creation.
- No automatic analysis, signal, or alert creation from workflow guidance.
- No provider expansion.
- No scheduler-driven market-data sync.
- No live/realtime market-data claim.
- No production-readiness, strategy-validation, or profitability claim.
- No secrets, `.env` values, provider keys, request URLs, raw payloads, private
  watchlists, cookies, broker data, account data, or fill data should be recorded in
  evidence.

## Done Criteria

v4.6 is done when:

- Dashboard gives a clear daily starting point.
- `/import` makes the intended update mode clear before advanced sections.
- `/signals` makes Active Review and Trigger Radar primary.
- Full lists, history, provider sync, and diagnostics remain available but secondary.
- Operator docs match the implemented flow.
- Review confirms whether a follow-up gap issue is needed.

## Implementation Notes

- #644 adds `Heute starten` above the broad Dashboard status cards so the operator
  sees the workflow order before diagnostics.

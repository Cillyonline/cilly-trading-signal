# v6.2 Next Increment Decision

Date: 2026-06-24

## Decision

Select `v6.3 - Paper Workflow Usage Polish` as the recommended next milestone.

The next increment should improve the existing sample/paper-only manual workflow
without expanding operational, private-data, provider, broker, automation,
production-readiness, profitability, or strategy-validation scope.

## Current State

- v5.9 completed the safe manual paper-trade path from signal review to trade
  logging, management, journal guidance, and paper-performance boundaries.
- v6.0 documented private-staging deploy and migration recovery posture.
- v6.1 kept offsite encrypted backup and restore drill deferred for the current
  sample/paper-only private-staging scope.
- v6.2 rebaselined the roadmap after v6.1 and is selecting the next scoped
  implementation increment.

Private trading data remains No-Go. Backup/restore implementation remains
deferred. Production-like or public exposure remains blocked by separate monitoring,
backup, incident, security, privacy, and owner-acceptance gates.

## Candidate Comparison

| Candidate | Decision | Rationale |
| --- | --- | --- |
| Paper Workflow Usage Polish | Selected | Safest small product increment. It builds on v5.9, improves daily sample/paper usability, and does not require private trading data, provider smokes, VPS changes, backup/restore, production claims, or trading-logic changes. |
| Monitoring/Incident Decision Gate | Deferred | Useful later, but higher operations scope than needed while the app remains private sample/paper-only and backup/restore is still deferred. |
| Review Calibration Follow-up | Deferred | No fresh sample/paper evidence currently shows concrete signal-quality or review-calibration gaps requiring strategy-rule work. |
| Private Data Gate | Not selected | Private trading data remains No-Go, and backup/restore remains deferred. Selecting this now would skip required safety gates. |
| Backup/Restore Implementation | Not selected | v6.1 deliberately deferred offsite backup and restore drill. Implementation requires explicit owner/operator reopening as a separate operations gate. |
| Production-Like/Public Exposure | Not selected | Requires monitoring, backup, incident, security, privacy, and owner-acceptance evidence that does not exist yet. |

## Recommended v6.3 Scope

`v6.3 - Paper Workflow Usage Polish` should stay small and focus on sample/paper
workflow clarity:

- Clarify paper-workflow next actions across the existing signal, trade, and
  performance pages where operators make manual decisions.
- Improve empty, boundary, or checklist copy that helps the operator understand
  what to do next with paper-only data.
- Keep all trade creation, trade updates, journal entries, and close events manual.
- Add or update tests only for UI behavior or copy that affects route output.
- Record a short review at milestone closure.

## Explicit Boundaries

v6.3 must not include:

- Private trading data approval.
- Offsite backup repository setup, backup credentials, Restic commands, or restore
  drills.
- Provider smoke, provider-key handling, secret rotation, VPS changes, or scheduler
  work.
- Production-readiness, public exposure, incident-response implementation, or
  monitoring implementation claims.
- Broker integration, account sync, automatic order execution, automatic trade
  creation, automatic position sizing, or automatic trade management.
- Live/realtime market-data claims.
- Profitability, predictive, strategy-validation, backtesting, or real-money
  readiness claims.
- Trading-rule, scoring, or calibration changes unless a later issue explicitly
  documents concrete sample/paper evidence requiring that work.

## Follow-Up Tracker Decision

Created milestone #75, `v6.3 - Paper Workflow Usage Polish`, with scoped follow-up
issues:

- #811: roadmap rebaseline for v6.3.
- #808: signal-to-paper next-action polish.
- #807: manual trade logging and management polish.
- #809: paper performance review polish.
- #806: sample/paper workflow validation.
- #810: milestone review.

The follow-up issues should use the repository issue template and preserve the
same safety boundaries.

## Verification

- Roadmap and recent decision docs reviewed.
- Open GitHub tracker reviewed: only #803 and #804 remain open in v6.2 after #802
  closure.
- Follow-up milestone #75 and issues #806 through #811 created for v6.3.
- This is a documentation and tracker decision only; application builds/tests are
  not required for behavior coverage.

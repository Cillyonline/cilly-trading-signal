# v6.2 Roadmap Rebaseline and Next Increment Selection Review

## Scope

This review closes the v6.2 roadmap rebaseline and next-increment selection
milestone. The milestone aligned roadmap docs after the v6.1 backup/restore
deferral and selected the next safe implementation milestone.

This review is not private trading data approval, backup/restore implementation,
production readiness, live/realtime market-data evidence, broker readiness,
profitability evidence, strategy validation, trading advice, real-money readiness,
or approval for automatic execution.

## Tracker Review

| Issue | Status | PR | Outcome |
| --- | --- | --- | --- |
| #802 `docs: rebaseline roadmap after v6.1 closure` | Closed | #805 | Roadmap docs were rebaselined after v6.1 and v6.2 was set as the active milestone. |
| #803 `docs: decide next increment after backup restore deferral` | Closed | #812 | `v6.3 - Paper Workflow Usage Polish` was selected and follow-up milestone/issues were created. |
| #804 `review: v6.2 roadmap and next increment selection` | In review | This PR | Milestone review and closure decision. |

## Completed Items

- `docs/NEXT_MILESTONE_DECISION.md`, `docs/DELIVERY_ROADMAP.md`, and
  `docs/PRODUCT_ROADMAP.md` no longer present v6.1 as the active next milestone.
- `docs/V6_2_NEXT_INCREMENT_DECISION.md` records the candidate comparison and
  selected next increment.
- Milestone #75, `v6.3 - Paper Workflow Usage Polish`, was created.
- v6.3 follow-up issues were created:
  - #811: roadmap rebaseline for v6.3.
  - #808: signal-to-paper next-action polish.
  - #807: manual trade logging and management polish.
  - #809: paper performance review polish.
  - #806: sample/paper workflow validation.
  - #810: milestone review.

## Decision Summary

Selected next milestone: `v6.3 - Paper Workflow Usage Polish`.

Rationale: this is the smallest safe implementation increment after v6.1. It builds
on the existing v5.9 sample/paper-only workflow and improves daily usability without
requiring private trading data, backup/restore, provider smoke, VPS changes,
production-readiness work, broker integration, automatic trade behavior, or trading
logic changes.

## Deferred Or Not Selected

- Private Data Gate: not selected because private trading data remains No-Go and
  backup/restore remains deferred.
- Backup/Restore Implementation: not selected because v6.1 explicitly deferred it;
  reopening requires a separate owner/operator operations gate.
- Production-like/Public Exposure: not selected because monitoring, backup,
  incident, security, privacy, and owner-acceptance gates are not complete.
- Monitoring/Incident Decision Gate: deferred as useful later but broader than the
  current sample/paper-only next increment requires.
- Review Calibration Follow-up: deferred because no fresh sample/paper evidence
  shows concrete signal-quality or review-calibration gaps.

## Validation Summary

- PR #805 CI: initially blocked by GitHub account billing/spending-limit before jobs
  could start; after the account-side blocker was resolved, PR #805 merged.
- PR #805 also reduced redundant Actions usage by path-limiting post-merge `main`
  push runs and adding workflow concurrency.
- Local CLI checks during the #805 blocker review:
  - `apps/web`: `npm run build` passed.
  - `apps/api`: Ruff passed from a temporary Python 3.12 test environment.
  - `apps/api`: Pytest passed, `409 passed, 17 warnings`.
  - `git diff --check` passed.
  - Local Alembic was blocked by local PostgreSQL authentication and no running
    Docker daemon; CI later covered required checks once GitHub Actions was usable.
- PR #812 CI: pass for API lint/tests, Web build, Dependency visibility, and
  Container visibility.

## Follow-Up Items

- Start v6.3 with #811 after this v6.2 review merges and the v6.2 milestone closes.
- Keep backup/restore implementation deferred unless explicitly reopened as a
  separate operations gate.
- Keep review calibration deferred unless fresh sample/paper validation identifies
  concrete signal-quality or review-calibration gaps.

## Boundary Review

- No broker integration was added.
- No automatic order execution was added.
- No automatic trade creation was added.
- No private trading data approval was added.
- No backup repository, backup credentials, Restic command, restore drill, secret
  rotation, provider smoke, VPS change, or production-readiness work was performed
  by v6.2.
- No private records, secrets, provider keys, database dumps, raw payloads, or
  sensitive screenshots were included in shared evidence.
- No profitability, predictive, strategy-validation, live/realtime, real-money
  readiness, broker-readiness, or production-readiness claim is made by this review.

## Closure Decision

v6.2 is closure-ready after this review PR merges. The roadmap state is aligned,
the next increment is selected, follow-up milestone #75 and issues #806 through
#811 exist, and there are no unresolved v6.2 blockers.

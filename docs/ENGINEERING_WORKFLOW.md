# Engineering Workflow

## Goal

Work should move through small, reviewable increments. Every meaningful change starts with a GitHub issue, is implemented on a branch, verified by checks, reviewed in a pull request, and only then merged into `main`.

## Issue Standard

Every issue should use the same structure:

- Goal: the outcome to deliver.
- Context: why this matters now and which docs/decisions apply.
- IN SCOPE: what is included.
- OUT OF SCOPE: what is explicitly excluded. This is mandatory.
- Acceptance Criteria: observable done checks.
- Test Requirements: expected automated or manual verification.
- Files Allowed To Change: explicit file or directory boundaries for the implementation.
- Files NOT Allowed To Change: files or areas that must remain untouched.
- Review Checks: what reviewers must inspect.
- Notes / Risks: optional known risks, assumptions, or follow-ups.

## Labels

Use a small label set so the board stays readable:

- Type: `type:feature`, `type:bug`, `type:chore`, `type:docs`, `type:test`
- Area: `area:web`, `area:api`, `area:infra`, `area:docs`, `area:trading-logic`, `area:workflow`
- Priority: `priority:p0`, `priority:p1`, `priority:p2`, `priority:p3`
- Status: `status:blocked`, `status:needs-review`

Avoid adding labels unless they improve planning or review decisions.

## Milestones And Versions

Use release-oriented milestones, not one milestone per task:

- `v0.1 - Foundation`: workflow, CI, local setup, data model, migrations.
- `v0.2 - MVP Data Flow`: watchlist, CSV import, indicators.
- `v0.3 - MVP Signal Flow`: signal engine, signal cards, manual trade logging basics.

Version numbers represent product maturity, not marketing releases.

## Branches

Create one branch per issue:

```text
issue-<number>-short-description
```

Examples:

```text
issue-3-ci-quality-checks
issue-5-watchlist-mvp-slice
```

## Pull Requests

Every pull request should include:

- linked issue
- summary of changes
- verification commands and results
- known risks or follow-ups
- screenshots for UI changes when useful

## Review Gates

Before merge:

- CI must pass or failures must be explicitly justified.
- Scope must match the issue.
- Security impact must be considered.
- Tests must be added or a test gap must be documented.
- Trading logic must be checked against `docs/STRATEGY_AND_ALERTS.md` when relevant.

## Trading Logic Review

Trading-related changes are treated conservatively:

- No automatic order execution.
- No profitability claims.
- Signals are decision support only.
- Prefer `No Trade` over weak or unexplained signals.
- Every signal must include clear reasoning, risk flags, stop, target, and R:R when applicable.
- No-Trade rules must be reviewed as first-class behavior, not edge cases.

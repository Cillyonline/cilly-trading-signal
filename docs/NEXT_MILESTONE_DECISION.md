# Next Milestone Decision

Date: 2026-06-04

## Decision

Recommended next milestone: `v4.6 - Browser Workflow Smoke`.

Rationale: v4.5 Operator Workflow Validation is complete with local build and
checklist evidence. The remaining validation gap is optional authenticated browser
smoke of `/import` and `/signals`, local by default and VPS-only after explicit
approval.

## v4.3 - Operational Evidence Closure

Goal: close the remaining operator-run provider evidence gap without expanding
product scope.

Status: Done.

Primary items:

- #614: Provider Daily/EOD smoke after explicit provider-key approval is recorded in
  `docs/reviews/v4-3-provider-daily-eod-smoke.md`. The configured provider path
  reached Alpha Vantage and failed safely with sanitized `provider_rate_limited`
  evidence.

Already closed:

- #605: Trigger Radar VPS smoke after approved deployment passed and is recorded in
  `docs/reviews/v4-2-vps-trigger-radar-smoke.md`.

Done when:

- Evidence is sanitized and references commit, environment class, pass/fail status,
  and issue links only.
- No secrets, provider keys, request URLs, cookies, `.env` values, database URLs,
  private symbols, or broker/account data are recorded.
- No production-readiness, live/realtime, broker-readiness, strategy-validation,
  profitability, or automatic-execution claim is introduced.

## v4.4 - Practical Operator Workflow

Goal: make daily use practical without paid provider reliance.

Status: Done. Review is recorded in
`docs/reviews/v4-4-practical-operator-workflow-review.md`.

Decision:

- TradingView CSV remains the operational baseline for `1W`, `1D`, and `4H`.
- Alpha Vantage remains optional guarded Daily/EOD smoke only.
- Broad provider reliance is deferred because provider budget is 0 EUR and the
  configured Alpha Vantage smoke failed safely with `provider_rate_limited`.
- Daily work should focus on a universe, active review shortlist, and trigger
  shortlist instead of updating about 200 symbols multiple times per day.

Planned issues:

- #625: record the practical operator workflow decision.
- #626: add a daily and weekly operator playbook.
- #627: add trigger-focused Import page guidance.
- #628: add an active review shortlist.
- #629: improve Trigger Radar operator workflow.

Decision record:

- `docs/V4_4_PRACTICAL_OPERATOR_WORKFLOW_DECISION.md`

## v4.5 - Operator Workflow Validation

Goal: validate the practical owner/operator workflow in the browser after the v4.4
changes.

Status: Done. Review is recorded in
`docs/reviews/v4-5-operator-workflow-validation-review.md`.

Recommended scope:

- Browser smoke `/import` CSV-Arbeitsplan, Import Readiness, and Analyze-All guidance.
- Browser smoke `/signals` Active Review shortlist and Trigger Radar worklist.
- Record sanitized pass/fail evidence only.
- File focused follow-up issues only for observed workflow blockers.

Checklist:

- `docs/V4_5_OPERATOR_WORKFLOW_VALIDATION_CHECKLIST.md`

Default if no explicit deployment approval is given:

- Run local/browser validation only.
- Do not touch VPS, secrets, `.env`, provider keys, or deployment state.

## v4.6 - Browser Workflow Smoke

Goal: run authenticated browser validation of the v4.4/v4.5 workflow when the
operator wants visual/runtime assurance.

Recommended scope:

- Local browser smoke of `/import` CSV-Arbeitsplan and Import Readiness.
- Local browser smoke of `/signals` Active Review and Trigger Radar.
- Mobile and desktop viewport checks when feasible.
- Sanitized pass/fail evidence only.

Default boundary:

- Keep validation local unless the owner/operator explicitly approves private VPS
  deployment/update steps.
- Do not add provider reliance, broker integration, automatic execution, or
  live/realtime claims.

## Not Now

- Broker integration.
- Automatic order execution.
- Automatic trade creation.
- Public SaaS or multi-user operation.
- Live/realtime market-data claims.
- Backtesting or profitability validation claims.

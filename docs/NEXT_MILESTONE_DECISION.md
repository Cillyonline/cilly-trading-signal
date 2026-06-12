# Next Milestone Decision

Date: 2026-06-12

## Decision

Recommended next milestone: `v5.4 - Roadmap Rebaseline After Provider Smoke`.

Rationale: v4.9 through v5.3 are complete and closed. Twelve Data now has local
operator-run configured-provider smoke evidence for guarded manual `1W`, `1D`,
and `4H` stored-data sync. The next highest-value step is to rebaseline roadmap
docs and tracker state before choosing the next implementation milestone.

Recommended implementation sequence after v5.4:

1. `v5.5 - Provider Operational Hardening`: plan and harden operator-facing
   provider limits, entitlement/rate-limit handling, symbol-scope guidance, and
   fallback wording without scheduler-driven sync or production-like reliance.
2. `v5.6 - Operator Data Refresh Workflow`: improve the manual provider/CSV
   refresh flow only if v5.5 confirms clear, safe scope.
3. `v5.7 - Review Calibration Follow-up`: add deterministic review/golden-case
   coverage only if fresh operator evidence shows signal-quality gaps.

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

## v4.6 - Guided Operator Workflow

Goal: make the CSV-first cockpit easier to use by guiding the operator through the
daily review sequence.

Status: Done. Review is recorded in
`docs/reviews/v4-6-guided-operator-workflow-review.md`.

Decision record:

- `docs/V4_6_GUIDED_OPERATOR_WORKFLOW_DECISION.md`

## v4.7 - Browser Workflow Smoke

Goal: validate the v4.6 guided workflow changes in the browser with a focused smoke
test.

Status: Done. VPS browser smoke evidence is recorded in
`docs/reviews/v4-7-vps-browser-workflow-smoke.md`.

Scope completed:

- Browser smoke `/import` CSV-Arbeitsplan placement, Provider-Sync collapse, and
  Analyze-All behavior.
- Browser smoke `/signals` Active Review, Trigger Radar, and collapsed
  Radar-Rangliste.
- Browser smoke Dashboard `Heute starten` panel and guided flow.
- Record sanitized pass/fail evidence only.
- File focused follow-up issues only for observed workflow blockers.

Decision record:

- `docs/V4_6_GUIDED_OPERATOR_WORKFLOW_DECISION.md`

Default boundary:

- Do not add provider reliance, broker integration, automatic execution, or
  live/realtime claims.
- Use the existing local/staging environment; no VPS or deployment changes without
  explicit approval.

## v4.8 - Guided First Run & Data Hygiene

Goal: make the app easier for a new operator by guiding first-run setup, asset
addition, data readiness, safe cleanup, and result interpretation.

Status: Done. Completion review is recorded in
`docs/reviews/v4-8-guided-first-run-data-hygiene-review.md`.

Completed issues:

- #667: add guided first-run workflow across Watchlist, Import, and Signals.
- #668: add beginner help panels for adding assets cleanly.
- #669: add data hygiene overview for each symbol.
- #670: add safe cleanup actions for watchlist data.
- #671: add plain-language explanations for signal result states.

Boundary:

- No trading logic, broker behavior, provider automation, scheduler, automatic
  execution, live/realtime claim, profitability claim, or production-readiness
  claim was introduced.

## v4.9 - Roadmap Rebaseline & Tracker Hygiene

Goal: align roadmap docs and tracker state after v4.7/v4.8 before starting the
next implementation work.

Status: Done. Review is recorded in
`docs/reviews/v4-9-roadmap-rebaseline-tracker-hygiene-review.md`.

Completed issues:

- #673: rebaseline roadmap after v4.7 and v4.8.
- #674: confirm completed v4.6 and v4.8 milestones are closed.
- #675: record v4.8 guided first-run completion.

Tracker hygiene snapshot, 2026-06-11:

- `v4.6 - Guided Operator Workflow`: closed, 0 open issues, 6 closed issues.
- `v4.8 - Guided First Run & Data Hygiene`: closed, 0 open issues, 5 closed issues.

Completion criteria:

- Roadmap docs no longer present completed v4.7/v4.8 work as pending.
- Completed milestones are closed in the tracker.
- The next implementation milestones are explicit.

## v5.0 - Twelve Data Provider Readiness

Goal: consolidate Twelve Data as the selected clean manual provider path and
harden provider configuration before relying on provider-backed stored data.

Status: Done. Review is recorded in
`docs/reviews/v5-0-twelve-data-provider-readiness-review.md`.

Completed issues:

- #676: limit configurable market data providers to implemented adapters.
- #677: clarify Twelve Data as selected clean provider path.
- #678: cover unsupported provider configuration behavior.
- #679: record Twelve Data provider smoke checklist result as `NOT RUN` with a
  follow-up to run the configured provider smoke after explicit approval.

Boundary:

- No scheduler, broker integration, automatic execution, live/realtime claim,
  profitability claim, or production-readiness claim.

## v5.1 - Local Verification Reliability

Goal: make local backend/frontend verification reproducible and aligned with CI.

Status: Done. Review is recorded in
`docs/reviews/v5-1-local-verification-reliability-review.md`.

Completed issues:

- #680: document `uv` setup and backend verification path.
- #681: add Python 3.12 and `uv` troubleshooting for Windows.
- #684: align local backend commands with CI expectations.

## v5.2 - Safe Browser Smoke Automation

Goal: evaluate and implement safe sample-only browser smoke automation under the
documented dry-run contract.

Status: Done. Review is recorded in
`docs/reviews/v5-2-safe-browser-smoke-automation-review.md`.

Completed issues:

- #682: add safe browser smoke dry-run implementation.
- #683: evaluate browser smoke CI versus manual runner.
- #685: record browser smoke evidence format.

Boundary:

- No VPS secret automation, provider-key automation, private-data use, broker
  integration, automatic execution, live/realtime claim, or production-readiness
  claim.

## v5.3 - Operator Provider Smoke

Goal: run the configured Twelve Data provider smoke after explicit key/setup
approval and record sanitized evidence.

Status: Done. Review is recorded in
`docs/reviews/v5-3-operator-provider-smoke-review.md`.

Completed issues:

- #695: run configured Twelve Data provider smoke after explicit approval.
- #709: review v5.3 operator provider smoke.

Outcome:

- Local Docker Compose smoke passed for Twelve Data `1W`, `1D`, and `4H` guarded
  manual stored-data sync.
- Evidence is recorded in `docs/reviews/v5-3-twelve-data-provider-smoke.md`.
- A follow-up `1D` sync did not create automatic signals, trades, or alerts.
- TradingView CSV remains the fallback.

Boundary:

- The smoke is local operator evidence only. It is not production-readiness,
  live/realtime, broker-readiness, profitability, strategy-validation, trading
  advice, or approval for automatic execution.

## v5.4 - Roadmap Rebaseline After Provider Smoke

Goal: align roadmap docs, product status, provider docs, and tracker state after
v5.0-v5.3 completion.

Status: Current.

Planned issues:

- #711: rebaseline next milestone decision after v5.3.
- #712: update delivery and product roadmap status after v5.3.
- #713: align provider docs with v5.3 smoke status.
- #714: review v5.4 roadmap rebaseline after provider smoke.

Done when:

- Roadmap docs no longer present v4.9-v5.3 work as pending.
- Provider docs consistently state local Twelve Data smoke status and remaining
  reliance boundaries.
- Tracker state is aligned and v5.4 is reviewed/closed.

## Next Implementation Candidates

Recommended candidate after v5.4:

- `v5.5 - Provider Operational Hardening`: clarify and harden the operator-facing
  provider path after local Twelve Data smoke. Likely scope includes symbol/asset
  guidance, entitlement/rate-limit failure wording, fallback instructions, and
  evidence requirements. It must not add scheduler-driven sync, automatic
  analysis, broker integration, automatic execution, live/realtime claims, or
  production-readiness claims.

Deferred candidates:

- Data-refresh workflow polish if operator use shows friction after v5.5 planning.
- Additional deterministic review calibration if fresh paper/operator evidence
  identifies signal-quality gaps.
- Production-like readiness hardening only after a separate explicit gate.

## Not Now

- Broker integration.
- Automatic order execution.
- Automatic trade creation.
- Public SaaS or multi-user operation.
- Live/realtime market-data claims.
- Backtesting or profitability validation claims.

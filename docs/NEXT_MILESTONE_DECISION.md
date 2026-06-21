# Next Milestone Decision

Date: 2026-06-21

## Decision

Recommended active milestone: `v6.1 - Backup & Restore Decision Gate`.

Rationale: v4.9 through v6.0 are complete and closed. Private trading data remains
No-Go after v5.8, while private staging is validated for sample/paper-only use and
now has documented deploy/migration recovery guidance. Offsite encrypted backup and
restore drill remain deferred from v5.8. The next highest-value increment is a
deliberate backup/restore decision gate before broader staging reliance or any
private-data readiness discussion.

Recommended implementation sequence after v6.0:

1. `v6.1 - Backup & Restore Decision Gate`: rebaseline roadmap docs, decide
   whether encrypted offsite backup and restore drill remain deferred or become
   the next explicit operations gate, record the outcome, and close the milestone.
2. If backup/restore becomes the next gate, create separate scoped implementation
   issues before performing any backup repository, secret, or restore operation.
3. Keep review calibration deferred unless fresh sample/paper operator evidence
   shows concrete signal-quality or review-calibration gaps.

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

Status: Done. Review is recorded in
`docs/reviews/v5-4-roadmap-rebaseline-after-provider-smoke-review.md`.

Completed issues:

- #711: rebaseline next milestone decision after v5.3.
- #712: update delivery and product roadmap status after v5.3.
- #713: align provider docs with v5.3 smoke status.
- #714: review v5.4 roadmap rebaseline after provider smoke.

Done when:

- Roadmap docs no longer present v4.9-v5.3 work as pending.
- Provider docs consistently state local Twelve Data smoke status and remaining
  reliance boundaries.
- Tracker state is aligned and v5.4 is reviewed/closed.

## v5.5 - Provider Operational Hardening

Goal: harden the operator-facing Twelve Data provider path after local v5.3
smoke without expanding provider automation or reliance claims.

Status: Done. Review is recorded in
`docs/reviews/v5-5-provider-operational-hardening-review.md`.

Completed issues:

- #719: define Twelve Data symbol and asset scope guidance.
- #720: harden sanitized provider failure guidance.
- #721: clarify provider sync fallback guidance on the Import page.
- #722: define provider operational evidence format.
- #723: cover provider sync hardening boundaries.
- #724: review v5.5 provider operational hardening.

Outcome:

- Twelve Data symbol/asset scope guidance is documented for public/sample symbols,
  mapping-sensitive assets, entitlement uncertainty, and CSV fallback.
- API provider failures use sanitized operator-actionable messages.
- Import page provider-sync failures, partials, skips, rate limits, and entitlement
  outcomes point back to manual recovery and TradingView CSV fallback.
- Tests assert manual provider sync does not automatically create signals, trades,
  alerts, or notification logs.
- Provider operational evidence rules explicitly forbid secrets, raw payloads,
  request URLs, private symbols, provider account details, and readiness overclaims.

Boundary:

- No scheduler-driven sync, automatic refresh, automatic analysis, broker
  integration, automatic execution, live/realtime claim, profitability claim, or
  production-readiness claim was introduced.

## v5.6 - Operator Data Refresh Workflow

Goal: make the manual owner/operator data refresh workflow clearer across CSV,
guarded provider sync, readiness next actions, fallback handling, and sanitized
refresh evidence.

Status: Done. Review is recorded in
`docs/reviews/v5-6-operator-data-refresh-workflow-review.md`.

Completed issues:

- #732: rebaseline roadmap after v5.5 provider hardening.
- #731: define operator data refresh workflow.
- #735: clarify Import page refresh next actions.
- #737: cover data refresh workflow boundaries.
- #736: define data refresh evidence format.
- #734: review v5.6 operator data refresh workflow.

Outcome:

- Operator docs define daily and weekly manual refresh cadence, refresh state
  handling, CSV fallback, and no-automation boundaries.
- Import page readiness and freshness copy gives clearer manual next actions for
  missing, stale, failed, partial, skipped, and unknown data states.
- API tests cover that CSV import/refresh does not automatically create signals,
  trades, alerts, or notification logs.
- `docs/DATA_REFRESH_EVIDENCE_FORMAT.md` defines sanitized refresh evidence fields.

Boundary:

- No scheduler-driven sync, automatic refresh, automatic analysis, broker
  integration, automatic execution, live/realtime claim, profitability claim, or
  production-readiness claim was introduced.

## v5.7 - Post-Refresh Operator Validation

Goal: prepare repeatable sample/paper-only validation for the manual workflow after
the v5.6 refresh guidance.

Status: Done. Review is recorded in
`docs/reviews/v5-7-post-refresh-operator-validation-review.md`; private VPS
post-refresh validation evidence is recorded in
`docs/reviews/v5-7-vps-post-refresh-validation-evidence.md`.

Planned issues:

- #744: rebaseline roadmap after v5.6 refresh workflow.
- #746: add post-refresh operator validation checklist.
- #745: define post-refresh validation evidence format.
- #747: review v5.7 post-refresh operator validation.

Done when:

- A sample/paper-only validation checklist exists for `/import`, readiness,
  explicit manual analysis, Signals review, and manual trade logging boundaries.
- A sanitized validation evidence format exists and cross-links to data-refresh,
  browser-smoke, and private-data evidence rules.
- The review confirms whether an operator-run validation follow-up is needed.
- v5.7 review is recorded and the milestone is closed.

Decision after v5.7 VPS validation:

- Do not start `v5.8 - Review Calibration Follow-up` now; the private VPS
  sample/paper-only validation passed and did not identify signal-quality gaps.
- Prefer a separate private-data/operations-readiness gate before any private
  trading-data usage or broader VPS reliance.

Deferred candidates:

- Additional deterministic review calibration if fresh paper/operator evidence
  identifies signal-quality gaps.
- Production-like readiness hardening only after a separate explicit gate.

## v5.8 - Private Data & Operations Readiness

Goal: prepare private-staging operations for possible private trading data use
through secret rotation, deploy-user routine operations, offsite encrypted backups,
restore-drill evidence, and a private-data readiness decision gate.

Status: Done / closed as No-Go for private trading data. Review is recorded in
`docs/reviews/v5-8-private-data-operations-readiness-review.md`.

Current decision:

- Private trading data remains No-Go; see
  `docs/PRIVATE_DATA_READINESS_DECISION_GATE.md`.
- #754 and #755 are complete.
- #756 and #757 were closed as not planned/deferred by owner/operator decision,
  not as pass evidence.
- v5.8 is closed without approving private trading data.

Completed or recorded:

- #754: stage-1 private-staging secret rotation recorded as pass;
  `POSTGRES_PASSWORD` and `DATABASE_URL` remain deferred.
- #755: deploy-user routine status/health re-verification recorded as pass.
- #756: offsite encrypted backup status recorded as deferred/not configured.
- #757: offsite restore-drill status recorded as deferred because #756 was
  deferred.
- #758: private-data readiness decision recorded as No-Go.
- #759: milestone review recorded.
- #768: deferred closure recorded; no duplicate follow-up issues needed.

## v5.9 - Paper Trade Workflow

Goal: improve the safe sample/paper-only workflow from signal review to manual
paper trade logging, trade management, journal, performance review, validation,
and milestone review.

Status: Done and closed. The v5.9 review is recorded in
`docs/reviews/v5-9-paper-trade-workflow-review.md`.

Completed issues:

- #770: rebaseline roadmap for paper-trade workflow.
- #771: clarify signal-to-paper-trade handoff.
- #772: improve manual paper-trade logging guidance.
- #773: improve paper-trade management and journal flow.
- #774: clarify paper-performance evidence boundaries.
- #775: validate sample paper-trade workflow.
- #776: review v5.9 paper-trade workflow.

Done when:

- Signal detail or related review UI gives clearer manual next actions without
  creating trades automatically.
- Paper trade logging and management/journal guidance is clearer and remains
  documentation-only.
- Performance evidence boundaries explicitly avoid profitability and strategy-
  validation claims.
- Sample/paper-only workflow validation is recorded.
- v5.9 review is recorded and the milestone is closed.

Boundary:

- No private trading data, broker integration, automatic execution, automatic trade
  creation, live/realtime claim, profitability claim, strategy-validation claim, or
  production-readiness claim.

## v6.0 - Staging Operations Rebaseline & Runbook Hygiene

Goal: rebaseline roadmap docs after v5.9, record sanitized private-staging database
credential recovery evidence, document repeatable staging deploy and migration
recovery, review private-staging operations posture, and close the milestone.

Status: Done and closed. The v6.0 review is recorded in
`docs/reviews/v6-0-staging-operations-rebaseline-review.md`.

Completed issues:

- #784: rebaseline roadmap after v5.9 closure.
- #785: record staging database credential recovery.
- #786: add staging deploy and migration recovery runbook.
- #787: review private-staging operations posture after v5.9.
- #788: review v6.0 staging operations rebaseline.

Done when:

- Roadmap docs no longer present v5.9 as the active next milestone.
- Sanitized DB credential recovery evidence is recorded without secrets, `.env`
  values, raw logs, database dumps, or private data.
- Staging deploy and migration recovery runbook clearly documents safe checks,
  correct repository path, correct Compose project name, mistaken-stack cleanup,
  Alembic, API health, web load, and credential-mismatch triage boundaries.
- Private-staging operations posture is reviewed, and any concrete blockers are
  captured as follow-up issues.
- v6.0 review is recorded and the milestone is closed.

Boundary:

- No private trading data approval, production-readiness claim, public exposure,
  broker integration, automatic execution, automatic trade creation, live/realtime
  claim, profitability claim, strategy-validation claim, secret publication, or
  destructive database-volume operation.

## v6.1 - Backup & Restore Decision Gate

Goal: decide whether encrypted offsite backup and restore drill remain deferred or
become the next explicit operations gate before broader staging reliance or any
private-data readiness discussion.

Status: Done. The v6.1 review is recorded in
`docs/reviews/v6-1-backup-restore-decision-gate-review.md`, and the milestone is
ready to close after #797 merges.

Completed issues:

- #794: rebaseline roadmap after v6.0 closure.
- #795: decide backup and restore path.
- #796: record backup restore decision outcome as deferred.
- #797: review v6.1 backup restore decision gate.

Done when:

- Roadmap docs no longer present v6.0 as the active next milestone.
- A backup/restore decision document explicitly chooses deferred, backup-only next,
  or backup-plus-restore next.
- The decision outcome is recorded without secrets, `.env` values, backup repository
  details, database dumps, private data, or readiness overclaims.
- If implementation is selected, follow-up issues are created before milestone
  review and before any backup repository, secret, or restore operation.
- v6.1 review is recorded and the milestone is closed.

Boundary:

- No backup or restore implementation in the decision issues, no private trading
  data approval, no production-readiness claim, no backup repository details, no
  secrets, no broker integration, no automatic execution, no automatic trade
  creation, no live/realtime claim, no profitability claim, and no strategy-
  validation claim.

## Not Now

- Broker integration.
- Automatic order execution.
- Automatic trade creation.
- Public SaaS or multi-user operation.
- Live/realtime market-data claims.
- Backtesting or profitability validation claims.

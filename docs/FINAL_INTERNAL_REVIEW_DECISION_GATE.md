# Final Internal Review Decision Gate

## Purpose

This document records the final v2.8 internal owner/operator review decision. It prevents the current evidence from being over-interpreted as production readiness, broker readiness, strategy validation, profitability evidence, live/realtime market-data evidence, trading advice, or approval for automatic execution.

## Decision

Status: Conditional Go for controlled internal owner/operator review only.

Date: 2026-05-31.

Approved use:

- Local review with sample, synthetic, or paper data.
- Controlled private single-owner/operator staging review when the separate deployment readiness gate remains satisfied.
- Manual watchlist, screener, import/sync, signal review, review batch, manual trade log, journal, and performance/risk review workflows.
- Decision-support review where the operator keeps execution outside the app and manually evaluates every setup.

Not approved:

- Public production launch or production-like public exposure.
- Broker, exchange, account sync, or order-routing use.
- Real-money readiness claim or reliance on the app as the source of execution decisions.
- Profitability, win-rate, benchmark-outperformance, backtest-validation, or strategy-validation claim.
- Live/realtime market-data claim.
- Public SaaS, multi-user onboarding, billing, or customer-support operation.
- Trading advice, buy/sell instructions, blind signal following, automatic trade creation, automatic position sizing, or automatic order execution.

## Evidence Reviewed

Passed or acceptable for this limited gate:

- Product docs were rebaselined after v2.7 to describe the final internal review candidate scope.
- API/Web CI has passed on recent merged PRs through the v2.8 docs and smoke-evidence work.
- Security scan visibility workflows are present and passed on the final internal smoke evidence PR, but remain visibility-only and are not a security certification.
- v2.8 final internal workflow smoke passed for local Docker Compose startup, API health, current database migrations, web HTTP load, authenticated sample-only workflow coverage, performance/risk review, logout, and cleanup. See `docs/MVP_SMOKE_TEST.md#v28-final-internal-workflow-smoke`.
- Deployment readiness gate v2 records Conditional Go for local review and private owner/operator staging only, with production-like exposure explicitly No Go.
- Operational docs now include monitoring checklist, structured health details, backup restore drill documentation, dependency/container scan workflow, and incident runbook.
- Strategy and alert boundaries still state decision-support only, manual execution only, no broker integration, no automatic order execution, no profitability claim, and no trading advice.
- Mobile/PWA baseline work improved signal and review-batch usability and installability without adding push trading, offline trading, background sync, broker actions, or execution.

## Remaining Risks And Gaps

These do not block controlled internal review, but they block broader exposure or stronger readiness claims:

- Visual browser clickthrough was not separately recorded in the v2.8 smoke run because no browser automation or screenshot harness is available in the local environment.
- A preserved local Docker volume required explicit `alembic upgrade head` before current screener/review workflow tables existed; migrated persistent stacks and fresh disposable stacks must verify migrations before workflow testing.
- Deployment readiness gate evidence needs a refresh after the scan workflow and incident runbook completion (`#375`).
- Monitoring checklist should link directly to the operational incident runbook (`#376`).
- Review correction audit history remains a gap (`#355`).
- Calibration finding categories still need stronger auditability (`#362`).
- Portfolio risk review should include all active trade statuses (`#368`).
- Mobile Screener density, mobile Trade workflow grouping, and global mobile header density remain follow-up gaps (`#381`, `#382`, `#383`).
- Production-grade monitoring, offsite encrypted backups, recurring restore evidence, rollback evidence, stricter security-scan policy, privacy handling, and explicit production-like owner acceptance are not complete.

## Go Conditions

Controlled internal review may continue only while all of these remain true:

- The app is used by a single owner/operator in local or approved private staging contexts.
- Data used for review is sample, synthetic, paper, or otherwise separately approved by the owner/operator.
- Secrets, cookies, database URLs, backup dumps, raw private logs, screenshots with sensitive data, and private trading data stay out of issues, PRs, docs, and commits.
- Current migrations are applied before workflow smoke testing on persistent volumes.
- The operator treats all signals, alerts, review batches, and performance views as decision-support evidence only.
- The operator manually executes, manages, and exits trades outside the app.
- `No Trade`, stale data, missing benchmark context, failed/partial/unknown provider freshness, ignored/rejected candidates, and unclear review outcomes remain valid conservative stop points.

## No-Go Conditions

The decision becomes No Go if any of these occur:

- Broker integration, account sync, automatic trade creation, automatic position sizing, automatic order execution, or automatic trading is introduced.
- UI, docs, alerts, or review artifacts imply buy/sell instructions, trading advice, profitability, win-rate, strategy validation, backtest proof, live/realtime data, or real-money readiness.
- Public exposure, public SaaS, multi-user onboarding, billing, or customer-support operation is requested without a separate production-like gate.
- Required health, migration, smoke, backup, restore, security, or auth checks fail without explicit accepted-risk documentation.
- Secrets, `.env` files, database URLs, cookies, tokens, backup dumps, sensitive screenshots, raw private logs, or private trading data are committed or attached to issues/PRs/docs.
- A restore or smoke-test target is not clearly disposable or explicitly approved.
- Critical/high security findings are open without owner acceptance.

## Required Next Decision Before Broader Use

Any broader or production-like use requires a new explicit decision gate with current evidence for:

- Target-environment deployment smoke.
- API/Web CI and reviewed dependency/container scan output.
- Monitoring and alerting operation.
- Backup freshness and restore drill on a disposable target.
- Incident response, rollback, secret rotation, and privacy handling.
- Browser/manual workflow evidence on the target environment.
- Explicit owner/operator acceptance of residual risks.

## Final Gate Statement

The final internal review candidate is acceptable for controlled internal owner/operator review with sample, synthetic, or paper workflows. It is not acceptable for production-like public exposure, real-money reliance, broker or exchange connectivity, automatic execution, live/realtime data claims, profitability claims, strategy-validation claims, trading advice, public SaaS use, or customer onboarding.

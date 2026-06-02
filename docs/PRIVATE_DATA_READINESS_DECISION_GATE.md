# Private Data Readiness Decision Gate

## Purpose

This document records the decision gate for using private owner/operator trading data in the app. It separates private-data handling from production-like exposure, broker readiness, real-money readiness, live/realtime market-data readiness, profitability validation, strategy validation, trading advice, and automatic execution.

## Current Decision

Status: No Go for routine private trading data use.

Date: 2026-06-01.

Private sample/paper staging: Conditional Go when the existing local/private-staging gates remain satisfied.

Production-like exposure: No Go.

v2.9 rebaseline snapshot, 2026-06-02: the current-main local validation evidence
passed for local Docker Compose build/startup, migrations, API health, web HTTP
load, sanitized evidence formatting, and cleanup using sample-only boundaries.
This does not change the gate: routine private owner/operator trading data remains
No Go until the required privacy, backup/restore, incident, secret-rotation, and
owner-acceptance evidence is complete.

Rationale:

- Controlled local review and private owner/operator staging are currently acceptable only for sample, synthetic, paper, or explicitly sanitized workflows.
- Private-data use needs additional evidence for privacy handling, backup retention, restore recurrence, incident rehearsal, and owner/operator acceptance.
- Local encrypted Restic backup evidence exists, but local-only storage is not geographic or ransomware-resistant by itself.
- The product remains decision-support only with manual execution outside the app.

## Safety Boundaries

- No broker integration, exchange account sync, automatic order execution, automatic trade creation, automatic position sizing, or automatic trading.
- No buy/sell instructions, trading advice, profitability claim, win-rate claim, backtest-validation claim, benchmark-outperformance claim, strategy-validation claim, or real-money-readiness claim.
- No live/realtime market-data claim.
- No public SaaS, multi-user onboarding, billing, customer-support operation, or production-like public exposure.
- Private-data approval, if later granted, applies only to the single owner/operator workflow and does not approve public or production-like use.

## Gate Matrix

| Data class | Current status | Approved use | Required evidence before use | Non-go conditions |
| --- | --- | --- | --- | --- |
| Sample/synthetic data | Go | Local checks, docs, disposable smoke tests, screenshots, issue evidence | Relevant checks pass or skipped with reason; no secrets or private records are included | Failed safety/auth checks, committed secrets, broker/execution scope introduced |
| Paper data | Conditional Go | Controlled local/private-staging review and calibration evidence | Existing local/private-staging gates remain satisfied; evidence is sanitized; operator accepts that results are process evidence only | Profitability or strategy-validation claims, private account context included, failed smoke/health checks |
| Private owner/operator trading data | No Go | None for routine use under this gate | Separate approval after evidence for evidence handling, privacy review, backup recurrence/retention, restore drill recurrence, incident rehearsal, secret rotation, and residual-risk acceptance | Missing required evidence, private records in issues/PRs/docs/logs/screenshots, unclear backup/restore path, no explicit owner acceptance |
| Production-like/private-data public exposure | No Go | None | Separate production-like gate with current security, monitoring, incident, backup, restore, rollback, privacy, and acceptance evidence | Any public exposure, multi-user use, customer data, broker/account sync, unresolved critical/high security finding |

## Required Evidence For Private-Data Approval

Private owner/operator trading data may be reconsidered only after all of this is documented with sanitized evidence:

- Current API/Web CI on `main` is passing for the relevant release candidate.
- Local/private-staging deployment and browser smoke evidence uses sample or paper data and remains current.
- Private-data evidence handling rules define allowed, redacted, and forbidden issue/PR/log/screenshot evidence. See `docs/PRIVATE_DATA_EVIDENCE_HANDLING.md`.
- Trade notes, journal content, performance records, watchlists, provider metadata, and restored rows have a documented privacy review. See `docs/TRADE_JOURNAL_PRIVACY_REVIEW.md` for the trade, journal, and performance review.
- Restic restore drill recurrence and snapshot retention expectations are documented in `docs/DEPLOYMENT_RUNBOOK.md#offsite-encrypted-backups`.
- Backup evidence avoids dump contents, restored row contents, database URLs, and secret values.
- Incident rehearsal covers database restore and secret rotation without performing service-impacting actions unless explicitly approved by the operator. See `docs/OPERATIONAL_INCIDENT_RUNBOOK.md#private-data-incident-rehearsal`.
- Secret rotation procedure is documented and accepted for provider keys, app secrets, database credentials, and deployment credentials.
- Residual risks are listed, including local-only backup risk unless an offsite encrypted target has current restore evidence.
- The owner/operator explicitly accepts the remaining risk and scope in an issue, PR, or decision record without exposing private data.

Current blockers before reconsideration:

- No explicit owner/operator acceptance for routine private trading data use is recorded.
- No current offsite/geographic encrypted backup restore evidence is recorded for
  routine private-data reliance.
- No private-data target-environment incident rehearsal with accepted secret
  rotation and restore decision boundaries is recorded.
- No evidence package proves that screenshots, logs, backups, restores, and issue
  evidence can be handled routinely without leaking private records.

## Allowed Evidence While Gate Is No Go

- Issue or PR checklist lines showing pass/fail, date, environment class, and doc references.
- Sanitized screenshots using sample, synthetic, fake, or paper-only records.
- Status enums, error-code categories, migration version, commit SHA, and CI/check links.
- Backup snapshot IDs, repository type, restore target class, and command names without paths that expose account or secret context.
- Follow-up issue links for gaps.

## Forbidden Evidence

- `.env` files, API keys, bearer tokens, cookies, session headers, database URLs, provider account IDs, broker/account data, or subscription/billing details.
- Backup dumps, restored row contents, raw database exports, raw provider payloads, raw private logs, or local storage/session dumps.
- Private watchlists, symbols that the operator considers private, trade notes, journal notes, screenshots of private records, performance exports, fill records, account balances, or broker statements.
- Claims that private-data approval means production readiness, public launch readiness, real-money readiness, profitability validation, live/realtime readiness, broker readiness, or permission for automatic execution.

## Reopen This Gate If

- Private trading data, private watchlists, real journal notes, provider-backed records, or performance records become part of routine use.
- Backup target, retention, restore process, secret storage, incident handling, authentication, session handling, logging, screenshots, or evidence sharing materially changes.
- Any secret, private record, raw log, backup dump, screenshot, or restored row content is exposed.
- Public exposure, multi-user use, customer onboarding, broker/account sync, or automatic execution is proposed.

## Final Gate Statement

The current app remains acceptable only for sample, synthetic, paper, and sanitized private-staging review workflows under the existing local/private-staging gates. Routine private owner/operator trading data use remains blocked until a separate approval records current evidence for privacy handling, backup/restore recurrence, incident rehearsal, secret rotation, and explicit owner/operator residual-risk acceptance. Production-like exposure remains No Go.

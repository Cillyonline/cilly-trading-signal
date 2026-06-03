# v3.5 Target And Owner Acceptance

## Purpose

This decision record captures the owner/operator decisions that unblock the next
v3.5 proof step for the existing VPS target.

It does not approve production-like exposure, routine private trading data,
broker integration, automatic execution, live/realtime claims, profitability
claims, trading advice, secret rotation, restore drills, firewall changes, DNS
changes, or unattended VPS actions.

## Decision

Date: 2026-06-03.

Target: existing VPS for `trading.cillyonline.de`.

Exposure: controlled private owner/operator staging only.

Data class: sample, synthetic, and paper data only.

Routine private owner/operator trading data: No Go.

Production-like/public exposure: No Go.

Next allowed operator-guided action class: non-destructive smoke only.

## Approved Next Step

The next v3.5 work may prepare and, with explicit operator participation, record
sanitized evidence for:

- Current release commit on the existing VPS.
- Caddy-routed API health.
- HTTPS web route load.
- Login/browser smoke using sample, synthetic, or paper-only workflows.
- Migration status as version-only evidence.
- Rollback readiness review using `docs/ROLLBACK_MIGRATION_SAFETY_CHECKLIST.md`.

## Not Approved

The following remain blocked unless separately approved in a later operator-run
issue:

- Production-like/public exposure.
- Routine private trading data or private journal/trade records.
- Secret rotation or credential inspection.
- Offsite backup configuration, backup upload, backup deletion, or restore drill.
- Firewall, DNS, host package, Docker daemon, or unrelated VPS project changes.
- Database repair, destructive restore, `down --volumes`, volume pruning, or broad
  Docker cleanup.
- Broker integration, account sync, order routing, automatic trade creation,
  automatic position sizing, or automatic execution.
- Profitability, win-rate, strategy-validation, live/realtime, broker-readiness,
  real-money-readiness, public SaaS, or trading-advice claims.

## Evidence Boundary

Allowed evidence:

- Pass/fail status, date/time, commit SHA, migration version, route category,
  HTTP status category, issue/PR links, and sanitized browser workflow status.

Forbidden evidence:

- `.env` files, secrets, database URLs, cookies, tokens, raw private logs,
  backup dumps, restored rows, private watchlists, private symbols if considered
  sensitive, trade notes, journal notes, provider account data, screenshots with
  private records, or credentialed URLs.

## Residual Risk Acceptance

The owner/operator accepts that this v3.5 scope is limited to controlled private
staging smoke evidence on the existing VPS. It does not prove production-like
readiness, private-data readiness, security certification, restore readiness,
offsite backup readiness, real-money readiness, profitability, or strategy
validation.

## Final Statement

The existing VPS remains a controlled private owner/operator staging target. The
next allowed work is non-destructive smoke evidence only; all broader proof areas
remain blocked until explicitly approved.

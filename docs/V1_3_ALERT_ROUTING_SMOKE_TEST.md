# v1.3 Alert Routing Smoke Test

## Purpose

This document records the v1.3 alert routing smoke-test evidence for safe automatic
Telegram routing of allowed review events.

This is a controlled validation artifact. It is not a production-readiness statement,
trading advice, profitability claim, broker-readiness claim, public SaaS readiness
claim, or approval for automatic execution.

## Safety Scope

- Decision-support only.
- Manual trade execution only.
- No broker integration.
- No automatic order execution.
- No automatic trade creation.
- Sample/test payloads only.
- No real trading data.
- No Telegram token, chat ID, webhook secret, cookie, `.env` value, screenshot with
  sensitive data, or private data is recorded here.

## Current Result

Status: Passed for local secret-free smoke verification.

Date: 2026-05-29.

Environment:

- Local repository checkout.
- API tests used faked Telegram delivery calls only.
- No real Telegram API call was made.
- No real VPS `.env` value or Telegram secret was used.

## Verification Commands

Backend verification was run from `apps/api` using a temporary Python virtual

```powershell
python -m ruff check --select E,F,UP,B .
python -m pytest
```

Result:

- Ruff: PASS.
- Pytest: PASS, `211 passed, 13 warnings`.

Frontend verification was run from `apps/web`:

```powershell
npm run build
```

Result:

- Web build: PASS.

## Covered Smoke Scenarios

The automated backend smoke coverage verifies the v1.3 routing behavior with
sample TradingView-style webhook payloads and mocked Telegram delivery:

- Webhook secret guard rejects invalid secrets.
- Valid TradingView-style webhook persists an alert event.
- Routing disabled results in `skipped` delivery without Telegram send.
- Policy-allowed events route to Telegram when enabled:
  - `near_trigger`
  - `entry_trigger`
  - `long_entry`
  - `invalidation`
  - `exit_warning`
- Manual-only events are persisted but not sent:
  - `info`
  - `watchlist`
  - `armed`
  - `management`
  - `exit_signal`
- Unsupported trigger values are rejected.
- Missing Telegram config records a failed delivery without rejecting webhook ingestion.
- Telegram provider failure records a failed delivery without rejecting webhook ingestion.
- Duplicate webhook events within 30 minutes are persisted and marked `skipped`.
- Separate `symbol + alert_type + timeframe` dedup keys are routed independently.
- Burst rate limit prevents more than 10 Telegram deliveries per user within 5 minutes.
- Alert review UI build succeeds and includes delivery-status visibility for `sent`,
  `failed`, and `skipped` outcomes.
- Message wording remains review-oriented and contains no buy/sell instruction.

## Sanitized Evidence Summary

- Allowed event routing: PASS via mocked Telegram send and persisted `NotificationLog`.
- Manual-only blocking: PASS via no mocked Telegram send and `skipped` alert status.
- Misconfigured Telegram path: PASS via `TelegramConfigurationError` persisted safely.
- Provider failure path: PASS via `TelegramDeliveryError` persisted safely.
- Deduplication: PASS via one sent delivery and duplicate alert marked `skipped`.
- Rate limiting: PASS via 10 sent deliveries and the 11th alert marked `skipped`.
- Alert UI status visibility: PASS via successful Next.js build.
- Secret handling: PASS; no real Telegram token, chat ID, webhook secret, cookie, or
  `.env` value was used or recorded.

## Staging Telegram Provider Gap

Real Telegram provider delivery from the private VPS staging environment was not run
in this repository session because it requires server-local secrets and operator-only
access to the staging `.env` and Telegram chat. This is an operational follow-up, not
an application-code blocker.

When the operator runs the staging provider smoke, use only sanitized evidence:

- API health before and after the test.
- One allowed sample webhook result showing delivery `sent`.
- One manual-only sample webhook result showing delivery `skipped`.
- One duplicate sample webhook result showing delivery `skipped`.
- Alert UI showing `sent`, `failed` or `skipped` states without secrets or private data.
- Telegram message screenshot or transcript only if token, chat ID, personal metadata,
  and private data are redacted.

Do not paste the real webhook secret, Telegram token, Telegram chat ID, cookies,
database URLs, `.env` contents, or private trading data into docs, issues, PRs, logs,
or chat.

## Final Statement

The v1.3 alert routing implementation passes local secret-free smoke verification and
CI-style automated coverage for allowed, blocked, failed/misconfigured, duplicate,
rate-limited, and UI visibility scenarios. Private VPS Telegram provider delivery
still requires an operator-run sanitized staging check before treating Telegram
delivery as operationally verified on the VPS.

# MVP Release Checklist

## Purpose

This checklist summarizes the current MVP release-candidate posture for review and handoff. It is not a production-readiness statement, strategy validation, profitability claim, or trading recommendation.

## Release Boundary

- Scope: single-user, local or controlled staging review cockpit for long-only swing-trading analysis and manual documentation.
- Execution: manual only, outside the app.
- Signals: decision-support prompts, not buy/sell instructions.
- Data: manually imported TradingView CSV data; no live data feed.
- Broker access: not included.

## Done

- FastAPI backend with SQLAlchemy models, Alembic migrations, and protected MVP routes.
- Next.js frontend with Login, Dashboard, Watchlist, CSV Import, Signals, Alerts, Trades, Performance, and Settings areas.
- Single-user HttpOnly cookie auth with no public registration and no client-side token storage.
- Watchlist CRUD for stock and crypto symbols.
- TradingView CSV import for `1W`, `1D`, and `4H` with required-field, plausibility, timeframe-spacing, upload-size, and candle-count validation.
- Persisted multi-timeframe analysis from manually imported CSV data.
- Indicator foundation for EMA, RSI, ATR, volume, relative volume, and swing structure.
- Deterministic Trend Pullback Long and Base Breakout Long signal generation with conservative `No Setup` outcomes.
- Signal explainability fields: reasoning, risk flags, No-Trade reasons, next action, manual review notes, review history, and stale-signal visibility.
- Manual signal review status transitions without trade or order creation.
- TradingView webhook ingestion that stores review alerts without storing webhook secrets and without broker execution.
- Telegram explicit test-message endpoint and settings UI test action; no automatic strategy alert delivery in the current slice.
- Read-only Alert Events UI for webhook and notification review records.
- Manual trade logging with risk/R:R calculation, trade events, close flow, journal review, and performance summary in R.
- Risk Settings for account size, max risk percent, minimum R:R, and max open trades.
- CI for API lint/tests, Web build, and PostgreSQL/Alembic migration smoke.
- Operational docs for deployment, backups, secrets, health checks, logging, and smoke-test guidance.

## Partial

- Full MVP smoke test is documented but not passed in the latest run; see `docs/MVP_SMOKE_TEST.md`.
- Dashboard, Journal, Performance, Alerts, and Settings are MVP-level views, not full analytics or operations consoles.
- Risk enforcement covers core manual trade logging rules, not full portfolio exposure, correlation, or account-level risk management.
- Stale signal handling flags old saved signals, but does not refresh market data or re-run strategy automatically.
- Telegram support currently covers explicit operator test messages; production alert routing is not complete.
- TradingView webhook support persists review events, but does not trigger broker execution, auto-trade creation, or automatic Telegram delivery.
- Local smoke testing needs deterministic fixture data and a repeatable runner; follow-ups: `#117`, `#118`.

## Missing

- Live market data API integration.
- Automated recurring imports or scheduled analysis.
- Full notification routing and automatic alert delivery rules.
- Production monitoring, operational alerting, and security review completion.
- Multi-user mode, roles beyond MVP admin, registration, password reset, and account management.
- Backtesting, strategy validation, benchmark reporting, or profitability evidence.
- Full mobile app/PWA hardening beyond responsive MVP layouts.
- Import history UX polish and release-candidate browser smoke pass.

## Blocked

- Latest Docker Compose MVP smoke startup was blocked because the Docker Desktop Linux engine was not reachable from the local shell session.
- Full CSV import -> analysis -> signal review smoke path is blocked until deterministic sample/paper CSV fixtures are available (`#117`).
- Repeatable release smoke validation is blocked until a smoke-test runner or clearer automation exists (`#118`).
- A complete browser-based end-to-end review is still required before calling the MVP smoke flow passed.

## Not Included

- Automatic order execution.
- Broker or exchange integration.
- Buy/sell recommendations or blind trading instructions.
- Profitability, win-rate, or strategy-validity claims.
- Live market data, live account sync, or portfolio execution automation.
- Public SaaS operation, multi-tenant isolation, billing, or user onboarding.
- Options, leverage, margin, short-selling strategies, or automated position sizing.

## Release Review Gate

Before using this MVP as a release candidate, reviewers should confirm:

- Required CI checks are green on the release branch.
- `docs/MVP_SMOKE_TEST.md` has a fresh run with the actual pass/fail state.
- Any material smoke-test failures have linked follow-up issues.
- Safety wording remains visible in Login/Dashboard, Signals, Alerts, Trades, Performance, and Settings flows.
- No documentation or UI copy claims production readiness, profitability, strategy validation, broker execution, or automatic trading.

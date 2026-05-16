# Delivery Roadmap

## Purpose

This document translates the strategic product roadmap into an operative delivery order. It should guide the next implementation increments without replacing `PRODUCT_ROADMAP.md`, `MVP_SPEC.md`, or the GitHub issue tracker.

The goal is to keep the project focused: build a stable foundation first, then a usable data flow, then reviewable trading signals, and only then trade logging and performance workflows.

## Current Status

The project is past the initial skeleton. The current MVP can run the core manual workflow from watchlist maintenance through CSV import, deterministic analysis, signal review, manual trade logging, journal notes, and basic performance review. It is still not production-ready and must remain decision-support only.

Done:

- Application skeleton for FastAPI, Next.js, PostgreSQL, Docker Compose, and Caddy.
- GitHub issue template and pull request template.
- Engineering workflow and review gates.
- CI checks for API lint/tests, web build, and PostgreSQL/Alembic migration smoke.
- `main` branch protection with required CI checks.
- Local setup documentation and smoke-check guidance.
- Single-user HttpOnly cookie auth with protected MVP API routes.
- Production/staging config guards for default secrets, unsafe credentials, wildcard CORS, and insecure auth cookies.
- Watchlist CRUD for stock and crypto symbols.
- TradingView CSV import and persisted market data series/candles.
- Indicator calculation foundation for EMA, RSI, ATR, volume, relative volume, and swing structure.
- Persisted multi-timeframe analysis using real `1W`, `1D`, and `4H` data.
- Trend Pullback Long and Base Breakout Long signal generation with conservative `No Setup` outcomes.
- Persisted signal explainability fields: reasoning, risk flags, No-Trade reasons, and next action.
- Signal list/detail UI for reviewable setup cards.
- Manual trade logging, trade events, close flow, journal entries, and R-multiple performance summary.
- Risk Settings API/UI with account size, max risk percent, minimum R:R, and max open trades.
- Dashboard and safety wording for manual execution only.

Partial:

- CSV import is usable, but strict upload-size and timeframe-consistency hardening is tracked in `#66`.
- Dashboard, journal, and performance views are MVP-level summaries, not full analytics modules.
- Risk enforcement covers manual trade creation basics, not complete portfolio-level exposure management.
- Multi-timeframe analysis requires manually imported `1W`, `1D`, and `4H` datasets; there is no live data sync.
- Auth is intentionally single-user and admin-only for MVP use.

Missing:

- Live market data API integration.
- TradingView webhook ingestion and Telegram alert delivery.
- Production deployment runbook, backup/restore process, monitoring, and operational alerting.
- Multi-user mode, roles beyond the MVP admin, public registration, and password reset flows.
- Backtesting, strategy validation, or profitability reporting.
- Broker integration or automatic order execution.

Current blockers and risks:

- The app is not production-ready until deployment, monitoring, backups, secrets operations, and security review are completed.
- CSV timeframe/upload hardening must be merged before CSV import should be considered robust against common user mistakes.
- Strategy behavior remains a deterministic decision-support hypothesis and must not be presented as trading advice or validated profitability.
- Local development depends on `uv`, Python 3.12, Node.js 20, Docker, and a reachable PostgreSQL database or Docker Compose.

## v0.1 - Foundation

Goal: make the backend foundation reliable enough for feature work.

Status: Done.

Primary work:

- Implement MVP backend data model and migrations: #2
- Add migration and database smoke checks.
- Keep local setup and CI reproducible while the data model is introduced.

Done when:

- PostgreSQL schema can be created from migrations.
- Core MVP entities exist in code and database.
- CI remains green.
- Data model deviations from `docs/DATA_MODEL.md` are documented.

## v0.2 - MVP Data Flow

Goal: move from empty skeleton to first useful data workflows.

Status: Done, with CSV hardening follow-up in `#66`.

Primary work:

- Build watchlist MVP slice: #5
- Implement TradingView CSV import validation: #6
- Implement indicator calculation foundation: #1

Done when:

- Symbols can be managed in the watchlist.
- TradingView CSV data can be validated and stored.
- Core indicators can be calculated deterministically and tested.
- The data flow is usable without live market data or broker integration.

## v0.3 - MVP Signal Flow

Goal: produce the first explainable, reviewable signal cards.

Status: Done for deterministic MVP signals and persisted explainability.

Primary work:

- Implement MVP signal engine for long setups: #8
- Generate signal cards with score, status, reasoning, risk flags, entry, stop, targets, R:R, and invalidation.
- Run Trading Logic Review through the ChatGPT Project before merge.

Done when:

- Trend Pullback Long and Base Breakout Long can produce Watchlist, Armed, and No Setup outcomes.
- No-Trade rules are implemented and tested as core behavior.
- Signal wording does not imply financial advice or automatic execution.
- Trading logic is reviewed against `docs/STRATEGY_AND_ALERTS.md`.

## v0.4 - Trade Logging And Risk

Goal: allow manual trades to be logged and reviewed without broker integration.

Status: Done for MVP manual trade logging and basic risk enforcement.

Expected work:

- Manual trade creation from a signal or directly from the Trades area.
- Risk calculation from entry, stop, position size, and account settings.
- Trade status transitions for open, closed, and reviewed trades.
- Basic trade events and notes.

Done when:

- A manually executed trade can be recorded, managed, closed, and reviewed.
- Result in R can be calculated from stored trade data.
- Risk defaults are configurable enough for MVP use.

## v0.5 - MVP Reviewable Release

Goal: provide an end-to-end MVP flow that can be used for disciplined paper trading or small manual review workflows.

Status: Mostly done for the local/manual MVP flow; production readiness and alerting are still missing.

Expected work:

- Dashboard summary for open trades, armed setups, recent imports, and performance basics.
- Basic journal and performance views.
- MVP usability pass for desktop and mobile layouts.
- Documentation for safe manual usage.

Done when:

- Watchlist -> CSV import -> indicators -> signals -> manual trade logging -> journal/performance can be completed.
- The app remains explicitly decision-support only.
- No automatic order execution or broker integration exists.

## v0.6 - Hardening And Production Preparation

Goal: make the implemented MVP safer, clearer, and closer to a deployable single-user tool without adding broker execution.

Primary work:

- Harden auth, production/staging config, and cookie/session behavior.
- Require real multi-timeframe data for persisted analysis.
- Add PostgreSQL migration smoke checks to CI.
- Tighten CSV import validation and upload limits.
- Keep README, roadmap, and architecture docs aligned with implemented behavior.

Done when:

- Default credentials and unsafe production settings fail fast.
- Required CI checks include API lint/tests, web build, and migration smoke.
- CSV import rejects common wrong-timeframe and oversized-upload mistakes.
- Documentation clearly separates implemented, partial, missing, and blocked areas.
- The app still makes no production-readiness, profitability, or execution claims.

## Not Now

These are intentionally outside the near-term delivery plan:

- Automatic order execution.
- Broker or Trade Republic integration.
- Live market data API.
- Multi-user mode.
- Native Android app.
- Complex backtesting engine.
- AI screenshot analysis.
- Short strategies.
- Options, leverage, or margin automation.

## Operating Rules

- Prefer small PRs tied to one issue.
- Keep `main` protected and green.
- Add or update tests with behavior changes.
- Treat trading logic as a hypothesis, not a guarantee.
- Prefer conservative signal behavior: `No Trade` is better than a weak or unexplained setup.
- Use the Trading Logic Review project for strategy, score, No-Trade, R:R, stop, target, invalidation, and alert wording changes.

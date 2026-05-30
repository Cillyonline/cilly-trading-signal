# Delivery Roadmap

## Purpose

This document translates the strategic product roadmap into an operative delivery order. It should guide the next implementation increments without replacing `PRODUCT_ROADMAP.md`, `MVP_SPEC.md`, or the GitHub issue tracker.

The goal is to keep the project focused: build a stable foundation first, then a usable data flow, then reviewable trading signals, and only then trade logging and performance workflows.

## Current Status

The project is past the initial skeleton. The current MVP can run the core manual workflow from watchlist maintenance through CSV import or guarded manual Daily/EOD provider sync, deterministic analysis, benchmark-context review, explainable signal review, alert review, manual trade logging, journal notes, basic performance review, and TradingView screener CSV prefiltering into explicit Watchlist candidates. It is still not production-ready and must remain decision-support only.

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
- Market data source, freshness, and sync metadata for CSV and provider-backed series.
- Manual provider sync endpoint and UI action, disabled by default, with the first Alpha Vantage Daily/EOD adapter and persisted provider candles.
- Indicator calculation foundation for EMA, RSI, ATR, volume, relative volume, and swing structure.
- Persisted multi-timeframe analysis using real `1W`, `1D`, and `4H` data.
- Trend Pullback Long and Base Breakout Long signal generation with conservative `No Setup` outcomes.
- Persisted signal explainability fields: reasoning, risk flags, No-Trade reasons, and next action.
- Signal list/detail UI for reviewable setup cards.
- Manual trade logging, trade events, close flow, journal entries, and R-multiple performance summary.
- Risk Settings API/UI with account size, max risk percent, minimum R:R, and max open trades.
- Dashboard and safety wording for manual execution only.
- TradingView webhook ingestion, Telegram test delivery, policy-gated automatic Telegram routing with dedup/rate limiting, alert event review UI, manual signal review workflow, and stale signal visibility.
- Review cockpit usability improvements across Dashboard, Signals, Alerts, Trades, and the documented manual review workflow.
- TradingView screener CSV import snapshots, validation, candidate review UI, and explicit screener-result to Watchlist conversion with visible duplicate handling.
- Strategy calibration v2.1: professional playbook, asset-specific stock/crypto overlays, improved swing/pullback/breakout/risk-plan logic, market regime and relative strength checks, improved No-Trade wording, analysis quality reports, and calibration workflow docs.
- Benchmark-context status for stored daily `SPY`/`QQQ` and `BTC`/`ETH` context in the Watchlist workflow.
- Focused calibration golden-case suite, end-to-end stored OHLCV/benchmark fixtures,
  historical/paper review protocol, and app-supported review batch workflow.
- Private VPS staging smoke test, operations hardening, and staging-only decision gate for controlled owner/operator use.

Partial:

- CSV import is hardened for upload size, candle count, and timeframe consistency, and remains the supported manual baseline/fallback.
- Screener CSV import is implemented as a candidate prefiltering workflow, but filtering, bulk review actions, pagination beyond the current row limits, and candidate prioritization remain future usability work.
- Manual provider sync currently targets Daily/EOD data first; `4H`/intraday provider support remains unresolved and not promised.
- Dashboard, journal, and performance views are MVP-level summaries, not full analytics modules.
- Risk enforcement covers manual trade creation basics, not complete portfolio-level exposure management.
- Multi-timeframe analysis still requires current stored data for required `1W`, `1D`, and `4H` timeframes; provider sync does not automatically fill unsupported timeframes or rerun analysis.
- Historical/paper review batches are implemented at an MVP level; richer review
  analytics and exports remain future usability work.
- Auth is intentionally single-user and admin-only for MVP use.

Missing:

- Scheduled or automatic market-data sync.
- Production-grade monitoring and operational alerting.
- Multi-user mode, roles beyond the MVP admin, public registration, and password reset flows.
- Backtesting, strategy validation, or profitability reporting.
- Broker integration or automatic order execution.

Current blockers and risks:

- The app is not production-ready until deployment is repeatedly verified and monitoring, secrets operations, and security review are completed.
- Strategy behavior remains a deterministic decision-support hypothesis and must not be presented as trading advice or validated profitability.
- Local development depends on `uv`, Python 3.12, Node.js 20, Docker, and a reachable PostgreSQL database or Docker Compose.
- Private VPS staging is accepted for controlled owner/operator use only after documented operations hardening; production-like or public use remains blocked until a separate operational readiness decision addresses data-handling readiness, offsite backups, security review, and monitoring expectations.
- MVP release posture is tracked in `docs/MVP_RELEASE_CHECKLIST.md`; it separates Done, Partial, Missing, Blocked, and Not Included areas without claiming production readiness.

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

Status: Mostly done for the local/manual MVP flow; private VPS staging has a conditional owner/operator go, while production readiness is still missing.

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

## v1.3 - Reliable Alert Routing

Goal: deliver Telegram notifications automatically only for policy-allowed review events,
without broker execution, order creation, trading advice, or buy/sell wording.

Status: Done for local secret-free verification and CI coverage; private VPS Telegram provider delivery still needs an operator-run sanitized check before operational reliance.

Primary work:

- Route only `near_trigger`, `entry_trigger`, `invalidation`, and `exit_warning` automatically.
- Keep `info`, `watchlist`, `armed`, `management`, `exit_signal`, and unknown triggers manual-only or blocked.
- Add explicit configuration guards so automatic delivery fails closed.
- Add deduplication and rate limiting for `symbol + alert_type + timeframe` within 30 minutes.
- Persist delivery outcomes and make failures reviewable without breaking webhook ingestion.
- Add backend tests and a sanitized smoke-test record.

Done when:

- Allowed events send Telegram automatically in staging with sanitized evidence.
- Manual-only and unknown events do not send Telegram.
- Missing config, Telegram failures, duplicates, and rate limits are covered by tests.
- Message wording remains manual-review only and contains no buy/sell instruction.
- No secrets, chat IDs, webhook secrets, or private trading data are exposed in docs, logs, issues, or PRs.

## v1.4 - Market Data Preparation

Goal: prepare the product for provider-backed market data without broker
integration, automatic execution, trading advice, or live-signal claims.

Status: Done. Provider choice, source/freshness model, schema preparation, sync
metadata, and UI visibility were implemented across v1.4 and refined in v1.5.

Primary work:

- Define the provider decision matrix for stocks and crypto.
- Preserve TradingView CSV import as a supported baseline and fallback.
- Add provider-neutral configuration, data source metadata, freshness metadata, and
  sync status handling.
- Prepare schema and service boundaries before adding guarded provider API calls.
- Make data source and freshness visible in API/UI so stale or unknown data cannot look
  equivalent to fresh data.

Done when:

- Provider choice, open questions, and unsupported needs are documented.
- CSV and provider-backed data can be represented distinctly.
- Stale, failed, partial, or unknown market data is conservative and visible.
- No API keys, provider secrets, subscription details, or private trading data are
  committed or pasted.
- No real-time, production-readiness, profitability, broker-readiness, trading advice,
  or automatic-execution claim is introduced.

## v1.5 - Market Data Usability

Goal: make market-data source and freshness useful in normal review workflows
without broker integration, automatic execution, trading advice, or live-signal
claims.

Status: Done.

Primary work:

- Derive CSV freshness automatically from stored candle end time and timeframe.
- Show latest market-data freshness on Watchlist and Dashboard.
- Treat stale, failed, partial, missing, or unknown required timeframe data
  conservatively in analysis.

Done when:

- Source/freshness is visible in review workflows.
- Required timeframe data that is not fresh adds conservative analysis flags.
- CSV workflows remain supported.

## v1.6 - Manual Provider Sync MVP

Goal: add controlled manual provider-backed market-data sync, disabled by default
and without scheduler, broker integration, automatic execution, or live/realtime
signal claims.

Status: Done.

Primary work:

- Implement a mocked provider client adapter boundary and first Alpha Vantage
  Daily/EOD path.
- Add authenticated manual provider sync endpoint.
- Persist provider candles safely to provider-backed series only.
- Add UI action and result visibility for manual provider sync.

Done when:

- Manual sync can be requested only through guarded API/UI paths.
- Sync states are visible as success, skipped, failed, or partial.
- Provider data is persisted with source/freshness/sync metadata.
- No scheduler, automatic analysis, broker action, live/realtime claim, or trading
  instruction is introduced.

## v1.7 - Documentation & Provider Sync Hardening

Goal: align documentation and harden the manual provider sync path after v1.4-v1.6.

Status: Done.

Primary work:

- Align product, delivery, deployment, provider, and freshness docs with the implemented provider-sync path.
- Add an operator runbook and safe smoke checklist for manual provider sync.
- Add provider sync API edge-case coverage and polish UI result states.

Done when:

- Provider sync remains manual, disabled by default, and conservative.
- Docs avoid scheduler, broker, automatic-execution, live/realtime, production-readiness, profitability, and trading-advice claims.

## v1.8 - Review Cockpit Usability

Goal: improve the day-to-day review cockpit across Dashboard, Signals, Alerts, Trades, and documentation.

Status: Done.

Primary work:

- Improve dashboard review priorities and stale-data visibility.
- Add actionable filters to Signals and alert event review workflows.
- Add trade review completeness indicators.
- Document the cockpit review workflow across data context, setup review, alerts, trades, journal, and performance.

Done when:

- Review surfaces show what needs attention without implying buy/sell instructions.
- Stale data, missing review context, and incomplete documentation remain visible conservative stop points.

## v1.9 - Screener CSV Preparation

Goal: prepare a safe TradingView screener CSV workflow for Watchlist candidate review.

Status: Done.

Primary work:

- Design the TradingView screener CSV import model.
- Add `ScreenerImport` and `ScreenerResult` models, schemas, migrations, validation service, and authenticated API routes.
- Add the `/screener` UI for upload, results, validation errors, and manual candidate review.
- Add explicit conversion from selected screener result to Watchlist item, linking duplicates visibly instead of creating another Watchlist symbol.

Done when:

- Screener rows are imported as stored snapshots and review candidates only.
- Adding a candidate to Watchlist requires an explicit user action.
- Duplicates are handled safely and visibly.
- No screener import or conversion creates analysis, signals, trades, alerts, broker actions, orders, live/realtime claims, profitability claims, or trading advice.

## v2.0 - Release Rebaseline & Operational Readiness

Goal: rebaseline the project after v1.8/v1.9, refresh release posture docs, rerun current smoke checks, and decide the next product milestone.

Status: Done.

Primary work:

- Close the completed v1.9 milestone and record completion.
- Update roadmap and release posture docs after provider sync, cockpit usability, and screener workflow work.
- Add a smoke checklist for the screener-to-Watchlist flow.
- Run a current-main Docker Compose smoke test and record sanitized evidence.
- Decide the next product milestone direction.

Done when:

- The docs and issue tracker reflect the current implemented, partial, missing, and not-included scope.
- Current smoke evidence is recorded without secrets or private trading data.
- The next milestone recommendation is explicit and still preserves manual-review-only safety boundaries.

## v2.1 - Strategy Calibration & Signal Quality

Goal: calibrate the trading analysis system toward professional, explainable setup quality for stocks and crypto.

Status: Done, including follow-ups `#292`, `#293`, `#294`, `#299`, and `#300`.

Primary work:

- Define the professional strategy playbook and stock/crypto overlays.
- Improve swing structure, Trend Pullback Long, Base Breakout Long, stop/target, invalidation, market regime, and relative strength logic.
- Improve no-trade reasons, next actions, and analysis quality reporting.
- Expose benchmark-context status for required stored daily stock and crypto context.
- Add a focused calibration golden-case suite.
- Add end-to-end stored OHLCV and benchmark-context calibration fixtures.
- Document strategy calibration and historical/paper review protocols.
- Add app-supported historical/paper review batches for structured evidence.

Done when:

- Weak or incomplete setups are blocked or downgraded with explicit reasons.
- Benchmark/regime and relative-strength context is visible and conservative when missing.
- Rule changes have a documented calibration workflow and focused golden-case tests.
- Historical/paper review remains process evidence only, not strategy validation.
- No broker integration, automatic execution, live/realtime claim, profitability claim, or trading advice is introduced.

## Next Candidate Increment

Recommended next planning candidates: screener usability v2, operational hardening,
or review-batch usability refinements after enough sanitized review examples exist.

Alternative next increments:

- Screener usability v2 after calibrated review paths are further protected.
- Operational hardening before broader exposure.
- Review-batch export/filtering and follow-up issue workflow polish.

## Not Now

These are intentionally outside the near-term delivery plan:

- Automatic order execution.
- Broker or Trade Republic integration.
- Real-time market data claims.
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

# Delivery Roadmap

## Purpose

This document translates the strategic product roadmap into an operative delivery order. It should guide the next implementation increments without replacing `PRODUCT_ROADMAP.md`, `MVP_SPEC.md`, or the GitHub issue tracker.

The goal is to keep the project focused: build a stable foundation first, then a usable data flow, then reviewable trading signals, and only then trade logging and performance workflows.

## Current Status

The project is a final internal review-candidate cockpit for controlled single owner/operator use. It can run the core manual workflow from watchlist maintenance through CSV import or guarded manual Daily/EOD provider sync, deterministic analysis, benchmark-context review, explainable signal review, alert review, manual trade logging, journal notes, performance/risk review, TradingView screener CSV prefiltering into explicit Watchlist candidates, and historical/paper review batches. It is still not production-ready and must remain decision-support only.

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
- Deployment readiness decision gate v2 for local review, private owner/operator staging, and production-like non-go boundaries.
- v2.2-v2.4 review workflow refinements: review entry correction support, calibration finding categories, repeated finding visibility, and documented follow-up gaps.
- v2.5 risk and portfolio review: open portfolio risk, max open risk warnings, asset concentration warnings, correlation proxy warnings, and trade journal analytics.
- v2.6 operational readiness: application monitoring checklist, structured health details, backup restore drill documentation, deployment readiness decision gate v2, dependency/container scan workflow, and operational incident runbook.
- v2.7 mobile/PWA owner cockpit baseline: mobile layout audit, improved mobile signal cards, improved mobile review batch entry, and PWA manifest/icons.
- v2.9-prep calibration and evidence work: the first paper calibration batch was
  expanded to 80 examples, resistance/missing-context/trigger-confirmation
  coverage was made deterministic, review evidence templates and UI wording were
  clarified, a safe dry-run browser smoke contract was documented, and a
  non-invasive local smoke evidence formatter was added.
- v2.9 current-state rebaseline, v3.0 Owner Cockpit Polish, and v3.1 Operator
  Validation And Evidence are complete. The owner/operator review workflow was
  rebaselined, local validation evidence was recorded, Review follow-up
  disposition, mobile Screener review, and mobile Trade Detail grouping were
  polished, and operator-run VPS update/browser smoke evidence was recorded.
- v3.3 Signal Quality Calibration Pack added targeted regression evidence for
  weak risk/reward rejection and missing/stale required `4H` trigger context.

Partial:

- CSV import is hardened for upload size, candle count, and timeframe consistency, and remains the supported manual baseline/fallback.
- Screener CSV import is implemented as a candidate prefiltering workflow with filters, bulk review actions, pagination, and explicit Watchlist conversion; mobile density and richer candidate prioritization remain future usability work.
- Manual provider sync currently targets Daily/EOD data first; `4H`/intraday provider support remains unresolved and not promised.
- Dashboard, journal, and performance views include useful MVP-level summaries, risk warnings, and journal analytics, but are not full institutional analytics modules.
- Risk enforcement covers manual trade creation basics and portfolio/risk review warnings, not complete account-level risk management or automatic position sizing.
- Multi-timeframe analysis still requires current stored data for required `1W`, `1D`, and `4H` timeframes; provider sync does not automatically fill unsupported timeframes or rerun analysis.
- Historical/paper review batches are implemented at an MVP level with correction, repeated-finding visibility, follow-up status snapshots, improved evidence templates, and clearer follow-up disposition drafting; richer review analytics and automated follow-up workflows remain future usability work.
- Auth is intentionally single-user and admin-only for MVP use.

Missing:

- Scheduled or automatic market-data sync.
- Production-grade monitoring and operational alerting beyond documented checklists and non-blocking scan visibility.
- Multi-user mode, roles beyond the MVP admin, public registration, and password reset flows.
- Backtesting, strategy validation, or profitability reporting.
- Broker integration or automatic order execution.

Current blockers and risks:

- The app is not production-ready until production-like monitoring, secrets operations, restore drills, incident response rehearsal, security/scan acceptance, private-data handling, rollback evidence, and explicit owner acceptance are completed for the target environment. Current local and private VPS smoke evidence supports controlled owner/operator review only.
- Strategy behavior remains a deterministic decision-support hypothesis and must not be presented as trading advice or validated profitability.
- Local development depends on `uv`, Python 3.12, Node.js 20, Docker, and a reachable PostgreSQL database or Docker Compose.
- Private VPS staging is accepted for controlled owner/operator use only after documented operations hardening; production-like or public use remains blocked until a separate operational readiness decision addresses data-handling readiness, offsite backups, security review, and monitoring expectations.
- Deployment readiness is currently gated by `docs/DEPLOYMENT_READINESS_DECISION_GATE_V2.md`: local review and private owner/operator staging are conditionally allowed; production-like exposure remains No Go.
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

## v2.2-v2.4 - Review Evidence Refinement

Goal: make the historical/paper review workflow more useful for process evidence without turning it into backtesting or profitability validation.

Status: Done, with follow-up gaps for audit history and auditable finding categories.

Primary work:

- Improve review entry correction support.
- Make calibration finding categories visible and repeated findings easier to spot.
- Preserve repeated findings as follow-up evidence only, not automatic strategy changes.

Done when:

- Review corrections and repeated findings support structured manual review.
- Follow-up gaps are captured explicitly.
- No profitability, backtesting, trading advice, or automatic execution claim is introduced.

## v2.5 - Risk And Portfolio Review

Goal: improve owner/operator risk visibility across open trades and historical journal records.

Status: Done, with follow-up gap `#368` for active trade status coverage.

Primary work:

- Add open portfolio risk overview and max open risk warnings.
- Add asset concentration and simple correlation proxy warnings.
- Add trade journal analytics focused on process quality.

Done when:

- Risk warnings are explainable and conservative.
- Unknown or incomplete risk data remains visible.
- No automatic position sizing, account sync, broker action, or trade advice is introduced.

## v2.6 - Operational Readiness

Goal: improve controlled owner/operator operational posture without production-readiness overclaims.

Status: Done, with follow-up gaps `#375` and `#376` for stale doc references after scan/runbook completion.

Primary work:

- Add application monitoring checklist and structured health details.
- Document backup restore drill and incident response procedures.
- Add deployment readiness decision gate v2.
- Add non-blocking dependency and container scan workflow.

Done when:

- Operators have documented monitoring, backup/restore, scan, and incident-response paths.
- Production-like exposure remains explicitly No Go without separate evidence and acceptance.
- No secrets, private data, production-readiness claim, broker readiness, or automated execution are introduced.

## v2.7 - Mobile/PWA Owner Cockpit

Goal: improve mobile owner/operator review usability and baseline installability.

Status: Done, with follow-up gaps `#381`, `#382`, and `#383` for Screener density, trade workflow grouping, and global header density.

Primary work:

- Audit mobile layouts across core review workflows.
- Improve mobile signal cards and signal detail review hierarchy.
- Improve mobile review batch entry and correction grouping.
- Add PWA manifest baseline and static icons.

Done when:

- Signals and review batch workflows are easier to use on mobile.
- The app has a basic installable shell.
- No push trading, offline trading mode, background sync, live/realtime claim, broker integration, or automatic execution is introduced.

## v2.9 - Current-State Rebaseline And Operator Validation

Goal: rebaseline the current internal review candidate after calibration/evidence
prep, record current-main sample-only validation evidence, and identify the top
owner/operator polish gaps before starting a larger v3.0 increment.

Status: Done.

Primary work:

- Rebaseline roadmap, release checklist, and gate summaries after the completed
  paper calibration expansion, review evidence polish, and safe automation prep.
- Record current-main sample-only smoke/validation evidence using sanitized
  pass/fail/skipped fields and the local evidence formatter.
- Review the owner/operator workflow from Watchlist through Review Batch, Trade
  Log, Journal, and Performance to identify real friction points.
- Convert only the highest-value polish findings into scoped follow-up issues.

Done when:

- Current docs describe the implemented, partial, missing, and blocked scope.
- Sample-only validation evidence is recorded or a blocker is documented.
- Top polish candidates are prioritized without private data, production-like
  exposure, broker integration, profitability claims, or automatic execution.

## v3.0 - Owner Cockpit Polish

Goal: reduce owner/operator workflow friction after the v2.9 rebaseline while
preserving manual review, evidence-only calibration, and no-execution boundaries.

Status: Done.

Primary work:

- Polish Review follow-up disposition visibility and draft wording: `#506`.
- Polish mobile Screener candidate review density and next-action clarity: `#507`.
- Polish mobile Trade Detail workflow grouping for Manage, Close, and Journal:
  `#508`.

Done when:

- Review follow-up disposition is clearer without automatic issue creation or
  strategy-rule changes.
- Screener candidates remain manual review candidates with explicit Watchlist
  conversion only.
- Trade Detail remains manual documentation only, with clearer mobile grouping.
- CI, local build, and PR review pass.

## v3.1 - Operator Validation And Evidence

Goal: validate the v3.0 cockpit polish with local/sample evidence and an
operator-run VPS smoke before choosing the next delivery gate.

Status: Done.

Primary work:

- Add a repeatable owner/operator cockpit validation checklist: `#516`.
- Record local Docker Compose, API health, web load, Caddy-routed browser login,
  and desktop/mobile cockpit validation evidence: `#514`, `#515`.
- Update the private VPS deployment from `e1d3e4c` to `b553f86`, rebuild/restart
  the stack, verify Alembic head, API health, public web load, and operator
  browser smoke, then record sanitized evidence: `#520`.

Done when:

- Local/sample and private VPS evidence is recorded without secrets, cookies,
  private trading data, production-readiness claims, profitability claims,
  live/realtime claims, trading advice, broker integration, or automatic
  execution.
- No remaining v3.1 cockpit friction is open in the tracker.

## v3.3 - Signal Quality Calibration Pack

Goal: add safe overnight calibration evidence that tightens regression coverage
around weak setup rejection and missing/stale context without broad strategy
rewrites.

Status: Done.

Primary work:

- Add weak risk/reward golden cases for Trend Pullback Long and Base Breakout
  Long: `#524`.
- Add stored e2e fixture coverage for missing and stale required `4H` trigger
  context: `#523`.
- Refresh calibration evidence status and review follow-up needs: `#525`, `#526`.

Done when:

- Weak R:R cases cannot produce `Watchlist`, `Armed`, or `Triggered`.
- Missing/stale required trigger context remains blocked and conservative.
- Evidence remains deterministic review coverage only, not backtesting,
  profitability validation, live-readiness, broker-readiness, trading advice, or
  automatic execution.

## Next Candidate Increment

Recommended next planning candidate after v3.3: choose between production-like
readiness hardening and another signal-quality calibration pack. Prefer
production-like readiness only if the owner wants to move beyond private
owner/operator staging; otherwise continue with focused paper calibration and
golden-case coverage.

Completed v3.0/v3.1 validation evidence:

- Review follow-up disposition workflow polish: `#506`.
- Mobile Screener candidate review polish: `#507`.
- Mobile Trade Detail workflow grouping polish: `#508`.
- Owner/operator cockpit validation checklist: `#516`.
- Local and operator browser validation evidence: `#514`, `#515`.
- VPS update and browser smoke evidence: `#520`.

Deferred candidates:

- Data-context handoff UI changes, pending a sample browser walkthrough that
  confirms the friction in the app rather than only in documentation.
- Browser smoke automation, pending a separate implementation issue under the
  safe dry-run contract and dependency review.

Alternative next increments after v3.2:

- Production-like readiness hardening, if the owner wants to move beyond private
  owner/operator staging.
- Safe browser smoke automation under the documented dry-run contract.
- Data-context handoff UI improvements, if a fresh browser walkthrough confirms
  the friction in the app.
- Provider/intraday data expansion after cost, license, rate-limit, and safety
  review.
- Additional paper calibration and golden-case coverage before strategy-rule
  changes.

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

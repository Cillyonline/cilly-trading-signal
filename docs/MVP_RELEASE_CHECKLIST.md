# MVP Release Checklist

## Purpose

This checklist records the current MVP v1.2 release-candidate posture for review and handoff. It is not a production-readiness statement, strategy validation, profitability claim, trading advice, or trading recommendation.

## Release Candidate Status

- Version / candidate: v1.2 release candidate.
- Evidence source: [2026-05-17 MVP smoke-test latest run](MVP_SMOKE_TEST.md#latest-run).
- Status: Blocked.
- Reason: the latest documented smoke-test run could not start the Docker Compose stack because the web image build failed before API health, login, CSV import, analysis, signal review, manual paper trade, journal, and performance checks could run.

## Passed

- Release boundary remains documented as a single-user, local or controlled staging review cockpit for long-only swing-trading analysis and manual documentation.
- Safety scope remains explicit: decision-support only, manual trade execution, no broker integration in MVP, no automatic order execution, no profitability claims, and no trading advice.
- Smoke-test tooling prerequisites passed in the latest run: Docker CLI, Docker Compose CLI, Docker engine reachability after Docker Desktop was started, Compose file presence, `.env` presence, and deterministic sample CSV fixture availability. See [MVP smoke-test coverage matrix](MVP_SMOKE_TEST.md#coverage-matrix).
- Operational deployment guidance remains documented in [Deployment Runbook](DEPLOYMENT_RUNBOOK.md), including health checks, deployment smoke steps, secret handling, backup/restore guidance, and safety boundaries.

## Known Gaps

- Dashboard, Journal, Performance, Alerts, and Settings are MVP-level views, not full analytics or operations consoles.
- Risk enforcement covers core manual trade logging rules, not full portfolio exposure, correlation, or account-level risk management.
- Stale signal handling flags old saved signals, but does not refresh market data or re-run strategy automatically.
- Telegram support currently covers explicit operator test messages; production alert routing is not complete.
- TradingView webhook support persists review events, but does not trigger broker execution, auto-trade creation, or automatic Telegram delivery.
- Production monitoring, operational alerting, restore-test evidence, and security review completion are not documented as passed.
- Full mobile app/PWA hardening beyond responsive MVP layouts is not documented as passed.

## Blocked

- Release-candidate smoke validation is blocked by the reproduced Docker Compose startup defect documented in [MVP smoke-test latest run](MVP_SMOKE_TEST.md#latest-run): the web Docker build expects `/app/public`, but no `public` directory existed in the tested checkout. Follow-up: `#132`.
- API health, browser login, watchlist, CSV import, analysis, signal review, manual paper trade logging, trade close, journal, performance, alerts, settings, dashboard, and browser safety-wording checks were not run because stack startup was blocked.
- A complete browser-based end-to-end review is still required before the MVP smoke flow can be marked passed.

## Not Included

- Automatic order execution.
- Broker or exchange integration.
- Buy/sell recommendations, blind trading instructions, or trading advice.
- Profitability, win-rate, backtesting, benchmark, strategy-validation, or real-money readiness claims.
- Live market data, live account sync, or portfolio execution automation.
- Public SaaS operation, multi-tenant isolation, billing, or user onboarding.
- Options, leverage, margin, short-selling strategies, or automated position sizing.

## Release Review Gate Status

| Gate | Status | Evidence |
| --- | --- | --- |
| Release boundary and safety wording documented | Passed | This checklist, [MVP Smoke Test](MVP_SMOKE_TEST.md#safety-scope), and [Deployment Runbook](DEPLOYMENT_RUNBOOK.md#safety-boundaries) keep decision-support and no-execution boundaries explicit. |
| Docker and Compose preflight | Passed | Latest smoke run recorded Docker CLI, Docker Compose CLI, Docker engine reachability, Compose file presence, and `.env` presence as passing. |
| Docker Compose stack startup | Blocked | Latest smoke run recorded stack startup as blocked by the web Docker build defect tracked by `#132`. |
| API health | Not run | Requires successful stack startup. |
| Browser MVP workflow | Not run | Login, watchlist, CSV import, analysis, signal review, manual paper trade, close, journal, performance, alerts, settings, dashboard, and safety-wording review require successful stack startup. |
| Release blocker tracking | Conditional | The known documented startup blocker is linked to `#132`; any additional defects found after the stack starts need follow-up issues. |
| Production readiness | Not passed | No production-readiness gate is documented as passed; deployment docs remain operational guidance only. |

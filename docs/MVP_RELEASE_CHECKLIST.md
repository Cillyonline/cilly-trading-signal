# MVP Release Checklist

## Purpose

This checklist records the current MVP v1.2 release-candidate posture for review and handoff. It is not a production-readiness statement, strategy validation, profitability claim, trading advice, or trading recommendation.

## Release Candidate Status

- Version / candidate: v1.2 release candidate.
- Evidence source: [2026-05-26 MVP smoke-test latest run](MVP_SMOKE_TEST.md#latest-run).
- Status: Staging/VPS-like deployment path passed with a documented UX/auth-guard follow-up.
- Reason: the latest documented rerun rebuilt and started the Docker Compose proxy stack, passed direct and Caddy-routed API health checks, loaded the web app through Caddy, completed the authenticated browser workflow, and confirmed protected API data was not accessible after logout.
- Boundary: this status is not a production-readiness statement, strategy validation, profitability claim, trading advice, or trading recommendation.

## Passed

- Release boundary remains documented as a single-user, local or controlled staging review cockpit for long-only swing-trading analysis and manual documentation.
- Safety scope remains explicit: decision-support only, manual trade execution, no broker integration in MVP, no automatic order execution, no profitability claims, and no trading advice.
- Staging/VPS-like Docker Compose proxy path passed in the latest run: stack rebuild, PostgreSQL health, API running, web running, Caddy running, direct API health, Caddy API health, and Caddy web load. See [MVP smoke-test coverage matrix](MVP_SMOKE_TEST.md#coverage-matrix).
- Frontend API base URL verification passed: bundle grep for `http://localhost:8000/api` returned no output after the `#139` fix.
- Browser workflow passed for login/session, dashboard, watchlist, CSV import, analysis, signals, signal detail, trades page, logout, and protected API data denial after logout.
- Analysis produced a conservative `No Setup` / `No Trade` result. This is valid behavior under the strategy and risk rules, not a failed workflow.
- Operational deployment guidance remains documented in [Deployment Runbook](DEPLOYMENT_RUNBOOK.md), including health checks, deployment smoke steps, secret handling, backup/restore guidance, and safety boundaries.

## Known Gaps

- After logout, opening `/watchlist` still renders the page shell and shows `Watchlist konnte nicht geladen werden` instead of redirecting cleanly to login. This is a UX/auth-guard follow-up gap, not observed protected data exposure.
- Dashboard, Journal, Performance, Alerts, and Settings are MVP-level views, not full analytics or operations consoles.
- Risk enforcement covers core manual trade logging rules, not full portfolio exposure, correlation, or account-level risk management.
- Stale signal handling flags old saved signals, but does not refresh market data or re-run strategy automatically.
- Telegram support currently covers explicit operator test messages; production alert routing is not complete.
- TradingView webhook support persists review events, but does not trigger broker execution, auto-trade creation, or automatic Telegram delivery.
- Production monitoring, operational alerting, restore-test evidence, and security review completion are not documented as passed.
- Full mobile app/PWA hardening beyond responsive MVP layouts is not documented as passed.

## Blocked

- No active release-candidate blocker is documented for `#132` or `#139` in the latest smoke-test rerun.
- Production monitoring, operational alerting, restore-test evidence, and security review completion remain not documented as passed, so production readiness is not claimed.

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
| Docker Compose proxy stack startup | Passed | Latest smoke run recorded successful proxy stack rebuild with Postgres healthy and API, web, and Caddy running. |
| API health | Passed | Direct API health and Caddy-routed API health passed. |
| Web through Caddy | Passed | `curl.exe -k -I https://localhost` returned `HTTP/1.1 200 OK` through Caddy. |
| Frontend API base URL | Passed | Bundle grep for `http://localhost:8000/api` returned no output after `#139`. |
| Browser MVP workflow | Passed | Dashboard, login/session, watchlist, CSV import, analysis, signals, signal detail, trades page, and logout were reviewed in the latest smoke run. |
| Conservative signal behavior | Passed | Sample analysis produced `No Setup` / `No Trade` because of strategy/risk rules; this preserves No Trade as a first-class outcome. |
| Logout protected-data behavior | Passed with UX follow-up | Protected API data was not accessible after logout; `/watchlist` still renders a page shell with an error instead of redirecting cleanly to login. |
| Release blocker tracking | Passed | `#132` and `#139` are no longer documented as active smoke-test blockers; the logout route-shell behavior remains a follow-up gap. |
| Production readiness | Not passed | No production-readiness gate is documented as passed; deployment docs remain operational guidance only. |

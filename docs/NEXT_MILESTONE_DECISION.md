# Next Milestone Decision

Date: 2026-06-04

## Decision

Recommended next milestone: `v4.4 - Provider Evaluation Decision`.

Rationale: all non-secret v3.8-v4.2 radar, CSV workflow, trigger radar,
provider-path, verification, roadmap, private VPS Trigger Radar smoke, and configured
provider Daily/EOD safe-failure smoke work is complete. The next decision is whether
provider reliance should expand beyond guarded Daily/EOD smoke.

## v4.3 - Operational Evidence Closure

Goal: close the remaining operator-run provider evidence gap without expanding
product scope.

Status: Done.

Primary items:

- #614: Provider Daily/EOD smoke after explicit provider-key approval is recorded in
  `docs/reviews/v4-3-provider-daily-eod-smoke.md`. The configured provider path
  reached Alpha Vantage and failed safely with sanitized `provider_rate_limited`
  evidence.

Already closed:

- #605: Trigger Radar VPS smoke after approved deployment passed and is recorded in
  `docs/reviews/v4-2-vps-trigger-radar-smoke.md`.

Done when:

- Evidence is sanitized and references commit, environment class, pass/fail status,
  and issue links only.
- No secrets, provider keys, request URLs, cookies, `.env` values, database URLs,
  private symbols, or broker/account data are recorded.
- No production-readiness, live/realtime, broker-readiness, strategy-validation,
  profitability, or automatic-execution claim is introduced.

## v4.4 - Provider Evaluation Decision

Goal: decide whether provider reliance should expand beyond guarded Daily/EOD smoke.

Inputs required:

- Watchlist size and expected growth.
- Required asset classes, exchanges, symbols, and timeframes.
- Whether `4H`/intraday provider data is required.
- Pricing and rate-limit assumptions.
- Storage/licensing acceptance.
- Secret handling and rollback plan.

Default if inputs are incomplete:

- Keep TradingView CSV as the supported baseline/fallback.
- Keep Alpha Vantage as guarded Daily/EOD smoke only.
- Do not enable scheduler-driven sync or provider reliance for `4H`.

## Not Now

- Broker integration.
- Automatic order execution.
- Automatic trade creation.
- Public SaaS or multi-user operation.
- Live/realtime market-data claims.
- Backtesting or profitability validation claims.

# Provider Sync Smoke Test

## Purpose

This checklist validates the guarded manual market-data provider sync path. It is
operator-run evidence only. It is not a live-data claim, real-time signal claim,
production-readiness statement, broker-readiness statement, trading advice,
profitability claim, or approval for automatic execution.

## Safety Scope

- Provider sync must be triggered manually through the app UI or authenticated API.
- Provider sync must not create signals, trades, alerts, orders, or broker actions.
- Provider sync must not run on a scheduler or background automation in this smoke.
- API keys, provider responses, request URLs, logs, screenshots, watchlist symbols,
  private notes, cookies, and database dumps must not be pasted into issues, PRs,
  docs, chat, or screenshots.
- Use sample symbols or redact private symbols in any evidence.

## Preconditions

- The app is running locally or in a controlled staging environment.
- The operator is authenticated as the single admin user.
- At least one Watchlist item exists for a non-sensitive sample symbol.
- No real provider key is committed to the repository.
- `.env` and provider secrets remain local to the operator environment.

## Disabled-By-Default Check

Configuration shape:

```dotenv
MARKET_DATA_PROVIDER_SYNC_ENABLED=false
MARKET_DATA_PROVIDER=
MARKET_DATA_API_KEY=
```

Manual steps:

1. Start the stack with provider sync disabled.
2. Open the Import page.
3. Select the sample Watchlist item and a timeframe.
4. Click the manual provider sync action.
5. Review the Provider Sync result panel and Import history.

Expected result:

- `sync_status` is `skipped`.
- `sync_error_code` is `sync_disabled`.
- `freshness_status` remains conservative based on stored data.
- Provider name/symbol/timeframe metadata may be shown, but no provider request is
  attempted.
- No signal, trade, order, alert, or analysis is created automatically.

## Configured Provider Check

This check is optional and requires an operator-owned provider key configured outside
the repository. Do not paste the key, full request URL, raw provider response, or
provider account/subscription details into evidence.

Configuration shape:

```dotenv
MARKET_DATA_PROVIDER_SYNC_ENABLED=true
MARKET_DATA_PROVIDER=alpha_vantage
MARKET_DATA_API_KEY=<redacted-real-provider-key>
```

Manual steps:

1. Restart the API after setting the local or staging environment variables.
2. Confirm API health without printing environment values.
3. Open the Import page and select a sample Watchlist item.
4. Request manual provider sync for `1D`.
5. Review the Provider Sync result panel and Import history.
6. Optionally verify the resulting provider-backed series via the authenticated UI or
   sanitized API output.

Expected success result:

- `sync_status` is `success`.
- `source` is `provider`.
- `freshness_status` is derived from the stored latest candle timestamp.
- Provider metadata is populated with sanitized provider name/symbol/timeframe.
- Latest candle timestamp and Import history are visible.
- No automatic analysis, signal, trade, order, broker call, or Telegram alert is
  created.

Expected safe failure results:

- Missing or unsafe provider config fails closed at startup in non-local environments.
- Unsupported timeframe, provider rate limit, invalid provider payload, empty provider
  response, or transport failure produces `failed` or `partial` with sanitized
  `sync_error_code` and `sync_error_message`.
- Failure evidence must not include raw provider payloads, API keys, request URLs with
  query strings, cookies, or private trading data.

## Evidence Template

Record only sanitized evidence:

```text
Date:
Environment: local | private staging
Branch or commit:
Provider sync disabled check: PASS | FAIL | NOT RUN
Configured provider check: PASS | FAIL | NOT RUN
Provider identifier: alpha_vantage | not configured | redacted
Timeframe tested: 1D | other
Observed sync_status: success | skipped | failed | partial
Observed freshness_status: fresh | stale | unknown | failed | partial
Provider metadata visible: PASS | FAIL | NOT RUN
Latest candle timestamp visible: PASS | FAIL | NOT RUN
Import history updated: PASS | FAIL | NOT RUN
No automatic analysis/signal/trade/order/alert created: PASS | FAIL
Secrets/redaction reviewed: PASS | FAIL
Notes:
```

## Final Boundary

A passing provider sync smoke test proves only that a manual, guarded stored-data sync
path behaved as expected in the tested environment. It does not prove live data,
realtime signals, trading readiness, broker readiness, public production readiness,
strategy validity, or profitability.

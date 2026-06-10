# Provider Sync Smoke Test

## Purpose

This checklist validates the guarded manual market-data provider sync path. It is
operator-run evidence only. It is not a live-data claim, real-time signal claim,
production-readiness statement, broker-readiness statement, trading advice,
profitability claim, or approval for automatic execution.

## Safety Scope

- Provider sync must be triggered manually through the app UI action labeled
  `Daten aktualisieren` or through the authenticated API.
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
- Preferred sample symbols are fake or clearly non-private, for example
  `SMOKE-PROVIDER-001` for disabled/failure-path checks or a public liquid symbol
  such as `AAPL` only when a configured provider check requires a provider-recognized
  symbol. Do not use a private watchlist or private notes as smoke evidence.
- No real provider key is committed to the repository.
- `.env` and provider secrets remain local to the operator environment.
- VPS `.env` edits, API restarts, stack restarts, or provider-key rotation require
  explicit owner/operator approval for that environment before they are performed.

## Repeatable Sample-Only Smoke Matrix

Use this matrix before recording evidence. It keeps the smoke path deterministic
without requiring private symbols, screenshots, raw logs, or provider secrets.

| Path | Symbol scope | Provider config | Expected result |
| --- | --- | --- | --- |
| Disabled path | Fake sample Watchlist symbol such as `SMOKE-PROVIDER-001` | `MARKET_DATA_PROVIDER_SYNC_ENABLED=false` | `sync_status=skipped`, no provider request, no automatic analysis/signal/trade/alert. |
| Failure path | Fake or public sample symbol | Enabled with mocked/local failure or known unsupported mapping | `sync_status=failed` or `partial`, sanitized error code/message only. |
| Success path | Public provider-recognized sample symbol only | Enabled with operator-owned key outside git | `sync_status=success`, provider-backed stored data visible, no automatic downstream workflow. |

Capability expectations for the current first provider path:

- Alpha Vantage is the guarded Daily/EOD smoke path.
- `1D` is the only supported provider-sync timeframe in this path.
- `1W` and `4H` must be explained as unsupported provider-sync timeframes and
  should point the operator back to TradingView CSV fallback.
- Unsupported timeframe responses should use sanitized `sync_error_code`, typically
  `unsupported_timeframe`, without raw provider payloads or secrets.

For local automated/API tests, prefer the mocked provider tests in
`apps/api/tests/test_imports_api.py` and `apps/api/tests/test_market_data_sync.py`.
Those tests validate success, skipped, failed, partial, and sanitized-error behavior
without network dependency or provider secrets. Browser smoke evidence should remain
manual and sample-only unless a separate automation issue explicitly implements a
safe harness.

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
4. Click the manual `Daten aktualisieren` action.
5. Review the Aktualisierungs-Ergebnis panel, capability hints, and Import history.

Optional API shape for local sample-only checks after authenticating through safe
local tooling. Do not paste cookies or session headers into evidence:

```http
POST /api/imports/sync
Content-Type: application/json

{
  "watchlist_item_id": <sample-watchlist-id>,
  "timeframe": "1D"
}
```

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

For VPS or private staging, do not set, rotate, remove, or print the provider key
as part of this checklist unless the owner/operator explicitly approved that exact
operation. Record only sanitized status evidence after the operator-approved change.

Configuration shape:

```dotenv
MARKET_DATA_PROVIDER_SYNC_ENABLED=true
MARKET_DATA_PROVIDER=twelve_data
MARKET_DATA_API_KEY=<redacted-real-provider-key>
```

The clean provider path uses Twelve Data with an operator-owned API key. Keep
TradingView CSV as the fallback and do not use this evidence as production-readiness
proof.

Manual steps:

1. Restart the API after setting the local or staging environment variables.
2. Confirm API health without printing environment values.
3. Open the Import page and select a sample Watchlist item.
4. Request manual data update for `1W`, `1D`, and `4H` with `Daten aktualisieren`.
5. Review the Aktualisierungs-Ergebnis panel, capability hints, and Import history.
6. Optionally verify the resulting provider-backed series via the authenticated UI or
   sanitized API output.

Expected success result:

- `sync_status` is `success`.
- `source` is `provider`.
- `freshness_status` is derived from the stored latest candle timestamp.
- Provider metadata is populated with sanitized provider name/symbol/timeframe.
- Provider capability hints match the configured provider. For `twelve_data`, `1W`,
  `1D`, and `4H` are supported for manual stored-data review.
- Latest candle timestamp and Import history are visible.
- No automatic analysis, signal, trade, order, broker call, or Telegram alert is
  created.

Expected safe failure results:

- Missing or unsafe provider config fails closed at startup in non-local environments.
- Unsupported timeframe, provider rate limit, invalid provider payload, empty provider
  response, or transport failure produces `failed` or `partial` with sanitized
  `sync_error_code` and `sync_error_message`.
- If Twelve Data plan limits, entitlements, symbol mapping, rate limits, or provider
  payload shape block a timeframe, the result should stay sanitized and conservative.
- Failure evidence must not include raw provider payloads, API keys, request URLs with
  query strings, cookies, or private trading data.

## Cleanup And Repeatability

- Keep sample provider-smoke Watchlist symbols clearly prefixed, such as
  `SMOKE-PROVIDER-`.
- Do not reset staging volumes, rotate secrets, restart VPS services, or edit `.env`
  as a smoke cleanup step without explicit operator approval.
- If provider sync must be rolled back after an approved VPS test, disable
  `MARKET_DATA_PROVIDER_SYNC_ENABLED`, restart only with approval, and confirm a
  skipped manual data update without printing `.env` or provider request details.
- For local disposable runs, use the documented local smoke cleanup path; otherwise
  prefer adding a new fake sample symbol for the next run.
- If a configured provider check used a public symbol, record only sanitized status
  evidence and not the raw payload, request URL, or account/subscription details.

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
Sample symbol scope: fake sample | public provider-recognized | redacted
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

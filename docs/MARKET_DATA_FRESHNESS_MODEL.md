# Market Data Source And Freshness Model

## Purpose

This document defines the implemented market-data source, freshness, and stale-data
model for TradingView CSV imports and guarded manual provider sync.

This is not a live-data claim, real-time signal claim,
production-readiness statement, trading advice, profitability claim, broker-readiness
claim, or approval for automatic execution.

## Goals

- Track whether market data came from CSV or a provider-backed sync.
- Track freshness per symbol and timeframe.
- Make stale, failed, partial, and unknown data visible and conservative.
- Preserve existing TradingView CSV workflows.
- Prevent old or incomplete data from looking trader-actionable.

## Source Model

Every market-data series should have an explicit source.

Implemented source values:

- `tradingview_csv`: uploaded TradingView CSV import.
- `provider`: provider-backed sync persisted through the manual sync path.
- `manual`: reserved for future operator-created data points, not used by current MVP.
- `unknown`: fallback only; must be treated conservatively.
- `api_later`: legacy placeholder accepted for existing early data only.

Provider-backed data should additionally track provider identity without making the
schema depend on one vendor.

Implemented provider fields:

- `provider_name`: symbolic provider identifier. Implemented active runtime values
  are `twelve_data` and `alpha_vantage`; other providers remain future candidates
  until a separate adapter and provider decision are added.
- `provider_symbol`: provider-specific symbol used for the request.
- `provider_exchange`: optional provider-specific exchange or venue code.
- `provider_timeframe`: provider-specific timeframe/granularity.

CSV-backed data should continue to track the uploaded filename or sanitized import
reference when available.

## Freshness Metadata

Freshness must be evaluated per symbol/timeframe, not globally.

Implemented fields for the latest data state:

- `source`: `tradingview_csv`, `provider`, `manual`, `unknown`, or legacy `api_later`.
- `timeframe`: `1W`, `1D`, or `4H`.
- `start_time`: earliest candle timestamp in the series.
- `end_time`: latest candle timestamp in the series.
- `imported_at`: when the series was first imported or created.
- `last_synced_at`: when a provider sync attempt completed, if applicable.
- `freshness_status`: `fresh`, `stale`, `unknown`, `failed`, or `partial`.
- `sync_status`: `not_applicable`, `success`, `skipped`, `failed`, or `partial`.
- `sync_error_code`: sanitized machine-readable failure category, if any.
- `sync_error_message`: sanitized human-readable failure summary, if any.

Do not store provider API keys, request authorization headers, raw secret-bearing
payloads, or account/subscription details in these fields.

## Freshness Status Rules

Freshness status should be derived conservatively.

Implemented rules:

- `fresh`: data exists for the expected symbol/timeframe and is inside the configured
  freshness window.
- `stale`: data exists but is older than the configured freshness window.
- `unknown`: migration fallback, missing metadata, or unclear source state.
- `failed`: the latest provider sync failed and no newer successful data exists.
- `partial`: some data was imported/synced, but expected candles, timeframes, or ranges
  are incomplete.

Implemented freshness windows:

- `1W`: stale after 14 days without newer data.
- `1D`: stale after 3 days without newer data.
- `4H`: stale after 24 hours without newer data.

These windows are conservative defaults for review visibility only. They are not a
claim that data is live or real-time.

## Sync Status Rules

Sync status should describe the latest sync/import attempt separately from whether
the available data is fresh.

Implemented values:

- `not_applicable`: CSV/manual data with no provider sync attempt.
- `success`: provider sync completed and persisted expected data.
- `skipped`: sync was intentionally skipped, for example disabled provider config.
- `failed`: sync attempted and failed without usable new data.
- `partial`: sync persisted some data but not the complete expected range/timeframe.

Examples:

- CSV upload from yesterday: `source=tradingview_csv`, `sync_status=not_applicable`,
  `freshness_status=fresh` for `1D`.
- Provider error with old data still present: `source=provider`, `sync_status=failed`,
  `freshness_status=stale` if the old data is outside the freshness window.
- Provider returns only daily data while `4H` was expected: `sync_status=partial`,
  `freshness_status=partial` for the missing `4H` series.

## Provider Failure States And Operator Recovery

Provider sync failures are manual/operator recovery events. They do not trigger
automatic orders, automatic analysis refreshes, broker actions, or buy/sell
instructions.

| Failure state | Typical evidence | Stored state | Operator recovery |
| --- | --- | --- | --- |
| Provider disabled | Sync is requested while provider sync is disabled or not configured. | `sync_status=skipped`, freshness remains existing state or `unknown`. | Keep CSV/manual workflow; enable provider config only through approved environment changes. |
| Auth/config failure | Missing API key, unsupported provider, invalid symbol mapping, or rejected credentials. | `sync_status=failed`, `freshness_status=failed` or unchanged stale state, sanitized `sync_error_code`. | Fix provider settings outside git, rerun manual sync, and avoid posting credentials or raw URLs. |
| Rate limit or transport failure | Timeout, network failure, HTTP error, provider rate limit, or temporary outage. | `sync_status=failed`, `freshness_status=failed` when no usable newer data exists. | Wait or reduce request scope, then rerun manual sync; fall back to CSV if review is time-sensitive. |
| Empty or invalid payload | Provider response cannot be parsed or contains no usable candles. | `sync_status=partial` or `failed`, `freshness_status=partial` or `failed`, sanitized error code. | Verify provider symbol/timeframe mapping; use known-good CSV data until resolved. |
| Partial coverage | Some candles/timeframes persist but required review context is incomplete. | `sync_status=partial`, `freshness_status=partial`. | Do not treat setup as current; fill missing timeframe via supported manual workflow before analysis. |
| Stale existing data | Old data remains after failed or skipped sync. | `freshness_status=stale` or `unknown` depending on metadata. | Treat existing signals as historical review only; refresh data before current setup review. |

Recovery evidence should include only sanitized facts: symbol category or fake/public
symbol, timeframe, sync status, freshness status, error code category, timestamp,
and whether a follow-up issue was created. Do not include API keys, request URLs
with tokens, account/subscription details, raw provider payloads, cookies, database
URLs, or private trading notes.

## Strategy And Signal Behavior

Strategy code must treat insufficient freshness as a conservative review blocker.

Rules:

- Fresh data may be used for normal deterministic analysis.
- Stale data may remain visible for historical review but must not be presented as a
  current actionable setup.
- Failed, partial, or unknown data should add explicit no-trade reasons or block new
  current-review signal generation until resolved.
- Existing stale signal visibility remains useful, but stale signals must not trigger
  automatic delivery as if current.
- `No Trade` remains the correct outcome when required timeframe data is stale,
  missing, failed, partial, or unknown.

Suggested no-trade reason labels:

- `market_data_stale`
- `market_data_missing_timeframe`
- `market_data_sync_failed`
- `market_data_partial`
- `market_data_source_unknown`

## Migration Direction

Existing imported CSV series migrate without changing candle values.

Migration defaults for existing rows:

- `source=tradingview_csv` for current TradingView CSV imports.
- `sync_status=not_applicable`.
- `provider_name`, `provider_symbol`, `provider_exchange`, and `provider_timeframe`
  unset.
- `imported_at` remains the import timestamp.
- `freshness_status` derived after migration from `data_end_at` and timeframe.

If source cannot be inferred safely, use `source=unknown` and treat the data
conservatively until re-imported or re-synced.

## UI/API Expectations

API responses and UI expose source and freshness clearly.

Minimum display expectations:

- Data source: CSV, Provider, Manual, or Unknown.
- Timeframe freshness: Fresh, Stale, Failed, Partial, or Unknown.
- Last data timestamp and last import/sync timestamp when available.
- Conservative wording for stale/failed/partial data.

UI must not present stale, failed, partial, or unknown data with the same visual weight
as fresh data.

## Final Statement

The freshness model exists to make market-data provenance and age explicit for both
CSV and provider-backed stored data. It should reduce the risk of old or incomplete
data being mistaken for current, trader-actionable information.

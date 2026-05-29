# Market Data Source And Freshness Model

## Purpose

This document defines the planned v1.4 market-data source, freshness, and stale-data
model before database or provider implementation.

This is a planning artifact. It is not a live-data claim, real-time signal claim,
production-readiness statement, trading advice, profitability claim, broker-readiness
claim, or approval for automatic execution.

## Goals

- Track whether market data came from CSV or a future provider sync.
- Track freshness per symbol and timeframe.
- Make stale, failed, partial, and unknown data visible and conservative.
- Preserve existing TradingView CSV workflows.
- Prevent old or incomplete data from looking trader-actionable.

## Source Model

Every market-data series should have an explicit source.

Recommended source values:

- `csv`: uploaded TradingView CSV or equivalent manual import.
- `provider`: future provider-backed sync.
- `manual`: reserved for future operator-created data points, not used by current MVP.
- `unknown`: migration fallback only; must be treated conservatively.

Provider-backed data should additionally track provider identity without making the
schema depend on one vendor.

Recommended provider fields:

- `provider_name`: symbolic provider identifier, for example `alpha_vantage`,
  `twelve_data`, `polygon`, or `tiingo`.
- `provider_symbol`: provider-specific symbol used for the request.
- `provider_exchange`: optional provider-specific exchange or venue code.
- `provider_timeframe`: provider-specific timeframe/granularity.

CSV-backed data should continue to track the uploaded filename or sanitized import
reference when available.

## Freshness Metadata

Freshness must be evaluated per symbol/timeframe, not globally.

Recommended fields for the latest data state:

- `source`: `csv`, `provider`, `manual`, or `unknown`.
- `timeframe`: `1W`, `1D`, or `4H`.
- `data_start_at`: earliest candle timestamp in the series.
- `data_end_at`: latest candle timestamp in the series.
- `last_imported_at`: when CSV data was imported or provider data was persisted.
- `last_synced_at`: when a provider sync attempt completed, if applicable.
- `freshness_status`: `fresh`, `stale`, `unknown`, `failed`, or `partial`.
- `sync_status`: `not_applicable`, `success`, `skipped`, `failed`, or `partial`.
- `sync_error_code`: sanitized machine-readable failure category, if any.
- `sync_error_message`: sanitized human-readable failure summary, if any.

Do not store provider API keys, request authorization headers, raw secret-bearing
payloads, or account/subscription details in these fields.

## Freshness Status Rules

Freshness status should be derived conservatively.

Suggested initial rules:

- `fresh`: data exists for the expected symbol/timeframe and is inside the configured
  freshness window.
- `stale`: data exists but is older than the configured freshness window.
- `unknown`: migration fallback, missing metadata, or unclear source state.
- `failed`: the latest provider sync failed and no newer successful data exists.
- `partial`: some data was imported/synced, but expected candles, timeframes, or ranges
  are incomplete.

Suggested initial freshness windows:

- `1W`: stale after 14 days without newer data.
- `1D`: stale after 3 days without newer data.
- `4H`: stale after 24 hours without newer data.

These windows are conservative defaults for review visibility only. They are not a
claim that data is live or real-time.

## Sync Status Rules

Sync status should describe the latest sync/import attempt separately from whether
the available data is fresh.

Recommended values:

- `not_applicable`: CSV/manual data with no provider sync attempt.
- `success`: provider sync completed and persisted expected data.
- `skipped`: sync was intentionally skipped, for example disabled provider config.
- `failed`: sync attempted and failed without usable new data.
- `partial`: sync persisted some data but not the complete expected range/timeframe.

Examples:

- CSV upload from yesterday: `source=csv`, `sync_status=not_applicable`,
  `freshness_status=fresh` for `1D`.
- Provider error with old data still present: `source=provider`, `sync_status=failed`,
  `freshness_status=stale` if the old data is outside the freshness window.
- Provider returns only daily data while `4H` was expected: `sync_status=partial`,
  `freshness_status=partial` for the missing `4H` series.

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

Existing imported CSV series should migrate without changing candle values.

Recommended migration defaults for existing rows:

- `source=csv` for current TradingView CSV imports.
- `sync_status=not_applicable`.
- `provider_name`, `provider_symbol`, `provider_exchange`, and `provider_timeframe`
  unset.
- `last_imported_at` from existing `imported_at` when available.
- `freshness_status` derived after migration from `data_end_at` and timeframe.

If source cannot be inferred safely, use `source=unknown` and treat the data
conservatively until re-imported or re-synced.

## UI/API Expectations

Future API responses and UI should expose source and freshness clearly.

Minimum display expectations:

- Data source: CSV, Provider, Manual, or Unknown.
- Timeframe freshness: Fresh, Stale, Failed, Partial, or Unknown.
- Last data timestamp and last import/sync timestamp when available.
- Conservative wording for stale/failed/partial data.

UI must not present stale, failed, partial, or unknown data with the same visual weight
as fresh data.

## Final Statement

The v1.4 freshness model exists to make market-data provenance and age explicit before
provider integration. It should reduce the risk of old or incomplete data being
mistaken for current, trader-actionable information.

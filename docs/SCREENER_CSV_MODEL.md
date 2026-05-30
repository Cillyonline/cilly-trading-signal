# Screener CSV Import Model

## Purpose

This document defines the intended TradingView screener CSV import model for review candidates. Screener CSV imports are a prefiltering workflow for many symbols; they do not create trades, broker orders, automatic signals, or trading advice.

The model is a design target for the v1.9 implementation issues. It intentionally separates raw screener rows from confirmed Watchlist items.

## Safety Boundaries

- Screener rows are manual review candidates only.
- Importing a screener CSV must not create trades or orders.
- Importing a screener CSV must not automatically create signals or run analysis.
- Adding a screener result to the Watchlist requires an explicit user action.
- Screener data is a snapshot from an uploaded file, not live or realtime market data.
- Numeric screener metrics are context fields, not predictions or profitability claims.

## Workflow

1. User exports a TradingView screener CSV outside the app.
2. User uploads the CSV in the app and selects default asset class/source context if needed.
3. Backend validates headers, rows, symbols, numeric fields, and row count limits.
4. Backend stores one `ScreenerImport` and normalized `ScreenerResult` rows.
5. User reviews results with filters and validation warnings.
6. User explicitly converts selected results into Watchlist candidates.
7. Existing Watchlist, market-data import/provider sync, and analysis workflows remain separate.

## Expected CSV Inputs

TradingView screener exports vary by selected columns and locale. The import should support a conservative normalized subset first.

Required columns:

| Normalized Field | Accepted Header Examples | Notes |
| --- | --- | --- |
| `symbol` | `Symbol`, `Ticker`, `Ticker No.` | Required, normalized uppercase/trimmed. |

Recommended columns:

| Normalized Field | Accepted Header Examples | Notes |
| --- | --- | --- |
| `name` | `Name`, `Description`, `Company` | Optional display text. |
| `exchange` | `Exchange`, `Market` | Optional venue context. |
| `sector` | `Sector` | Optional stock context. |
| `industry` | `Industry` | Optional stock context. |
| `currency` | `Currency` | Optional; useful for stocks. |
| `price` | `Price`, `Last`, `Close` | Optional numeric snapshot. |
| `change_percent` | `Change %`, `Change % 1D` | Optional numeric snapshot. |
| `volume` | `Volume` | Optional numeric snapshot. |
| `relative_volume` | `Relative Volume`, `Rel Volume` | Optional numeric snapshot. |
| `market_cap` | `Market Cap`, `Market capitalization` | Optional numeric snapshot. |
| `rsi14` | `RSI (14)`, `RSI14` | Optional numeric indicator snapshot. |
| `ema20` | `EMA20`, `Exponential Moving Average (20)` | Optional numeric indicator snapshot. |
| `ema50` | `EMA50`, `Exponential Moving Average (50)` | Optional numeric indicator snapshot. |
| `ema200` | `EMA200`, `Exponential Moving Average (200)` | Optional numeric indicator snapshot. |

Import metadata selected by the user or inferred conservatively:

- `asset_class`: `stock` or `crypto`; required if it cannot be inferred.
- `source_name`: default `tradingview_screener_csv`.
- `file_name`: sanitized original upload filename.
- `screener_preset`: optional user label such as `US growth pullback`.
- `snapshot_at`: optional timestamp from the file or user input; otherwise import time.

Unknown CSV columns should not fail the import by default. Preserve unrecognized values in row metadata only after sanitizing headers and limiting size.

## Entity Design

### ScreenerImport

Purpose: one uploaded screener CSV file and its validation/import summary.

Fields:

- `id`
- `user_id`
- `source`
- `file_name`
- `asset_class`
- `screener_preset`
- `snapshot_at`
- `row_count`
- `accepted_count`
- `rejected_count`
- `duplicate_count`
- `status`
- `validation_errors`
- `created_at`

Values:

- `source`: `tradingview_screener_csv`
- `asset_class`: `stock`, `crypto`
- `status`: `pending`, `validated`, `failed`, `imported`, `partial`

Notes:

- `validation_errors` stores sanitized file-level errors and warnings.
- `partial` means at least one row was accepted and at least one row was rejected or deduplicated with warning.
- Do not store raw files, secrets, browser cookies, or local paths.

### ScreenerResult

Purpose: one normalized row from a screener import that can be reviewed and optionally converted into a Watchlist candidate.

Fields:

- `id`
- `screener_import_id`
- `user_id`
- `watchlist_item_id`
- `symbol`
- `name`
- `asset_class`
- `exchange`
- `currency`
- `sector`
- `industry`
- `price`
- `change_percent`
- `volume`
- `relative_volume`
- `market_cap`
- `rsi14`
- `ema20`
- `ema50`
- `ema200`
- `rank`
- `status`
- `duplicate_of_result_id`
- `validation_errors`
- `raw_metadata`
- `created_at`
- `updated_at`

Values:

- `status`: `candidate`, `watchlist_added`, `duplicate`, `rejected`, `ignored`

Notes:

- `watchlist_item_id` remains empty until explicit user confirmation creates or links a Watchlist item.
- `raw_metadata` stores small sanitized extra fields for audit; it must not store full unbounded row data.
- `rank` is the CSV row order after header normalization, not an investment ranking.

## Validation Rules

File-level validation:

- CSV must be parseable as text.
- Header row is required.
- `symbol` equivalent column is required.
- Row count must be above zero and below the configured maximum.
- Asset class must be selected or safely inferred.
- Empty files, binary files, and oversized files fail closed.

Row-level validation:

- `symbol` is required after trim.
- `symbol` must use a conservative allowlist such as letters, numbers, dot, dash, underscore, colon, slash, and equals where needed for provider/ticker formats.
- `symbol` is normalized to uppercase.
- `asset_class` must be `stock` or `crypto`.
- Numeric fields must parse with locale-tolerant cleanup for commas, percent signs, and compact suffixes where explicitly supported.
- Invalid optional numeric fields should reject or warn the row rather than silently inventing values.
- Text fields should be trimmed and length-limited.
- Validation errors must be sanitized and must not echo entire raw rows when they may contain private notes.

Recommended row count limits:

- MVP default max accepted rows: 500.
- Hard max upload rows: 2,000.
- Later limits can be raised only after UI and API pagination are confirmed.

## Dedupe Behavior

Dedupe should happen in layers:

1. Within one import, normalize by `user_id + asset_class + symbol + exchange` where exchange is available.
2. Across previous screener results, mark repeated candidates as duplicates if an unresolved candidate already exists for the same normalized key.
3. Against Watchlist, mark result as already represented when an active or inactive Watchlist item exists for the same normalized key.

Dedupe outcomes:

- Keep the first valid row in an import as `candidate`.
- Mark later same-import duplicates as `duplicate` and link `duplicate_of_result_id` where possible.
- Do not automatically update existing Watchlist items from duplicate screener rows.
- User may still inspect duplicate rows, but conversion should explain the existing Watchlist link.

## Watchlist Conversion

Converting a result to Watchlist is explicit and user-driven.

Allowed behavior:

- Create a new `WatchlistItem` from selected `ScreenerResult` fields.
- Link `ScreenerResult.watchlist_item_id` to the created or existing Watchlist item.
- Set result status to `watchlist_added` after successful conversion.
- Preserve screener import metadata for audit.

Disallowed behavior:

- No automatic trade creation.
- No automatic signal creation.
- No automatic market-data import or provider sync.
- No automatic analysis run.
- No broker or order action.

## API Boundaries For Follow-Up Issues

Suggested endpoints:

- `POST /api/screener/imports`: upload and validate a TradingView screener CSV.
- `GET /api/screener/imports`: list imports and summaries.
- `GET /api/screener/imports/{id}`: retrieve import detail and result counts.
- `GET /api/screener/results`: list/filter stored results.
- `POST /api/screener/results/{id}/watchlist`: explicitly convert one result into a Watchlist candidate.

API responses should include:

- Import status and sanitized validation summary.
- Result-level status, duplicate flags, Watchlist linkage, and normalized display fields.
- Pagination or limit information before row limits are raised.

## UI Boundaries For Follow-Up Issues

Suggested page behavior:

- Upload form with asset class, optional preset label, and clear manual-review copy.
- Import summary showing accepted, rejected, duplicate, and partial counts.
- Results table/cards with filters for status, asset class, exchange, sector, duplicate state, and Watchlist linkage.
- Per-result action to add/link to Watchlist.
- Empty and error states that distinguish validation failure from no candidates.

UI copy must describe screener rows as candidates or review inputs, never as recommendations.

## Implementation Sequence

Recommended v1.9 follow-ups:

1. Add backend schema/models and migration for `ScreenerImport` and `ScreenerResult`.
2. Add CSV validation and normalization service with tests.
3. Add authenticated API routes for imports/results.
4. Add results UI for reviewing imports and candidates.
5. Add explicit conversion from screener result to Watchlist item.

## Open Questions

- Whether to infer `asset_class=crypto` from common quote suffixes such as `USDT`, or require explicit selection for the first implementation.
- Whether to preserve unrecognized columns in `raw_metadata` from day one or only store normalized fields first.
- Whether import replacement should archive older candidates for the same preset or leave all import snapshots visible.

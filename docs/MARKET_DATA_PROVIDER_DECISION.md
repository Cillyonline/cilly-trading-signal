# Market Data Provider Decision

## Purpose

This document records the market-data provider decision matrix and the current
manual provider-backed data sync scope.

This is not a live-trading claim, real-time signal claim,
production-readiness statement, broker-readiness claim, profitability claim, trading
advice, or approval for automatic execution.

## Decision Summary

Status: First practical provider path selected for guarded Daily/EOD stock sync;
broader provider reliance remains deferred.

Current decision:

- Keep TradingView CSV import as a supported data source.
- Keep provider-neutral configuration, source metadata, freshness metadata, and sync
  status handling independent of any one vendor.
- Treat Daily/EOD data as the first practical provider-backed target.
- Use Alpha Vantage as the first implemented adapter path for Daily/EOD sync behind
  the provider boundary.
- Keep Alpha Vantage as the current practical first path for US-stock Daily/EOD
  smoke and operator learning because it is already implemented and sufficient to
  validate provider plumbing, freshness states, and failure handling.
- Defer a paid/production-like provider decision until provider terms, symbol
  coverage, storage rights, rate limits, and `4H` availability are reviewed against
  the actual watchlist size.
- Keep `4H`/intraday provider support unresolved until provider cost, licensing, and
  rate-limit constraints are confirmed.
- Do not claim live, real-time, or trader-actionable data freshness from manual
  provider sync.

## Safety Boundaries

- No broker integration.
- No automatic order execution.
- No buy/sell instructions.
- No profitability, win-rate, or prediction claims.
- No real-time market-data claim until a provider with documented latency and
  licensing is integrated and verified.
- Stale, partial, failed, or unknown data must remain visible and conservative.
- `No Trade` remains a first-class outcome when data freshness is insufficient.
- API keys, account IDs, subscription details, and provider secrets must not be
  committed or pasted into docs, issues, PRs, logs, screenshots, or chat.

## Data Handling And Privacy Boundary

Provider-backed market data introduces two separate data classes:

1. Stored candle/freshness metadata used by the app.
2. Provider credentials, account/subscription details, request URLs, and raw payloads
   that must stay outside repository and evidence channels.

Allowed to store in PostgreSQL for guarded manual sync:

- OHLCV candles returned by the configured provider for the requested symbol/timeframe.
- Sanitized provider metadata: `provider_name`, `provider_symbol`, optional
  `provider_exchange`, and `provider_timeframe`.
- Sync/freshness state: `sync_status`, `freshness_status`, `last_synced_at`, sanitized
  `sync_error_code`, and sanitized `sync_error_message`.

Forbidden in git, issues, PRs, docs, screenshots, chat, and routine evidence:

- API keys, bearer tokens, request authorization headers, signed URLs, full request
  URLs with query strings, provider account IDs, subscription tier details, invoices,
  or billing identifiers.
- Raw provider payloads when they include request metadata, entitlement details,
  account context, or error output that could reveal secrets or subscription state.
- Private watchlists, private trading notes, broker/account/fill data, personal journal
  details, cookies, session headers, database URLs, backups, or restored row contents.

Allowed evidence examples:

- `sync_status=skipped`, `sync_error_code=sync_disabled` for a fake sample symbol.
- `sync_status=failed`, `sync_error_code=provider_rate_limited` without raw response.
- `freshness_status=partial` for `1D`/`4H` context with a fake or public sample symbol.
- `provider_name=alpha_vantage`, `timeframe=1D`, latest candle timestamp redacted or
  shown only when it is not private.

Disallowed evidence examples:

- `.env` snippets with real provider keys.
- Full URLs such as `https://provider.example/query?...apikey=...`.
- Raw JSON/XML provider responses copied from logs.
- Screenshots showing private symbols, account/provider dashboards, cookies, or local
  storage values.

When in doubt, record only pass/fail, status enum, error-code category, timeframe,
environment class, and a follow-up issue link.

## v4.1 Practical Provider Comparison

This comparison is for provider-path planning only. It does not configure API keys,
select a subscription, approve storing provider data beyond current guarded scope,
or create any live/realtime data claim.

| Provider | US Stocks | `1D` / EOD | `4H` / Intraday | Main Strength | Main Risk | Practical v4.1 Position |
| --- | --- | --- | --- | --- | --- | --- |
| Twelve Data | Broad coverage depending on plan | Supported on relevant plans | Supported depending on plan and entitlement | One API surface for daily and intraday; potentially useful if `4H` becomes required. | Plan/entitlement, symbol mapping, and storage/licensing terms need confirmation. | Candidate for a later paid provider evaluation, not immediate default. |
| Tiingo | Strong US equities focus depending on plan | Strong daily/equity fit | Intraday availability depends on plan/API | Good fit for adjusted daily US-stock data and clearer equity focus. | Intraday/crypto coverage and storage terms need confirmation. | Candidate if Daily/EOD quality is prioritized over unified stock/crypto coverage. |
| Polygon.io | Strong US market coverage on paid plans | Supported | Strong paid intraday support | High-quality US-stock/intraday path if budget and licensing fit. | Cost, entitlement complexity, and production-like licensing burden. | Candidate for later serious intraday path, not low-friction first step. |
| EODHD | Broad EOD-oriented market coverage depending on plan | Strong EOD fit | Intraday availability depends on plan | Practical EOD-first vendor with broad symbol coverage. | Intraday details, exchange entitlements, and storage terms need review. | Candidate for Daily/EOD replacement if Alpha Vantage proves limiting. |
| Alpha Vantage | Broad public symbols, plan-dependent reliability | Supported and already implemented | Intraday exists but rate limits and `4H` construction need caution | Already implemented; good for validating guarded provider plumbing with no new code path. | Free/low-cost rate limits, adjusted-data details, and reliability may limit scale. | Current practical first path for guarded Daily/EOD smoke only. |

Recommendation:

- Keep Alpha Vantage as the first practical provider path for the next controlled
  Daily/EOD smoke because the adapter and tests already exist.
- Do not expand provider reliance to `4H`, automated refresh, or production-like use
  yet.
- Keep TradingView CSV as the required fallback and the only currently reliable way
  to fill all `1W`, `1D`, and `4H` timeframes for multi-timeframe analysis.
- Revisit Twelve Data, Tiingo, Polygon, and EODHD only after recording watchlist size,
  required symbols/exchanges, expected sync frequency, budget, and storage/licensing
  acceptance.

Deferral:

- No paid provider is selected in this issue.
- No provider secret, API key, account ID, subscription tier, or VPS setting is added.
- No provider is approved as live/realtime or broker/execution-ready.

## Candidate Provider Matrix

| Candidate | Stocks | Crypto | EOD/Daily | Intraday/4H | Operational Notes | v1.4 Fit |
| --- | --- | --- | --- | --- | --- | --- |
| TradingView CSV | Manual export only | Manual export only | Yes, via upload | Yes, via upload if exported manually | Already implemented; no provider key; manual and repeatable but not automated. | Keep as baseline and fallback. |
| Alpha Vantage | Broad public-market coverage depends on plan | Limited crypto/FX coverage | Yes | Intraday exists but rate limits and adjusted-history details require review | Simple API shape; free/low-cost tiers can be restrictive; licensing must be checked before reliance. | First implemented guarded Daily/EOD adapter path. |
| Twelve Data | Stocks/ETFs/FX depending on plan | Crypto support depending on plan | Yes | Intraday support depending on plan | Broad API surface; pricing and symbol mapping need review. | Candidate if combined stock/crypto coverage is prioritized. |
| Polygon.io | Strong US market coverage depending on subscription | Crypto support depending on subscription | Yes | Strong intraday support on paid tiers | Higher-quality option but cost/licensing likely higher; useful if intraday becomes required. | Candidate for later paid/intraday path, not first low-risk default. |
| Tiingo | US equities and ETFs depending on plan | Some crypto data depending on plan | Yes | Intraday depends on plan/API | Often suitable for adjusted daily equity data; crypto/intraday needs confirmation. | Candidate for daily stock data if licensing is acceptable. |
| Yahoo Finance unofficial libraries | Broad visible coverage | Some crypto symbols | Yes | Some intraday windows | Unofficial interfaces can break and may have unclear terms; avoid relying on scraping-like paths for staging operations. | Not recommended for operational provider integration. |
| Exchange-native crypto APIs | No | Exchange-specific | Yes, via candles | Yes | Good crypto candle availability, but symbol/exchange mapping and per-exchange quirks add complexity. | Candidate for later crypto-specific integration, not first unified provider. |

## Implemented Scope

The current implementation adds manual provider sync without binding domain models to
one vendor.

Included:

- Provider selection documentation and decision record.
- Environment configuration placeholders and safety guards.
- Data source metadata for `tradingview_csv` and `provider` data.
- Freshness metadata by symbol/timeframe.
- Sync result states such as `success`, `skipped`, `failed`, and `partial`.
- UI/API wording that distinguishes CSV, provider, stale, failed, partial, and unknown
  data.
- Authenticated manual `POST /api/imports/sync` endpoint.
- Provider-backed candle persistence for provider series only.
- First Alpha Vantage Daily/EOD provider adapter with mocked tests.

Not included:

- Scheduler-driven imports.
- Live price display.
- Automatic signal generation from provider data.
- Real-time alerting claims.
- Broker or execution functionality.

## Open Provider Questions

- Which provider has acceptable licensing for private staging and later production-like
  use?
- Which provider covers both the desired stock universe and major crypto coins without
  excessive symbol-mapping complexity?
- Is Daily/EOD enough for the first provider-backed release, or is `4H` required before
  the feature is useful?
- What are the rate limits for syncing the current watchlist size plus future growth?
- How are adjusted prices, splits, dividends, and crypto exchange differences handled?
- What is the maximum acceptable data delay before the UI must mark data as stale?

## Unsupported Or Deferred Needs

- Tick data is out of scope.
- Level 2/order-book data is out of scope.
- Broker fills, account positions, and portfolio sync are out of scope.
- Automatic order execution is out of scope.
- Multi-provider fallback is out of scope for the first integration.
- Guaranteed real-time 4H/intraday coverage is unresolved until provider selection.

## Review Gate For Broader Provider Reliance

Before relying on broader provider coverage, intraday data, or production-like use, a
follow-up issue must document:

- Selected provider and subscription tier assumptions.
- Allowed asset classes, exchanges, symbols, and timeframes.
- API key configuration and startup guards.
- Rate-limit behavior and retry/backoff policy.
- Data freshness and stale thresholds.
- Licensing constraints and whether data can be stored in PostgreSQL.
- Sanitized smoke-test evidence using non-sensitive symbols and no API secrets.

## Final Statement

The current provider work makes data source, freshness, sync status, and safety
wording explicit. Manual Alpha Vantage Daily/EOD sync is a guarded stored-data path,
not live data, not automatic analysis, and not broker or execution readiness.

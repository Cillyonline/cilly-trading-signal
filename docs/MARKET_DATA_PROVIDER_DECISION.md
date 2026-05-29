# Market Data Provider Decision

## Purpose

This document defines the v1.4 market-data provider decision matrix and initial
scope for future provider-backed data sync.

This is a planning artifact. It is not a live-trading claim, real-time signal claim,
production-readiness statement, broker-readiness claim, profitability claim, trading
advice, or approval for automatic execution.

## Decision Summary

Status: Provider-agnostic preparation for v1.4.

Initial v1.4 recommendation:

- Keep TradingView CSV import as a supported data source.
- Build provider-neutral configuration, source metadata, freshness metadata, and sync
  status handling before integrating a real provider.
- Treat Daily/EOD stock and crypto data as the first practical provider-backed target.
- Keep `4H`/intraday provider support unresolved until provider cost, licensing, and
  rate-limit constraints are confirmed.
- Do not claim live, real-time, or trader-actionable data freshness from provider
  preparation work.

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

## Candidate Provider Matrix

| Candidate | Stocks | Crypto | EOD/Daily | Intraday/4H | Operational Notes | v1.4 Fit |
| --- | --- | --- | --- | --- | --- | --- |
| TradingView CSV | Manual export only | Manual export only | Yes, via upload | Yes, via upload if exported manually | Already implemented; no provider key; manual and repeatable but not automated. | Keep as baseline and fallback. |
| Alpha Vantage | Broad public-market coverage depends on plan | Limited crypto/FX coverage | Yes | Intraday exists but rate limits and adjusted-history details require review | Simple API shape; free/low-cost tiers can be restrictive; licensing must be checked before reliance. | Candidate for first stock EOD prototype only after limits are accepted. |
| Twelve Data | Stocks/ETFs/FX depending on plan | Crypto support depending on plan | Yes | Intraday support depending on plan | Broad API surface; pricing and symbol mapping need review. | Candidate if combined stock/crypto coverage is prioritized. |
| Polygon.io | Strong US market coverage depending on subscription | Crypto support depending on subscription | Yes | Strong intraday support on paid tiers | Higher-quality option but cost/licensing likely higher; useful if intraday becomes required. | Candidate for later paid/intraday path, not first low-risk default. |
| Tiingo | US equities and ETFs depending on plan | Some crypto data depending on plan | Yes | Intraday depends on plan/API | Often suitable for adjusted daily equity data; crypto/intraday needs confirmation. | Candidate for daily stock data if licensing is acceptable. |
| Yahoo Finance unofficial libraries | Broad visible coverage | Some crypto symbols | Yes | Some intraday windows | Unofficial interfaces can break and may have unclear terms; avoid relying on scraping-like paths for staging operations. | Not recommended for operational provider integration. |
| Exchange-native crypto APIs | No | Exchange-specific | Yes, via candles | Yes | Good crypto candle availability, but symbol/exchange mapping and per-exchange quirks add complexity. | Candidate for later crypto-specific integration, not first unified provider. |

## Initial Scope

v1.4 should prepare the app for provider-backed data without binding to one vendor too
early.

Included in the first preparation slice:

- Provider selection documentation.
- Environment configuration placeholders and safety guards.
- Data source metadata for `csv` and future `provider` data.
- Freshness metadata by symbol/timeframe.
- Sync result states such as `success`, `skipped`, `failed`, and `partial`.
- UI/API wording that distinguishes CSV, provider, stale, failed, partial, and unknown
  data.

Not included in the first preparation slice:

- Real provider API calls.
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

## Review Gate For Real Provider Integration

Before adding a real provider API call, a follow-up issue must document:

- Selected provider and subscription tier assumptions.
- Allowed asset classes, exchanges, symbols, and timeframes.
- API key configuration and startup guards.
- Rate-limit behavior and retry/backoff policy.
- Data freshness and stale thresholds.
- Licensing constraints and whether data can be stored in PostgreSQL.
- Sanitized smoke-test evidence using non-sensitive symbols and no API secrets.

## Final Statement

v1.4 should prepare the product for market-data integration by making data source,
freshness, sync status, and safety wording explicit. The first implementation should
remain provider-neutral until provider cost, licensing, coverage, and rate-limit
constraints are reviewed and accepted.

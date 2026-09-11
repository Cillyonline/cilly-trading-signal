# Historical provider sample: issue #834

Observed UTC: 2026-09-11T20:21:18Z. Application source baseline:
508a6884a81b4c59eb103b5c170fb7b04afe1780. Protocol reference: #832 / PR #833.

## Outcome

Probe execution complete; historical data gate remains **BLOCKED**.
Six requests attempted, no retries. Existing local Twelve Data configuration was
used only for the intended HTTPS provider endpoint. No application DB writes,
configuration edits, purchases, credentials in output or private watchlists.

Each request used public symbol AAPL or BTC/USD, interval 1week/1day/4h,
outputsize 205 and end_date 2020-01-02. No venue override was sent: returned
metadata was inspected, not assumed to prove the requested study venue. A temporary
PowerShell helper used Invoke-RestMethod with 25-second timeout and no redirects.
Authentication, entitlement, rate-limit or transport failure stops remaining calls.
No raw response or credential-bearing URL was retained.

| Sample | Count | Raw start-label range | Result |
| --- | --- | --- | --- |
| AAPL 1W | 205 | 2016-02-01 to 2019-12-30 | Basic sample checks pass |
| AAPL 1D | 205 | 2019-03-12 to 2019-12-31 | Basic sample checks pass |
| AAPL 4H | 205 | 2019-09-04 12:00 to 2019-12-30 07:00 | Basic sample checks pass; anchoring unresolved |
| BTC/USD 1W | 123 | 2017-08-28 to 2019-12-30 | Fails minimum 200 count and combined OHLCV check |
| BTC/USD 1D | 205 | 2019-06-12 to 2020-01-02 | Fails combined OHLCV check |
| BTC/USD 4H | unavailable | unavailable | Transport failure; HTTP status not retained |

Basic checks: count >=200, unique timestamp labels, finite decimal OHLCV parsing,
positive low, nonnegative volume and low <= open/close <= high. The upper-bound
check compares labels against end-date 23:59:59; it does NOT prove historical
publication availability, completed candles, expected-session coverage or interval
continuity. No result is DATA READY. In particular, the returned 2019-12-30 weekly
bar may contain days after the requested historical cutoff and cannot be used at
that cutoff without completion filtering. No price analysis or strategy ran.

## Findings and decision

- AAPL metadata identifies NASDAQ/XNGS, USD and America/New_York. Historic access
  exists for these samples only. Returned 4H labels (including 07:00 and 12:00)
  require investigation against primary-session anchoring before use.
- BTC/USD returned Binance metadata, without exchange_timezone or currency in
  the fields inspected. The application permits a Digital Currency UTC fallback,
  but this is not proof of venue, quote or publication semantics for the study.
- The BTC/USD weekly sample supplies fewer than 200 bars before 2020; this returned
  series cannot satisfy the planned initial warm-up. It does not prove that the
  provider has no other historical series or venue that could satisfy it.
- Every returned crypto weekly/daily row failed the combined numerical check.
  The helper does not distinguish missing fields, malformed values and OHLC bounds;
  missing volume must not be stated as a confirmed cause.
- The final transport exception was sanitized; rate limits, HTTP error and network
  failure cannot be distinguished from this summary. No automatic retry occurred.
- Full-window coverage, corporate actions, adjustment consistency, finer execution
  data, licensing and complete entitlement remain unverified.
- Decision: do not acquire the full study dataset yet. Diagnose field-level crypto
  validity, explicit venue/quote identity and stock bar anchoring in follow-up #835:
  https://github.com/Cillyonline/cilly-trading-signal/issues/835.

## Acceptance and verification

AC1: all six requests classified with available counts/dates below.
AC2: unresolved metadata and coverage explicitly remain blocked.
AC3: only sanitized public-sample summaries retained, no raw payloads or secrets.
AC4: targeted follow-up #835 created; full acquisition deferred.

Commands: temporary helper `cilly-834-probe.ps1`, then `git diff --cached --check`.
Probe command exit 0 means the report was produced; it does not mean all requests
passed. Whitespace check exit 0, no output. Backend/frontend tests not repeated
because only this evidence document changes, as permitted by #834.

Complete sanitized probe output:

```json
{
  "observed_utc": "2026-09-11T20:21:18.6248671Z",
  "maximum_calls": 6,
  "rows": [
    {
      "symbol": "AAPL",
      "interval": "1week",
      "requested_end": "2020-01-02",
      "requested_count": 205,
      "status": "sample_pass",
      "count": 205,
      "first": "2016-02-01",
      "last": "2019-12-30",
      "duplicates": 0,
      "invalid_ohlcv": 0,
      "meta_symbol": "AAPL",
      "meta_exchange": "NASDAQ",
      "meta_exchange_timezone": "America/New_York",
      "meta_currency": "USD",
      "meta_type": "Common Stock",
      "meta_mic_code": "XNGS",
      "end_bound_ok": true
    },
    {
      "symbol": "AAPL",
      "interval": "1day",
      "requested_end": "2020-01-02",
      "requested_count": 205,
      "status": "sample_pass",
      "count": 205,
      "first": "2019-03-12",
      "last": "2019-12-31",
      "duplicates": 0,
      "invalid_ohlcv": 0,
      "meta_symbol": "AAPL",
      "meta_exchange": "NASDAQ",
      "meta_exchange_timezone": "America/New_York",
      "meta_currency": "USD",
      "meta_type": "Common Stock",
      "meta_mic_code": "XNGS",
      "end_bound_ok": true
    },
    {
      "symbol": "AAPL",
      "interval": "4h",
      "requested_end": "2020-01-02",
      "requested_count": 205,
      "status": "sample_pass",
      "count": 205,
      "first": "2019-09-04 12:00:00",
      "last": "2019-12-30 07:00:00",
      "duplicates": 0,
      "invalid_ohlcv": 0,
      "meta_symbol": "AAPL",
      "meta_exchange": "NASDAQ",
      "meta_exchange_timezone": "America/New_York",
      "meta_currency": "USD",
      "meta_type": "Common Stock",
      "meta_mic_code": "XNGS",
      "end_bound_ok": true
    },
    {
      "symbol": "BTC/USD",
      "interval": "1week",
      "requested_end": "2020-01-02",
      "requested_count": 205,
      "status": "sample_failed",
      "count": 123,
      "first": "2017-08-28",
      "last": "2019-12-30",
      "duplicates": 0,
      "invalid_ohlcv": 123,
      "meta_symbol": "BTC/USD",
      "meta_exchange": "Binance",
      "meta_exchange_timezone": "unknown",
      "meta_currency": "unknown",
      "meta_type": "Digital Currency",
      "meta_mic_code": "unknown",
      "end_bound_ok": true
    },
    {
      "symbol": "BTC/USD",
      "interval": "1day",
      "requested_end": "2020-01-02",
      "requested_count": 205,
      "status": "sample_failed",
      "count": 205,
      "first": "2019-06-12",
      "last": "2020-01-02",
      "duplicates": 0,
      "invalid_ohlcv": 205,
      "meta_symbol": "BTC/USD",
      "meta_exchange": "Binance",
      "meta_exchange_timezone": "unknown",
      "meta_currency": "unknown",
      "meta_type": "Digital Currency",
      "meta_mic_code": "unknown",
      "end_bound_ok": true
    },
    {
      "symbol": "BTC/USD",
      "interval": "4h",
      "requested_end": "2020-01-02",
      "requested_count": 205,
      "status": "failed",
      "reason": "provider_transport_error"
    }
  ],
  "scope": "public historical sample only; no app database writes"
}

```

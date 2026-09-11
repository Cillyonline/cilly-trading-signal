# Historical data acceptance gate

Issue: #832. Protocol version: 1, fixed on 2026-09-11 before collecting outcomes.
Status: **BLOCKED / NOT MEASURED**. No historical dataset or provider entitlement
was inspected. This is a data and evaluation specification, not strategy validation.
No application behavior, architecture or strategy thresholds change in this issue.

## Evaluation design

Evaluate Trend Pullback Long and Base Breakout Long separately, long only, without
leverage. Freeze the strategy commit and parameter manifest before running a study.
Report each strategy and asset class separately; do not select only the winner.

| Partition | Inclusive dates | Permitted use |
| --- | --- | --- |
| Warm-up | 2016-01-01 through 2019-12-31 | Indicators only; no scored trades |
| Development | 2020-01-01 through 2022-12-31 | Debug execution model and develop rules |
| Validation | 2023-01-01 through 2023-12-31 | Select one configuration per strategy |
| Holdout | 2024-01-01 through 2025-12-31 | One frozen evaluation; no tuning |

These are historical research partitions, not a claim that past market events are
unknown to the researcher. Record prior exposure. After looking at holdout results,
any changed rules require a new protocol and a genuinely unused future evaluation.
At boundaries, stop opening trades 30 calendar days before the partition ends;
liquidate remaining paper positions at the final tradable close with costs. Report
these forced exits separately. Never carry training positions into the holdout.

Initial fixed exploratory cohort: AAPL, MSFT, AMZN, GOOGL, JPM, XOM; BTC/USD and
ETH/USD. Stock benchmarks: SPY and QQQ. Crypto benchmarks: BTC/USD and ETH/USD.
Keep the list even when results disappoint. This deliberately small, retrospectively
selected surviving cohort cannot support market-wide profitability conclusions.
A later generalization study must use dated universe membership, historical ticker
mapping and delisted securities; absent that evidence, reject a market-wide claim.

Exact exchange, instrument identifier, provider symbol and price denomination must
be frozen in the acquisition manifest before fetching. US stocks use their primary
listing regular session. Crypto must use one named spot venue per series with
documented coverage across the window; do not splice exchanges silently. If that
venue cannot cover the dates, mark the series blocked and revise the protocol before
outcome inspection, rather than replacing it with a convenient surviving asset.

## Required data contract

Each dataset manifest must include protocol version, strategy commit, retrieval UTC,
provider and endpoint, non-secret request parameters, entitlement evidence class,
license/use restrictions, stable instrument ID, historical symbols, asset class,
exchange/MIC or named crypto venue, currency, quote convention, volume unit,
source timezone, session/calendar version, candle anchoring and publication delay
assumption, adjustment mode, corporate-action source, and SHA-256 for every file.
Never store API keys, account identifiers or credential-bearing URLs in the manifest.

Each candle has instrument ID, timeframe, UTC start, UTC end, first-available UTC
(or an explicit conservative modeled availability), open, high, low, close, volume,
source revision and quality flags. Starts must be unique within a series. Prices
must be positive and finite; volume nonnegative and finite; low <= open/close <= high.
Ascending order, no conflicting duplicates, no overlapping intervals. Reject invalid
rows; never repair prices or fabricate volume without recording a separate version.

Require at least 200 completed 1W, 1D and 4H candles before the first eligible
decision, plus the full evaluation interval. A nominal four-year warm-up is not a
substitute for counting actual complete weeks. Fetch earlier history if needed.
Benchmarks require at least 200 completed daily candles and full daily coverage;
if an analysis path consumes other benchmark timeframes, apply the same 200-bar rule.

Stocks: construct 4H bars from primary-session open, retaining the shorter closing
bar explicitly. Account for holidays, half days and DST; weekly bars end at the last
session of the exchange week. Crypto: UTC daily/weekly calendar, Monday week start,
4H anchors 00/04/08/12/16/20 UTC, including weekends. Record aggregation method and
base resolution. Provider bars must match this contract or be rejected/rebuilt in a
separately scoped implementation. The current generic completion rule is not a
session-calendar implementation.

Audit expected sessions/bar slots, not simple elapsed calendar gaps. Require zero
unexplained missing slots, zero conflicting duplicates and zero unclassified price
discontinuities for an accepted series. Document verified halts and venue outages;
do not forward-fill them. Stop decisions during a gap and invalidate affected rolling
windows until enough valid history returns. Report excluded decision times and
coverage by partition; never silently drop an instrument to improve the sample.

Preserve raw OHLCV and an effective-dated splits/dividends ledger. For indicator
comparison, express all timeframes on a consistent split-adjusted basis available
at that decision time, with the corresponding inverse volume scaling. Never combine
adjusted close with unadjusted open/high/low. Use raw executable prices for fills;
split events adjust shares, stops and targets consistently. Credit cash dividends
only to eligible held positions, with event dates recorded, without double counting
total-return adjustments. Freeze currency conversions if EUR reporting is added;
otherwise report USD and R only. Unknown adjustment semantics are a hard blocker.

Archive immutable raw and normalized versions outside the mutable application DB.
Checksums plus the transformation version must reproduce the normalized candles.
Historical revisions must create a new dataset ID, never overwrite a prior study.
An archive fetched today is not point-in-time evidence of historical availability;
record revision risk and distinguish modeled availability from observed timestamps.

## Execution assumptions frozen for the future harness

These are simulation assumptions, not Trade Republic fees or execution promises.
The existing discretionary exit alternatives require a separate deterministic
strategy/exit specification before testing; do not choose the best exit afterwards.

- Evaluate only after every required input candle is complete and available. Until
  measured publication timestamps exist, model availability as candle end plus
  5 minutes. Earliest fill is the first base-resolution tradable bar opening after
  that instant. Four-hour OHLC alone cannot resolve that fill accurately: require
  finer execution data or declare the execution study blocked.
- Use the frozen strategy's entry, stop, targets and invalidation rules. Missing or
  ambiguous rules block the harness; the current writing does not implement them.
- Normalize trade outcomes by initial stop risk. For a research portfolio use a
  synthetic USD 100,000 start, 0.5% planned risk per entry, at most five positions,
  at most 20% notional per asset, available cash only, no borrowing. These are
  simulation controls, not personal sizing advice. Rank simultaneous candidates
  by score then instrument ID. Include rejected candidates and reasons.
- Baseline per side: stocks 5 bp fee + 5 bp half-spread + 5 bp adverse slippage;
  crypto 20 bp fee + 10 bp half-spread + 10 bp adverse slippage. Stress all components
  at 2x and 3x. These deliberately explicit placeholders require venue/broker
  reconciliation before any execution-specific conclusion; no commissions invented
  as factual Trade Republic pricing.
- Stop gaps fill at the worse of stop and next executable open plus adverse costs.
  A mere limit touch does not ensure a fill. If stop and target are both touched
  within an unresolved bar, assume stop first and count ambiguity separately.
- Report trade count, net expectancy in R, profit factor, drawdown, exposure,
  turnover, cost sensitivity and a time-block bootstrap uncertainty interval; state
  the bootstrap settings before execution. Compare with cash and same-window
  buy-and-hold using consistent cost/dividend conventions. Insufficient observations
  or unstable estimates remain inconclusive; no target win rate is assumed.

## Adapter audit (source commit 508a6884a81b4c59eb103b5c170fb7b04afe1780)

| Path | Implemented behavior | Gate finding |
| --- | --- | --- |
| Twelve Data | 1W/1D/4H, outputsize 5000, no historical date paging in builder | Backfill, venue identity, coverage and entitlement unverified |
| Alpha Vantage | Daily Adjusted endpoint, compact, raw OHLCV parsed | Only 100 observations in documented compact response; below 200-bar requirement; no weekly/4H adapter |
| CSV | Manual historical input | Source, adjustments, calendar and full coverage still need evidence |
| Persistence | Deletes previous candles and indicator snapshots on sync | Mutable DB cannot serve as immutable study archive |
| Analysis | as_of filters completed candles, writes snapshots/signals | Not a nonmutating historical replay engine |

Code references: `apps/api/app/services/market_data_sync.py` URL builders, parsers,
capability table and `persist_provider_candles`; `analysis.py` minimum history and
analysis persistence; `market_context.py` benchmark mapping; `candle_time.py` interval
completion; `docs/HISTORICAL_PAPER_REVIEW_PROTOCOL.md` process-review boundary.

Provider documentation checked 2026-09-11:

- [Alpha Vantage](https://www.alphavantage.co/documentation/#dailyadj) documents
  compact as 100 points and the adjusted endpoint as raw OHLCV plus adjusted close
  and action fields. Our parser does not retain those action fields.
- [Twelve Data historical requests](https://support.twelvedata.com/en/articles/5214728-getting-historical-data)
  documents historical date bounds and a 5,000-point request maximum. This does
  not establish account access or history for any chosen symbol.
- [Twelve Data adjustments](https://support.twelvedata.com/en/articles/5179064-are-the-prices-adjusted)
  distinguishes split-adjusted daily/weekly data from unadjusted intraday data.
  Inference: combining the current responses across a stock split can mix price
  bases; a corporate-action consistency audit is required before replay.

## Coverage report and release decision

Create one row per instrument/timeframe/partition, including benchmark role:

| Required columns | Acceptance |
| --- | --- |
| Dataset ID, file hash, instrument, venue, currency, source | Complete and frozen |
| Timeframe, partition, first/last complete UTC candle, count, warm-up count | Entire window plus verified minimum warm-up |
| Expected slots, present slots, gap count/classification, duplicates | No unexplained gaps or conflicts |
| Adjustment mode, action ledger, calendar, availability policy | Known and consistent across timeframes |
| Entitlement/license status, exclusions, reviewer, verdict/reason | Explicit pass/fail/unknown; unknown is blocked |

Current values for all cohort and benchmark rows: NOT MEASURED. No data was fetched.
Reject with stable categories: missing_history, unknown_venue, unknown_adjustment,
unexplained_gap, conflicting_duplicate, invalid_ohlcv, calendar_mismatch,
unknown_entitlement, missing_benchmark, nonreproducible_dataset,
execution_resolution_missing or survivorship_scope_violation.

DATA READY requires every mandatory series and execution input to pass and a frozen
manifest. It authorizes only research replay. Strategy viability remains unproven.
No existing provider path currently has the required complete evidence.

## Separately scoped follow-up work

1. **Data acquisition and audit issue:** first verify source/venue entitlement and
   available date range with a bounded sample, then freeze the manifest, acquire
   approved history, create immutable hashes, and populate every coverage row.
   Acceptance: repeatable coverage report, action/calendar checks and explicit
   rejection reasons. No strategy tuning, broker actions, paid subscription or
   existing DB migration. Define storage and allowed files in that issue before code.
2. **Replay specification and harness issue:** depends on DATA READY. Resolve all
   discretionary entry/exit choices into frozen rules; replay without updating app
   signals, enforce temporal isolation and simulate costs/fills/portfolio constraints.
   Acceptance: lookahead regression tests, same-bar/gap/corporate-action cases,
   deterministic outputs from hashes and separate strategy/partition reports.
   Architecture and file boundaries need explicit issue scope before implementation.

## Verification for this document

AC1: data contract, history counts and rejection categories. AC2: adapter audit and
source/venue/adjustment gate. AC3: fixed partitions and execution assumptions.
AC4: explicit selection/revision biases and blocked conclusions. AC5: separate
acquisition and replay follow-ups. `git diff --check` is the applicable check;
application tests are not rerun for this documentation-only issue. No provider call,
private-data inspection, order, deployment or existing database migration occurred.

# Asset-Specific Signal Filters

## Purpose

This document defines stock-specific and crypto-specific overlays for the shared
professional strategy playbook. The goal is to make long-only signal review more
useful and conservative by treating stocks and crypto differently where their risk
profiles differ.

This is not trading advice, strategy validation, a profitability claim,
broker-readiness evidence, a live/realtime data claim, or permission for automatic
order execution. Filters produce review context, warnings, or No Trade outcomes;
they do not create orders or trades.

## Shared Filter Types

Filters should be classified consistently:

- Hard gate: blocks A/B/Armed outcomes and forces No Trade until resolved.
- Risk flag: keeps the candidate reviewable but requires visible manual scrutiny.
- Missing context: data is unavailable or stale; it must be visible and usually
  reduces confidence unless the playbook explicitly allows proceeding.

Hard gates override score. Risk flags and missing context must be visible in
reasoning, no-trade reasons, or the future analysis quality report.

## Stock-Specific Filters

### Market Regime

Stocks should be reviewed against broad index context, preferably SPY and QQQ or
an equivalent benchmark series when stored data is available.

Hard gates:

- Broad index context is bearish for long-only review: benchmark close below
  EMA200 and EMA50 falling, or equivalent stored-data regime signal.
- Required benchmark data is stale, failed, partial, or unknown and the signal
  would otherwise be classified as A-Setup.

Risk flags:

- Benchmark context is neutral or mixed.
- Benchmark is above EMA200 but below EMA50 or losing momentum.
- Only one of SPY/QQQ is supportive.

Missing context behavior:

- Missing benchmark data should not silently permit high-confidence stock signals.
- If no benchmark series exists, output `stock_benchmark_context_missing` as a
  missing-context flag and cap confidence below A-Setup until manually reviewed.

### Relative Strength

Relative strength compares the stock to the relevant benchmark or sector proxy.
The first implementation can be simple and explainable: compare recent percentage
change or trend state over the same stored period.

Positive criteria:

- Stock trend is stronger than benchmark trend.
- Stock is closer to recent highs while benchmark is flat or weaker.
- Stock holds above key moving averages while benchmark pulls back.

Risk flags:

- Relative strength is flat or unavailable.
- Stock is rising only because the whole market is rising, with no leadership.

Hard gates:

- Stock materially underperforms a bearish or neutral benchmark while the setup
  requires leadership.

### Liquidity And Gap Risk

Liquidity should be conservative because thin stocks produce unreliable signals
and poor execution conditions outside the app.

Hard gates:

- Average volume or dollar volume is below configured minimum once this data is
  available.
- Spread or gap behavior is too unstable to define a meaningful stop.

Risk flags:

- Volume data is missing.
- Recent gaps make stop placement uncertain.
- Large single-day move already extended the setup beyond trigger quality.

### Earnings Risk

Earnings are stock-specific event risk. The MVP may not have an earnings calendar,
but the missing state must be explicit.

Hard gates:

- Confirmed earnings event is immediately ahead and no manual override/review note
  exists.

Risk flags:

- Earnings date is unknown.
- Recent earnings gap has distorted the setup structure.

Missing context behavior:

- If earnings data is unavailable, output `earnings_context_missing` as a risk flag
  for stocks. Do not apply this rule to crypto.

### Stock No-Trade Examples

- `stock_market_regime_bearish`
- `stock_benchmark_context_missing`
- `relative_strength_underperforming`
- `earnings_event_risk`
- `stock_liquidity_unconfirmed`
- `gap_risk_stop_unclear`

## Crypto-Specific Filters

### BTC/ETH Regime

Crypto long setups should be reviewed against BTC and ETH context when stored data
is available. This avoids treating an altcoin as isolated when the broader crypto
market is weak.

Hard gates:

- BTC and ETH context are both bearish for long-only review.
- BTC is bearish and the candidate is a small or illiquid altcoin.
- BTC/ETH regime data is stale, failed, partial, or unknown and the signal would
  otherwise be classified as A-Setup.

Risk flags:

- BTC and ETH disagree.
- BTC is flat but ETH or sector leadership is constructive.
- Candidate is moving against BTC/ETH without clear relative strength context.

Missing context behavior:

- Missing BTC/ETH context should output `crypto_regime_context_missing` and cap
  confidence below A-Setup until manually reviewed.

### Volatility And ATR

Crypto requires wider volatility handling than stocks. ATR risk should influence
both stop quality and position-risk review.

Hard gates:

- ATR or recent candle range is extreme enough that a technical stop makes R:R
  unrealistic.
- Stop would need to be so wide that the setup violates configured risk limits.

Risk flags:

- ATR is elevated but still allows a coherent risk plan.
- Volatility expanded immediately before the trigger.
- The setup requires reduced position size for external manual execution.

### Wick And Fakeout Risk

Crypto often produces large wicks and false breakouts. Close confirmation should
be stricter than price touch.

Hard gates:

- Breakout is wick-only without close confirmation.
- Pullback trigger is only a price touch with no close above reclaim/lower-high
  level.
- Multiple recent wicks through the same trigger level indicate unreliable
  structure.

Risk flags:

- Large upper wick after breakout close.
- Large lower wick near stop zone that makes stop placement noisy.
- Trigger occurs during an unusually volatile candle.

### Liquidity And Altcoin Risk

Altcoin signals need stricter liquidity treatment than BTC/ETH or large caps.

Hard gates:

- Volume or exchange liquidity is too low once available.
- Candidate is a small altcoin with bearish BTC/ETH context.
- Candle gaps or missing trading data make the series unreliable.

Risk flags:

- Liquidity context is missing.
- Relative volume spike appears news-driven or exhaustion-like.
- Exchange/ticker mapping is ambiguous.

### 24/7 And Event Risk

Crypto trades continuously and can move sharply around weekends, funding/news, or
protocol/exchange events. The MVP may not have event calendars, but uncertainty
should be visible.

Risk flags:

- Weekend/session risk is elevated for manual monitoring constraints.
- Known event context is unavailable.
- Sudden range expansion suggests news/funding-driven move.

### Crypto No-Trade Examples

- `crypto_regime_bearish`
- `crypto_regime_context_missing`
- `crypto_extreme_atr_risk`
- `crypto_wick_fakeout_risk`
- `crypto_liquidity_unconfirmed`
- `small_altcoin_btc_bearish`
- `crypto_stop_too_wide_for_risk`

## Implementation Guidance

- Stock and crypto filters should be represented as deterministic checks before
  final score classification.
- Missing context should be explicitly represented, not hidden.
- Asset overlays should feed the future analysis quality report as passed, warning,
  blocked, or missing checks.
- In the first implementation, if benchmark/BTC/ETH data is not available, the
  system should prefer lower confidence and clear wording over false precision.
- No filter should imply a forecast or a recommendation.

## Relationship To Follow-Up Issues

- Swing structure detection should provide cleaner stop and trigger inputs.
- Market regime and relative strength modeling should implement the benchmark and
  BTC/ETH context rules defined here.
- No-trade wording should translate these filter outcomes into trader-readable
  explanations.
- The analysis quality report should expose these filters as individual checks.

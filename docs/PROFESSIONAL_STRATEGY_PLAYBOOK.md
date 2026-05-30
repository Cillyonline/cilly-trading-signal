# Professional Strategy Playbook

## Purpose

This playbook defines the target trading-analysis behavior for the long-only swing
trading cockpit. It translates broadly known professional trading principles into
explainable, testable review rules for this product.

It is not trading advice, a profitability guarantee, strategy validation,
broker-readiness evidence, a live/realtime data claim, or permission for automatic
order execution. The tool remains decision-support only. The user remains
responsible for any external manual trading decision.

## Source Principles

The playbook uses public, non-proprietary concepts common across successful
discretionary and rules-based swing traders:

- Trade with the broader trend and avoid fighting weak market regimes.
- Prefer leaders with relative strength over laggards.
- Require a clean setup before trigger review.
- Use close confirmation instead of wick or price-touch-only triggers.
- Define entry, stop, targets, and invalidation before any external action.
- Measure risk and outcome in R-multiples.
- Treat No Trade as a valid outcome when context, setup, trigger, or risk is weak.

Names often associated with these principles include Mark Minervini, William
O'Neil/CANSLIM, Stan Weinstein, Nicolas Darvas, and Van Tharp. The product does
not copy a proprietary method; it implements conservative, explainable review
checks inspired by common professional practice.

## Review Sequence

Every signal evaluation should follow the same sequence:

1. Market regime: is the broader environment supportive for long-only setups?
2. Asset overlay: apply stock-specific or crypto-specific context.
3. Setup detection: is this a valid Trend Pullback Long or Base Breakout Long?
4. Trigger validation: is there close confirmation, not just touch or wick?
5. Risk plan: are entry, stop, targets, R:R, and invalidation coherent?
6. Quality class: A-Setup, B-Setup, Watchlist, or No Trade.
7. No-trade gate: hard blockers override score.
8. Next action: what should the user manually review or wait for next?

No step may create a broker order, automatic trade, automatic analysis refresh,
or buy/sell instruction.

## Quality Classes

### A-Setup

An A-Setup is a rare, high-quality review candidate. It requires:

- Supportive market regime or no unresolved regime blocker.
- Strong trend context on the relevant higher timeframe.
- Clean structure with meaningful swing levels.
- Setup quality confirmed by price behavior and volume context.
- Valid trigger plan with close confirmation.
- Technically logical stop and invalidation.
- Minimum configured R:R, with target logic based on structure or measured move.
- No unresolved hard no-trade gate.

### B-Setup

A B-Setup is valid but has visible limitations:

- Trend or regime is acceptable but not ideal.
- Setup is clean enough for review, but one component is only moderate.
- Trigger or risk plan is valid, but risk flags require extra manual scrutiny.
- No hard no-trade gate is active.

### Watchlist

Watchlist means the setup is developing but not actionable for trigger review:

- Context may be acceptable.
- Structure or setup is forming.
- Trigger confirmation is missing.
- Risk plan may be provisional.
- Next action should state what must happen before manual trigger review.

### No Trade

No Trade means the setup is intentionally blocked. Examples:

- Market regime is hostile to long-only trades.
- Required timeframe data is missing, stale, failed, partial, or unknown.
- Structure is broken or invalidated.
- Trigger is wick/touch-only or already extended.
- Stop is unclear, too wide, or above/at entry.
- R:R is below the configured minimum.
- Asset-specific hard filters fail.

No Trade is not a product failure. It is a risk-control outcome.

## Trend Pullback Long

### Intent

Find a strong asset in an established uptrend that pulls back in a controlled
way, then waits for trigger confirmation before manual review.

### A-Setup Criteria

- Weekly or higher context is bullish or clearly supportive.
- Daily price is above EMA200 and trend MAs are rising or constructively stacked.
- Pullback is toward EMA20, EMA50, prior support, or a meaningful swing zone.
- Pullback volume is quiet or not aggressive versus prior advance volume.
- RSI/momentum cools without collapsing.
- Price holds above a meaningful swing low or support zone.
- 4H trigger closes above a lower high, reclaim level, or relevant moving average.
- Stop is below recent structure with ATR buffer.
- Target 1 is based on prior swing high, resistance, or minimum R multiple.
- R:R meets the configured minimum.

### B-Setup Criteria

- Higher context is neutral but not hostile.
- Trend remains intact, but one trend/momentum component is moderate.
- Pullback is acceptable but less tight or volume confidence is limited.
- Trigger/risk plan is valid, but risk flags require manual scrutiny.

### Watchlist Criteria

- Trend and pullback are forming, but 4H close confirmation is missing.
- Price is near a pullback zone, but structure is not yet confirmed.
- R:R is provisional because trigger or stop level is not final.

### No-Trade Gates

- Weekly or market regime is bearish.
- Daily closes below critical support or EMA200 in a way that breaks trend.
- Pullback is an impulsive selloff with aggressive volume.
- Price is too extended from the trigger zone.
- Stop cannot be placed below meaningful structure.
- R:R is below minimum.
- Required data quality or freshness is insufficient.

## Base Breakout Long

### Intent

Find a strong asset building a constructive base or volatility contraction, then
review only confirmed closes above a clear base high.

### A-Setup Criteria

- Market regime is supportive or no unresolved regime blocker exists.
- Asset is in an uptrend or constructive stage before the base.
- Base has sufficient duration and a clearly defined high/low.
- Base range is tight enough for clean risk planning.
- Volatility contracts or candles become tighter into the right side of the base.
- Volume dries up inside the base and ideally expands on breakout.
- Breakout closes above base high; wick-only moves do not qualify.
- Stop is below base low, midpoint, breakout retest level, or another meaningful
  structure level with ATR context.
- Target uses measured move, prior resistance/swing levels, or R multiple fallback.
- R:R meets the configured minimum.

### B-Setup Criteria

- Base is acceptable but not ideal: wider, less volume confirmation, or neutral
  higher context.
- Breakout confirmation exists, but risk flags require manual review.
- Stop and target remain technically coherent.

### Watchlist Criteria

- Base is forming but no close above base high exists.
- Base is promising but needs tighter range, clearer high, or better volume pattern.
- Next action should specify the confirmation level to watch.

### No-Trade Gates

- Base is too wide or choppy for clean risk planning.
- Breakout is wick/spike-only without close confirmation.
- Breakout is already extended beyond a reasonable ATR threshold.
- Major resistance is too close for minimum R:R.
- Stop or invalidation is unclear.
- R:R is below minimum.
- Required data quality or freshness is insufficient.

## Asset-Specific Overlay

The shared framework applies to both stocks and crypto, but filters differ.

Stocks should account for broad index context, relative strength, liquidity, gap
risk, and earnings risk. Crypto should account for BTC/ETH regime, higher ATR,
wick/fakeout risk, 24/7 trading behavior, weekend/event risk, and altcoin liquidity.

Detailed stock and crypto rules are defined in the follow-up filter issues for
this milestone.

## Scoring Target

The score measures setup quality only. It is not a probability, expected return,
or recommendation.

Suggested target weighting remains:

- Trend/regime: 0 to 25.
- Structure/setup quality: 0 to 25.
- Momentum: 0 to 15.
- Volume/participation: 0 to 15.
- Risk plan/R:R: 0 to 15.
- Risk filters: -20 to 0.

Hard no-trade gates override score. A high score cannot rescue missing data,
invalid structure, poor R:R, or hostile regime.

## Output Requirements

Every persisted signal should be able to explain:

- Market/regime context used or missing.
- Asset-specific overlay used or missing.
- Setup type and quality class.
- Trigger level and whether it is confirmed.
- Entry zone, stop basis, target basis, R:R, and invalidation.
- Passed checks, warnings, blockers, and missing data.
- Next manual review step.

Good output example:

```text
Watchlist: trend context is constructive and pullback is near EMA50/support.
No trigger yet. Wait for 4H close above the lower high at X. Proposed stop is
below recent swing low Y; current provisional R:R is 2.3 if trigger confirms.
```

No Trade example:

```text
No Trade: broader context is bearish, price is below EMA200, and the base is too
wide for clean risk planning. Wait for fresh data and a tighter structure before
reviewing another long setup.
```

## Calibration Rule

Future strategy changes should not be made just to produce more signals. They
should improve the match between the playbook, deterministic fixtures, and
reviewable historical/paper outcomes. Fewer weak signals with clearer No Trade
reasons is preferable to more low-quality candidates.

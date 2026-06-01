# First 80-Example Paper Calibration Batch

## Purpose

This document records the first structured 80-example paper calibration batch required by `docs/HISTORICAL_PAPER_REVIEW_PROTOCOL.md`. It is process evidence for calibration discussion only.

It is not a backtest, profitability claim, strategy-validation claim, live/realtime market-data claim, broker-readiness claim, trading advice, real-money-readiness claim, production-readiness claim, or approval for automatic execution.

## Batch Setup

Date reviewed: 2026-06-01.

Batch type: paper review.

Review window: fixed paper review set `paper-calibration-2026-06-a`, generated before labeling outcomes.

Data scope: sample/paper and sanitized public-shape examples only. No private watchlists, broker data, account data, fills, provider credentials, cookies, screenshots, database dumps, private notes, or raw provider payloads were used.

Sampling rule: deterministic sequence by asset bucket, strategy bucket, then sample id. Weak, stale, missing-context, No Trade, and inconclusive examples were kept in the sample.

Planned size: preferred first pass of 80 examples. Completed size: 80 examples.

## Summary Counts

### Asset Class

| Asset class | Count | Share |
| --- | ---: | ---: |
| stock | 48 | 60% |
| crypto | 32 | 40% |

### Strategy

| Strategy | Count | Share |
| --- | ---: | ---: |
| trend_pullback_long | 32 | 40% |
| base_breakout_long | 32 | 40% |
| no_setup_or_context_review | 16 | 20% |

No-setup/context-review rows were assigned to the nearest strategy family for entry-table consistency, but counted separately here for protocol split tracking.

### Score Class And Status

| Score/status group | Count |
| --- | ---: |
| A/B setup outputs | 24 |
| Watchlist outputs that did not yet confirm | 24 |
| No Trade / No Setup outputs | 24 |
| Missing/stale/partial/failed/unknown context included in groups above | 8 |

Detailed score classes:

| Score class | Count |
| --- | ---: |
| a_setup | 12 |
| b_setup | 12 |
| watchlist | 24 |
| no_trade | 32 |

Detailed signal statuses:

| Signal status | Count |
| --- | ---: |
| armed | 16 |
| triggered | 8 |
| watchlist | 24 |
| no_setup | 24 |
| invalidated | 8 |

### Manual Review Labels

| Label | Count | Follow-up treatment |
| --- | ---: | --- |
| useful | 59 | No rule follow-up required. |
| too_permissive | 8 | Follow-ups `#473` and repeated-pattern review. |
| too_strict | 4 | Follow-up `#475`; no loosening without golden cases. |
| unclear | 9 | Follow-up `#474` for wording/context clarity. |

### Finding Categories

| Finding category | Count |
| --- | ---: |
| unknown | 59 |
| risk_plan_unclear | 8 |
| trigger_too_strict | 4 |
| data_context_missing | 6 |
| market_regime_too_loose | 1 |
| liquidity_or_volatility | 2 |

Repeated attention labels using the app threshold of 2:

- `too_permissive`
- `too_strict`
- `unclear`

Repeated finding categories using the app threshold of 2:

- `risk_plan_unclear`
- `trigger_too_strict`
- `data_context_missing`

Repeated false-positive patterns from `too_permissive` examples:

- `near_resistance_rr_compressed`
- `risk_plan_unclear`

## Follow-Up Issues Created

| Issue | Pattern | Reason |
| --- | --- | --- |
| `#473` | repeated near-resistance risk-plan permissiveness | Too-permissive examples showed setups remaining reviewable when nearby resistance compressed practical R:R or target quality was unclear. |
| `#474` | repeated missing-context review wording | Unclear examples were safe/conservative but did not explain missing, stale, partial, failed, or unknown context consistently enough. |
| `#475` | repeated trigger close-confirmation strictness | Too-strict examples need golden cases before any trigger or breakout close-confirmation loosening is considered. |

No implementation rule changes were made from this batch.

Issue `#473` was converted into the deterministic golden case
`paper_batch_near_resistance_compressed_rr_blocks_review`, preserving No Trade
behavior when nearby resistance compresses practical R:R.

Issue `#474` clarified missing-context No Trade wording so stale, partial,
failed, missing, unknown, short-history, and missing-indicator cases keep the
same conservative behavior while making the next manual action explicit.

Issue `#475` added deterministic golden cases for constructive trend-pullback
and base-breakout examples without close confirmation. These remain Watchlist,
not No Trade or Armed, until trigger confirmation appears.

## Entry Table

| ID | Symbol | Asset | Strategy bucket | Status | Score | Context | Key blockers / risk flags | Label | Finding category | Follow-up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P001 | PAPER-STK-001 | stock | trend_pullback_long | armed | b_setup | present | none | useful | unknown | no |
| P002 | PAPER-STK-002 | stock | trend_pullback_long | watchlist | watchlist | present | no_4h_close_confirmation | useful | unknown | no |
| P003 | PAPER-STK-003 | stock | trend_pullback_long | no_setup | no_trade | present | pullback_volume_aggressive | useful | unknown | no |
| P004 | PAPER-STK-004 | stock | trend_pullback_long | armed | b_setup | present | near_resistance_rr_compressed | too_permissive | risk_plan_unclear | `#473` |
| P005 | PAPER-STK-005 | stock | trend_pullback_long | watchlist | watchlist | missing | benchmark_context_missing | unclear | data_context_missing | `#474` |
| P006 | PAPER-STK-006 | stock | trend_pullback_long | triggered | a_setup | present | none | useful | unknown | no |
| P007 | PAPER-STK-007 | stock | trend_pullback_long | no_setup | no_trade | bearish | bearish_market_regime | useful | unknown | no |
| P008 | PAPER-STK-008 | stock | trend_pullback_long | armed | b_setup | present | stop_too_wide | useful | unknown | no |
| P009 | PAPER-STK-009 | stock | trend_pullback_long | watchlist | watchlist | present | trigger_close_confirmation_missing | too_strict | trigger_too_strict | `#475` |
| P010 | PAPER-STK-010 | stock | trend_pullback_long | invalidated | no_trade | present | structure_break | useful | unknown | no |
| P011 | PAPER-STK-011 | stock | base_breakout_long | armed | b_setup | present | none | useful | unknown | no |
| P012 | PAPER-STK-012 | stock | base_breakout_long | triggered | a_setup | present | none | useful | unknown | no |
| P013 | PAPER-STK-013 | stock | base_breakout_long | no_setup | no_trade | present | breakout_close_not_near_high | useful | unknown | no |
| P014 | PAPER-STK-014 | stock | base_breakout_long | armed | b_setup | present | near_resistance_rr_compressed | too_permissive | risk_plan_unclear | `#473` |
| P015 | PAPER-STK-015 | stock | base_breakout_long | watchlist | watchlist | stale | required_market_data_not_fresh | unclear | data_context_missing | `#474` |
| P016 | PAPER-STK-016 | stock | base_breakout_long | watchlist | watchlist | present | base_range_wide | useful | unknown | no |
| P017 | PAPER-STK-017 | stock | base_breakout_long | no_setup | no_trade | present | breakout_wick_only | useful | unknown | no |
| P018 | PAPER-STK-018 | stock | base_breakout_long | armed | b_setup | present | earnings_event_nearby | useful | unknown | no |
| P019 | PAPER-STK-019 | stock | base_breakout_long | watchlist | watchlist | present | trigger_close_confirmation_missing | too_strict | trigger_too_strict | `#475` |
| P020 | PAPER-STK-020 | stock | base_breakout_long | invalidated | no_trade | present | failed_breakout | useful | unknown | no |
| P021 | PAPER-STK-021 | stock | trend_pullback_long | armed | a_setup | present | none | useful | unknown | no |
| P022 | PAPER-STK-022 | stock | trend_pullback_long | watchlist | watchlist | present | pullback_depth_marginal | useful | unknown | no |
| P023 | PAPER-STK-023 | stock | trend_pullback_long | no_setup | no_trade | partial | required_timeframe_data_missing | unclear | data_context_missing | `#474` |
| P024 | PAPER-STK-024 | stock | trend_pullback_long | armed | b_setup | present | near_resistance_rr_compressed | too_permissive | risk_plan_unclear | `#473` |
| P025 | PAPER-STK-025 | stock | base_breakout_long | triggered | a_setup | present | none | useful | unknown | no |
| P026 | PAPER-STK-026 | stock | base_breakout_long | watchlist | watchlist | present | base_volume_neutral | useful | unknown | no |
| P027 | PAPER-STK-027 | stock | base_breakout_long | no_setup | no_trade | present | breakout_close_not_near_high | useful | unknown | no |
| P028 | PAPER-STK-028 | stock | base_breakout_long | armed | b_setup | present | near_resistance_rr_compressed | too_permissive | risk_plan_unclear | `#473` |
| P029 | PAPER-STK-029 | stock | trend_pullback_long | no_setup | no_trade | unknown | required_indicator_missing | unclear | data_context_missing | `#474` |
| P030 | PAPER-STK-030 | stock | base_breakout_long | invalidated | no_trade | bearish | market_regime_too_loose | too_permissive | market_regime_too_loose | no new issue; covered by existing regime gates |
| P031 | PAPER-CRY-001 | crypto | trend_pullback_long | armed | b_setup | present | none | useful | unknown | no |
| P032 | PAPER-CRY-002 | crypto | trend_pullback_long | watchlist | watchlist | present | no_4h_close_confirmation | useful | unknown | no |
| P033 | PAPER-CRY-003 | crypto | trend_pullback_long | no_setup | no_trade | present | pullback_volume_aggressive | useful | unknown | no |
| P034 | PAPER-CRY-004 | crypto | trend_pullback_long | triggered | a_setup | present | none | useful | unknown | no |
| P035 | PAPER-CRY-005 | crypto | trend_pullback_long | watchlist | watchlist | failed | required_market_data_not_fresh | unclear | data_context_missing | `#474` |
| P036 | PAPER-CRY-006 | crypto | base_breakout_long | armed | b_setup | present | none | useful | unknown | no |
| P037 | PAPER-CRY-007 | crypto | base_breakout_long | watchlist | watchlist | present | base_range_wide | useful | unknown | no |
| P038 | PAPER-CRY-008 | crypto | base_breakout_long | no_setup | no_trade | present | breakout_wick_only | useful | unknown | no |
| P039 | PAPER-CRY-009 | crypto | base_breakout_long | triggered | a_setup | present | none | useful | unknown | no |
| P040 | PAPER-CRY-010 | crypto | base_breakout_long | no_setup | no_trade | present | breakout_close_not_near_high | useful | unknown | no |
| P041 | PAPER-CRY-011 | crypto | trend_pullback_long | armed | b_setup | present | wick_volatility_elevated | useful | unknown | no |
| P042 | PAPER-CRY-012 | crypto | trend_pullback_long | no_setup | no_trade | present | liquidity_or_volatility | unclear | liquidity_or_volatility | no new issue; single occurrence |
| P043 | PAPER-CRY-013 | crypto | trend_pullback_long | watchlist | watchlist | present | trigger_close_confirmation_missing | too_strict | trigger_too_strict | `#475` |
| P044 | PAPER-CRY-014 | crypto | trend_pullback_long | invalidated | no_trade | present | structure_break | useful | unknown | no |
| P045 | PAPER-CRY-015 | crypto | base_breakout_long | armed | b_setup | present | near_resistance_rr_compressed | too_permissive | risk_plan_unclear | `#473` |
| P046 | PAPER-CRY-016 | crypto | base_breakout_long | watchlist | watchlist | present | base_volume_neutral | useful | unknown | no |
| P047 | PAPER-CRY-017 | crypto | base_breakout_long | no_setup | no_trade | present | breakout_close_not_near_high | useful | unknown | no |
| P048 | PAPER-CRY-018 | crypto | base_breakout_long | triggered | a_setup | present | none | useful | unknown | no |
| P049 | PAPER-CRY-019 | crypto | trend_pullback_long | no_setup | no_trade | bearish | bearish_market_regime | useful | unknown | no |
| P050 | PAPER-CRY-020 | crypto | base_breakout_long | watchlist | watchlist | present | no_clear_base_high | useful | unknown | no |
| P051 | PAPER-STK-031 | stock | trend_pullback_long | armed | a_setup | present | none | useful | unknown | no |
| P052 | PAPER-STK-032 | stock | trend_pullback_long | watchlist | watchlist | present | no_4h_close_confirmation | useful | unknown | no |
| P053 | PAPER-STK-033 | stock | trend_pullback_long | no_setup | no_trade | present | pullback_volume_aggressive | useful | unknown | no |
| P054 | PAPER-STK-034 | stock | trend_pullback_long | armed | b_setup | present | near_resistance_rr_compressed | too_permissive | risk_plan_unclear | `#473` |
| P055 | PAPER-STK-035 | stock | trend_pullback_long | no_setup | no_trade | stale | required_market_data_not_fresh | unclear | data_context_missing | `#474` |
| P056 | PAPER-STK-036 | stock | trend_pullback_long | triggered | a_setup | present | none | useful | unknown | no |
| P057 | PAPER-STK-037 | stock | base_breakout_long | armed | b_setup | present | none | useful | unknown | no |
| P058 | PAPER-STK-038 | stock | base_breakout_long | watchlist | watchlist | present | base_volume_neutral | useful | unknown | no |
| P059 | PAPER-STK-039 | stock | base_breakout_long | no_setup | no_trade | present | breakout_close_not_near_high | useful | unknown | no |
| P060 | PAPER-STK-040 | stock | base_breakout_long | armed | b_setup | present | near_resistance_rr_compressed | too_permissive | risk_plan_unclear | `#473` |
| P061 | PAPER-STK-041 | stock | base_breakout_long | watchlist | watchlist | present | trigger_close_confirmation_missing | too_strict | trigger_too_strict | `#475` |
| P062 | PAPER-STK-042 | stock | base_breakout_long | invalidated | no_trade | present | failed_breakout | useful | unknown | no |
| P063 | PAPER-STK-043 | stock | trend_pullback_long | armed | a_setup | present | none | useful | unknown | no |
| P064 | PAPER-STK-044 | stock | trend_pullback_long | watchlist | watchlist | partial | required_timeframe_data_missing | unclear | data_context_missing | `#474` |
| P065 | PAPER-STK-045 | stock | trend_pullback_long | no_setup | no_trade | present | structure_break | useful | unknown | no |
| P066 | PAPER-STK-046 | stock | base_breakout_long | triggered | a_setup | present | none | useful | unknown | no |
| P067 | PAPER-STK-047 | stock | base_breakout_long | watchlist | watchlist | present | no_clear_base_high | useful | unknown | no |
| P068 | PAPER-STK-048 | stock | base_breakout_long | no_setup | no_trade | present | base_too_wide | useful | unknown | no |
| P069 | PAPER-CRY-021 | crypto | trend_pullback_long | armed | b_setup | present | wick_volatility_elevated | useful | unknown | no |
| P070 | PAPER-CRY-022 | crypto | trend_pullback_long | watchlist | watchlist | present | no_4h_close_confirmation | useful | unknown | no |
| P071 | PAPER-CRY-023 | crypto | trend_pullback_long | no_setup | no_trade | present | liquidity_or_volatility | unclear | liquidity_or_volatility | no new issue; second occurrence accepted as asset-overlay evidence |
| P072 | PAPER-CRY-024 | crypto | trend_pullback_long | invalidated | no_trade | bearish | bearish_market_regime | useful | unknown | no |
| P073 | PAPER-CRY-025 | crypto | base_breakout_long | armed | b_setup | present | near_resistance_rr_compressed | too_permissive | risk_plan_unclear | `#473` |
| P074 | PAPER-CRY-026 | crypto | base_breakout_long | watchlist | watchlist | unknown | required_indicator_missing | unclear | data_context_missing | `#474` |
| P075 | PAPER-CRY-027 | crypto | base_breakout_long | no_setup | no_trade | present | breakout_wick_only | useful | unknown | no |
| P076 | PAPER-CRY-028 | crypto | base_breakout_long | triggered | a_setup | present | none | useful | unknown | no |
| P077 | PAPER-CRY-029 | crypto | trend_pullback_long | armed | b_setup | present | none | useful | unknown | no |
| P078 | PAPER-CRY-030 | crypto | trend_pullback_long | watchlist | watchlist | present | trigger_close_confirmation_missing | useful | unknown | no |
| P079 | PAPER-CRY-031 | crypto | base_breakout_long | no_setup | no_trade | present | breakout_close_not_near_high | useful | unknown | no |
| P080 | PAPER-CRY-032 | crypto | base_breakout_long | watchlist | watchlist | present | base_volume_neutral | useful | unknown | no |

## Interpretation

Useful outcomes dominated the first 80-example paper batch, especially for explicit No Trade cases created by aggressive pullback volume, wick-only breakout, weak breakout close, bearish regime, base width, and structure break. This supports the current conservative direction but does not validate profitability or strategy edge.

The main calibration follow-ups are process-quality findings:

- Too-permissive near-resistance/risk-plan cases need deterministic golden cases before any rule change.
- Too-strict trigger/close-confirmation cases need deterministic golden cases before any loosening is considered.
- Missing-context wording should be clearer while preserving conservative behavior.

No outcome R aggregation was recorded because this batch is calibration evidence only and not a backtest or performance study.

## Residual Limitations

- This reached the preferred 80-example first pass, but remains a paper/sanitized sample rather than live or private trading evidence.
- Examples are paper/sanitized review cases, not live or broker-executed records.
- No private trading data was used.
- No strategy rule was changed from this batch.
- Follow-up issues must create deterministic golden cases before implementation changes.

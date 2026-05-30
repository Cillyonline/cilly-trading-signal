# Next Milestone Decision

## Purpose

This document records the planning rebaseline after v2.1 Strategy Calibration and
its follow-up issues. It is not a production-readiness statement, strategy
validation, profitability claim, trading advice, broker-readiness claim,
live/realtime data claim, or permission for automatic order execution.

## Current Context

The project now supports the core single-operator review cockpit: Watchlist,
TradingView OHLCV CSV import, guarded manual Daily/EOD provider sync,
deterministic multi-timeframe analysis, explainable signals, benchmark-context
visibility, alert review, manual trade logging, journal and basic performance
views, plus TradingView screener CSV snapshots that can be explicitly converted
into Watchlist candidates.

v2.1 and its follow-ups improved strategy quality and reviewability:

- Professional strategy playbook and stock/crypto overlays are documented.
- Swing structure, pullback, breakout, stop/target, invalidation, market regime,
  relative strength, no-trade wording, and next actions are calibrated and tested.
- Stored benchmark context requirements for `SPY`/`QQQ` and `BTC`/`ETH` are visible
  in the Watchlist workflow.
- Analysis quality reports expose passed, warning, missing, and blocked checks.
- Calibration golden cases provide a focused regression suite for strategy labels.
- Historical/paper review has a documented protocol, but no app-supported batch
  workflow yet.

## Options Considered

| Option | Benefit | Risk / Reason Not First |
| --- | --- | --- |
| End-to-End Calibration Fixtures | Strengthens confidence that stored OHLCV, timeframes, and benchmark context produce expected strategy labels. | Still deterministic test coverage, not profitability evidence. |
| Historical/Paper Review Batches | Turns the new protocol into a practical workflow for repeated `useful`, `too_permissive`, `too_strict`, and `unclear` findings. | More product surface and data-model work; should stay clearly separate from backtesting/profit claims. |
| Screener Usability v2 | Makes daily candidate triage more practical with filtering, bulk review, pagination, and prioritization. | Useful, but should not bypass the calibrated signal-review workflow. |
| Operational Hardening | Improves deployment confidence, monitoring, and backup posture. | Important before broader exposure, but product planning currently needs the next review-quality increment. |
| Mobile/PWA | Improves daily access and alert/trade review on phone. | Better after the core review and calibration workflows stabilize. |
| Market Data v2 | Could reduce CSV friction and expand provider coverage. | Higher licensing, cost, freshness, and live/realtime-claim risk. |

## Decision Point

Recommended next planning discussion: choose between a strategy-quality increment
and a workflow-usability increment.

Recommended near-term technical next step: `#300 - Expand calibration golden cases
with full OHLCV and benchmark fixtures`.

Reasoning:

- It is the smallest high-leverage continuation of v2.1.
- It tests the full stored-data path behind the new benchmark-context and quality
  report work.
- It supports safer future rule changes before adding larger app workflows.
- It keeps the safety boundary clear: deterministic review fixtures are not
  strategy validation or profitability evidence.

Next candidate after `#300`: `#299 - Add app support for historical and paper
review batches`, if the user wants to start recording structured review evidence.

## Safety Boundaries

- Signals remain review prompts only and must not be described as guaranteed or
  validated trading opportunities.
- No automatic trade creation, broker action, order execution, profitability
  claim, live/realtime claim, or trading advice may be introduced.
- `No Trade`, stale data, missing benchmark context, duplicates, ignored, and
  rejected outcomes remain valid conservative stop points.

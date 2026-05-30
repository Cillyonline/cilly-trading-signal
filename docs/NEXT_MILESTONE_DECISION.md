# Next Milestone Decision

## Purpose

This document records the v2.0 rebaseline decision for the next product milestone.
It is not a production-readiness statement, strategy validation, profitability
claim, trading advice, broker-readiness claim, live/realtime data claim, or
permission for automatic order execution.

## Current Context

The project now supports the core single-operator review cockpit: Watchlist,
TradingView OHLCV CSV import, guarded manual Daily/EOD provider sync, deterministic
analysis, explainable signals, alert review, manual trade logging, journal and
basic performance views, plus TradingView screener CSV snapshots that can be
explicitly converted into Watchlist candidates.

The strongest remaining planning need is to make the analysis output more useful
as a professional review system before adding more workflow convenience.

## Options Considered

| Option | Benefit | Risk / Reason Not First |
| --- | --- | --- |
| Operational Hardening | Improves deployment confidence, monitoring, and backup posture. | Important, but recent private VPS hardening already created a controlled owner/operator baseline. It should continue in parallel when operational use expands. |
| Mobile/PWA | Improves daily access and alert/trade review on phone. | Useful after the review surfaces stabilize; otherwise mobile work may polish workflows that still need product iteration. |
| Analytics/Journal | Improves performance and process feedback. | Valuable after more sample/manual records exist; current pain is earlier in the candidate triage flow. |
| Screener Usability v2 | Makes the newly implemented screener CSV workflow practical for daily candidate triage. | Useful later, but secondary if the underlying signal quality is not yet actionable. |
| Strategy Calibration & Signal Quality | Improves the core value of the product: professional, explainable setup review and risk planning. | Requires careful rules, fixtures, and safety wording so it does not become a recommendation engine or profitability claim. |
| Market Data v2 | Could expand provider coverage and reduce CSV friction. | Higher licensing, cost, and data-freshness risk; must avoid live/realtime and automatic-analysis claims. Not the next safest increment. |

## Decision

Recommended next milestone: `v2.1 - Strategy Calibration & Signal Quality`.

Reasoning:

- The product's core value is useful, explainable analysis rather than more UI
  around weak signals.
- The current MVP strategy engine is deterministic and conservative, but it needs
  professional calibration around market regime, asset-specific filters, setup
  quality, triggers, stop/target logic, and no-trade actionability.
- Improving signal quality should happen before adding more screener convenience.

## Candidate Issues For v2.1

1. Define professional strategy playbook.
2. Define stock-specific signal filters.
3. Define crypto-specific signal filters.
4. Improve swing structure detection.
5. Improve Trend Pullback Long detection.
6. Improve Base Breakout Long detection.
7. Improve stop, target, and invalidation logic.
8. Add market regime and relative strength model.
9. Improve no-trade reasons and next actions.
10. Add analysis quality report.
11. Document strategy calibration workflow.

## Safety Boundaries

- Signals remain review prompts only and must not be described as guaranteed or
  validated trading opportunities.
- No automatic trade creation, broker action, order execution, profitability
  claim, live/realtime claim, or trading advice may be introduced.
- `No Trade`, stale data, duplicates, ignored, and rejected outcomes remain valid
  conservative stop points.

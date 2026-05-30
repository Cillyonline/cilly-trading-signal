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

The strongest remaining planning need is to turn the new screener workflow into a
more usable daily review surface without increasing execution risk or making data
freshness claims.

## Options Considered

| Option | Benefit | Risk / Reason Not First |
| --- | --- | --- |
| Operational Hardening | Improves deployment confidence, monitoring, and backup posture. | Important, but recent private VPS hardening already created a controlled owner/operator baseline. It should continue in parallel when operational use expands. |
| Mobile/PWA | Improves daily access and alert/trade review on phone. | Useful after the review surfaces stabilize; otherwise mobile work may polish workflows that still need product iteration. |
| Analytics/Journal | Improves performance and process feedback. | Valuable after more sample/manual records exist; current pain is earlier in the candidate triage flow. |
| Screener Usability v2 | Makes the newly implemented screener CSV workflow practical for daily candidate triage. | Must stay manual-review-only and avoid ranking or recommendation wording. This is manageable with conservative copy and scoped UI/API work. |
| Market Data v2 | Could expand provider coverage and reduce CSV friction. | Higher licensing, cost, and data-freshness risk; must avoid live/realtime and automatic-analysis claims. Not the next safest increment. |

## Decision

Recommended next milestone: `v2.1 - Screener Review Usability`.

Reasoning:

- v1.9 introduced the safe data model, import service, API, UI, and explicit
  Watchlist conversion.
- The next useful increment is review efficiency: filtering, status handling,
  duplicate visibility, and candidate auditability.
- This improves the top of the workflow without adding broker integration,
  automatic orders, automatic analysis, or trading advice.

## Candidate Issues For v2.1

1. Add screener result filters for status, asset class, exchange, sector, and Watchlist linkage.
2. Add explicit ignore/reject review actions for screener candidates.
3. Improve duplicate visibility across imports and existing Watchlist symbols.
4. Add pagination or bounded result limits before raising screener row limits.
5. Add screener import detail view with candidate counts and validation summary.
6. Document the screener review operating workflow after usability improvements.

## Safety Boundaries

- Screener rows remain review candidates only.
- Filters and status changes must not be described as recommendations.
- No automatic analysis, signal creation, trade creation, alert creation, broker
  action, order execution, profitability claim, live/realtime claim, or trading
  advice may be introduced.
- `No Trade`, stale data, duplicates, ignored, and rejected outcomes remain valid
  conservative stop points.

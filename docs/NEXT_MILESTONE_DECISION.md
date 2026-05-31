# Next Milestone Decision

## Purpose

This document records the planning rebaseline after v2.7 Mobile/PWA Owner Cockpit
and the start of v2.8 Final Internal Review Candidate work. It is not a production-readiness statement, strategy
validation, profitability claim, trading advice, broker-readiness claim,
live/realtime data claim, or permission for automatic order execution.

## Current Context

The project now supports the core single-operator review cockpit: Watchlist,
TradingView OHLCV CSV import, guarded manual Daily/EOD provider sync,
deterministic multi-timeframe analysis, explainable signals, benchmark-context
visibility, alert review, manual trade logging, journal and performance/risk
review, TradingView screener CSV snapshots that can be explicitly converted
into Watchlist candidates, and historical/paper review batches.

v2.1-v2.7 improved strategy quality, reviewability, operational posture, and mobile owner/operator usability:

- Professional strategy playbook and stock/crypto overlays are documented.
- Swing structure, pullback, breakout, stop/target, invalidation, market regime,
  relative strength, no-trade wording, and next actions are calibrated and tested.
- Stored benchmark context requirements for `SPY`/`QQQ` and `BTC`/`ETH` are visible
  in the Watchlist workflow.
- Analysis quality reports expose passed, warning, missing, and blocked checks.
- Calibration golden cases provide focused strategy-label regression coverage and
  end-to-end stored OHLCV plus benchmark-context fixtures.
- Historical/paper review has both a documented protocol and an app-supported batch
  workflow for process evidence.
- Review evidence workflows now include correction support, finding categories,
  repeated finding visibility, and known auditability follow-up gaps.
- Risk/portfolio review now includes open risk, max open risk warnings, asset concentration,
  simple correlation proxies, and process-oriented journal analytics.
- Operational readiness now includes monitoring checklist, structured health details,
  backup restore drill documentation, deployment readiness gate v2, dependency/container scan
  visibility, and an operational incident runbook.
- Mobile owner/operator usability now has an audit, improved signal/review batch flows,
  and a basic PWA manifest baseline.

## Options Considered

| Option | Benefit | Risk / Reason Not First |
| --- | --- | --- |
| Final internal workflow smoke test | Verifies the current post-v2.7 workflow end to end before handoff. | Requires Docker/browser availability and sanitized evidence discipline. |
| Final internal go/no-go decision gate | Gives an explicit owner/operator handoff decision with current evidence and gaps. | Must not become a production-readiness or real-money claim. |
| Gap cleanup | Addresses known follow-ups from v2.3-v2.7. | Useful, but should not block final internal review unless the gap affects handoff safety. |
| Screener/mobile/trade polish | Improves remaining dense mobile workflows. | Helpful, but can follow final internal candidate evidence. |
| Operational evidence hardening | Refreshes deployment readiness evidence and operational docs. | Broader production-like readiness still needs a separate gate. |
| Market Data v2 | Could reduce CSV friction and expand provider coverage. | Higher licensing, cost, freshness, and live/realtime-claim risk. |

## Decision Point

Recommended next step: complete v2.8 Final Internal Review Candidate.

Recently completed near-term technical steps:

- v2.5 Risk And Portfolio Review.
- v2.6 Operational Readiness.
- v2.7 Mobile/PWA Owner Cockpit.

Recommended v2.8 sequence:

- `#339` Rebaseline product docs for final internal review candidate.
- `#340` Run final internal workflow smoke test.
- `#341` Final internal go/no-go decision gate.

Reasoning:

- The current app has enough review, risk, operational, and mobile baseline capability
  to warrant a final internal owner/operator handoff check.
- The remaining v2.8 work is evidence and decision quality, not new product surface.
- Any final decision must keep deterministic fixtures, historical/paper review,
  security scans, and smoke checks separate from strategy validation, profitability
  evidence, production readiness, and execution.

## Safety Boundaries

- Signals remain review prompts only and must not be described as guaranteed or
  validated trading opportunities.
- No automatic trade creation, broker action, order execution, profitability
  claim, live/realtime claim, or trading advice may be introduced.
- `No Trade`, stale data, missing benchmark context, duplicates, ignored, and
  rejected outcomes remain valid conservative stop points.

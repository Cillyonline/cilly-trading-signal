# Historical And Paper Review Protocol

## Purpose

This protocol defines how to review calibrated signal outputs with historical or
paper samples. The goal is to learn whether the cockpit output is useful for
manual review and which rules need follow-up calibration.

This is not a backtest engine, strategy validation, trading advice, a
profitability claim, production-readiness evidence, broker-readiness evidence, a
live/realtime data claim, or permission for automatic order execution.

## Review Inputs

Allowed inputs:

- Stored CSV or provider-synced candle data already supported by the app.
- Paper examples created for review only.
- Historical examples using public market data and anonymized notes.
- Manual observations about whether signal wording, risk plan, and No Trade gates
  were useful.

Disallowed inputs:

- Private brokerage statements, account balances, API keys, fills, or screenshots
  containing personal or broker data.
- Claims that a sample proves expectancy or profitability.
- Any workflow that creates orders, broker actions, automatic trades, or automatic
  analysis refreshes.

## Sampling Rules

Use a fixed review window before looking at outcomes:

- Asset class: stock or crypto.
- Strategy: Trend Pullback Long, Base Breakout Long, or both.
- Time period or paper-review batch.
- Data source and freshness state.
- Benchmark/regime context availability.

Do not cherry-pick only successful examples. Include:

- Armed A/B setups.
- Watchlist candidates that never confirmed.
- No Trade outcomes from bearish regime, missing data, poor structure, no trigger,
  or weak risk plan.
- Examples where the system looked too strict or too permissive.

## Review Template

Create one row per reviewed signal or candidate:

| Field | Value |
| --- | --- |
| Review ID | Unique local identifier |
| Date reviewed | YYYY-MM-DD |
| Symbol | Public ticker only |
| Asset class | stock / crypto |
| Strategy | trend_pullback_long / base_breakout_long |
| Stored data date range | Start/end of stored candles |
| Benchmark context | Present, missing, stale, mixed, bearish |
| Signal status | armed / watchlist / no_setup / invalidated / missed / expired |
| Score class | a_setup / b_setup / watchlist / no_trade |
| Key no-trade reasons | Codes from signal output |
| Key risk flags | Codes from signal output |
| Quality report blockers | Blocked or missing checks |
| Entry / stop / target | Stored plan values if available |
| Planned R:R | Stored R:R if available |
| Manual review label | useful / too_permissive / too_strict / unclear |
| Paper or historical outcome R | Optional, if measured consistently |
| Outcome measurement rule | How R was measured, if used |
| Follow-up needed | yes / no |
| Follow-up issue | GitHub issue URL when created |
| Notes | Sanitized process notes only |

## Review Labels

Use these labels consistently:

- `useful`: output matched the playbook and gave a clear manual next step.
- `too_permissive`: output allowed review when a professional rule should have
  blocked or downgraded it.
- `too_strict`: output blocked or downgraded a case that the playbook says should
  be reviewable.
- `unclear`: output was technically safe but not understandable enough for manual
  review.

`too_strict` does not automatically justify loosening a rule. It must become a
calibration follow-up with a golden case before implementation changes.

## R-Multiple Handling

R-multiple review is optional and only valid when entry, stop, and outcome are
measured consistently.

Rules:

- Use the stored signal/trade risk plan where available.
- If no coherent stop exists, do not force an R value.
- Treat paper outcomes as review notes, not performance proof.
- Keep fees, slippage, gaps, and manual execution assumptions explicit when they
  materially affect the review.
- Do not aggregate small samples into profitability claims.

## Follow-Up Rule

Every `too_permissive`, `too_strict`, or repeated `unclear` label should create a
follow-up issue unless it is intentionally accepted as a limitation.

Follow-up issues should include:

- Sanitized example description.
- Expected playbook behavior.
- Actual signal output.
- A proposed golden case or fixture.
- Safety boundary confirmation: no broker action, automatic execution, live data,
  profitability claim, or trading advice.

Do not silently change strategy rules based on a review note alone.

## Minimum Review Summary

At the end of each batch, summarize:

- Number of reviewed examples.
- Count by strategy and asset class.
- Count by manual review label.
- Repeated blockers or missing-context patterns.
- Follow-up issues created.
- Residual limitations and whether more samples are required.

The summary is process evidence only. It must not be presented as proof of edge,
expected profit, live readiness, broker readiness, or production readiness.

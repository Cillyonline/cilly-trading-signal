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

## First Structured Sample Plan

The first calibration evidence batch should contain 50 to 100 reviewed examples.
It is intentionally a process-evidence sample, not a backtest, profitability study,
or proof of positive expectancy.

Recommended initial size:

- Minimum usable sample: 50 examples.
- Preferred first pass: 80 examples.
- Upper bound before recalibration review: 100 examples.

Asset split:

- Stocks: 60 percent of examples.
- Crypto: 40 percent of examples.
- If one asset class lacks enough clean stored data, keep the shortfall visible in
  the batch notes instead of replacing it with cherry-picked examples.

Strategy split:

- Trend Pullback Long: 40 percent of examples.
- Base Breakout Long: 40 percent of examples.
- No Setup / No Trade / missing-context cases: 20 percent of examples.

Score/status split targets:

- A/B setup outputs: 25 to 35 percent.
- Watchlist outputs that did not yet confirm: 25 to 35 percent.
- No Trade / No Setup outputs: 25 to 35 percent.
- Missing, stale, partial, failed, or unknown context cases: at least 10 percent,
  included within the groups above.

Sampling order:

1. Define the review window, asset universe, strategies, and data source before
   looking at outcomes.
2. Pull candidates in deterministic order, such as by import date, screener import
   order, signal creation date, or alphabetic symbol order within the fixed window.
3. Keep rejected, stale, missing-context, and No Trade cases in the sample.
4. Do not replace weak, boring, or inconclusive examples with more interesting
   winners or losers.
5. Stop at the planned sample size even if additional examples look attractive.

Labeling rules:

- Use `useful` when the output matches the playbook and gives a clear manual next
  step, including valid No Trade outcomes.
- Use `too_permissive` when the output allowed review despite a blocker that the
  playbook says should downgrade or block the setup.
- Use `too_strict` when the output blocked or downgraded a setup that the playbook
  says should remain reviewable with explicit risk context.
- Use `unclear` when the result may be safe but the reason, next action, or quality
  report is not understandable enough for manual review.
- Record `outcome_r` only when the stored risk plan and measurement rule are
  coherent; otherwise leave it blank.

Minimum batch notes:

- Fixed review window and source universe.
- Asset and strategy split achieved versus planned.
- Counts by status, score class, label, and blocker pattern.
- Missing or stale context count.
- Follow-up issues created or explicitly deferred.
- Statement that the sample is evidence for calibration discussion only and not
  profitability, live-readiness, broker-readiness, or trading advice.

## Review Template

Use the app review workflow at `/reviews` when available, or create one row per
reviewed signal or candidate manually when working outside the app:

- Create a fixed historical or paper review batch before evaluating outcomes.
- Add one structured entry per signal or candidate.
- Use `too_permissive`, `too_strict`, and repeated `unclear` labels to identify
  calibration follow-ups.
- Treat the batch summary as process evidence only, not backtest or profitability
  validation.

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
| Finding category | Persisted category code; keep `unknown` when unclear |
| Finding category source | `derived` when system-assigned, `manual` when reviewer-confirmed |
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

Finding categories are calibration evidence only. `derived` categories are
system-assigned from existing review evidence and may be corrected during manual
review. `manual` means a reviewer explicitly confirmed or corrected the category;
it does not request or authorize an automatic rule change.

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

## Recorded Batches

- First 80-example paper calibration batch:
  `docs/reviews/first-50-paper-calibration-batch.md`. The batch includes a
  follow-up status snapshot for issues `#473`-`#475` and `#480`-`#483`, including
  closed dispositions for resistance compression, missing-context clarity, and
  watchlist trigger-confirmation coverage.

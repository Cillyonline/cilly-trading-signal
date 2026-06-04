# v4.4 Practical Operator Workflow Decision

Date: 2026-06-04

## Decision

v4.4 will focus on a practical CSV-first operator workflow instead of expanding
provider reliance.

The owner/operator inputs are:

- Asset focus: mixed assets.
- Current Watchlist size: about 20 symbols.
- Expected Watchlist size: about 200 symbols in 6-12 months.
- `4H` provider data: useful if possible, but not required at zero budget.
- Update cadence: multiple updates can be useful for trigger review, but should be
  limited to a small trigger shortlist.
- Provider budget: 0 EUR.
- Priority: simple handling and practical daily use.

Given those constraints, TradingView CSV remains the operational baseline for `1W`,
`1D`, and `4H`. Alpha Vantage remains an optional guarded Daily/EOD smoke path only.
The configured Alpha Vantage smoke reached the provider path, but failed safely with
`provider_rate_limited`, which confirms that free/low-cost provider limits are not a
good foundation for broad 200-symbol multi-update operation.

## Operating Model

Use a three-level workflow instead of trying to refresh every symbol all day:

- Universe: up to about 200 mixed symbols for broad preparation.
- Active review shortlist: about 20-40 symbols that currently deserve manual review.
- Trigger shortlist: about 5-15 symbols near trigger or needing focused `4H` context.

Recommended cadence:

- `1W`: update weekly, preferably during weekend preparation.
- `1D`: update daily after close or before the next review session.
- `4H`: update only for the trigger shortlist, around relevant candle closes when the
  operator is actively monitoring.
- Crypto: can be reviewed more often, but still only for a small trigger shortlist.

## Provider Decision

Current decision:

- Do not select or pay for a broader provider now.
- Do not build operational reliance on Alpha Vantage beyond guarded Daily/EOD smoke.
- Do not try to update about 200 symbols multiple times per day with a free provider.
- Keep provider-neutral metadata and failure handling in place for future options.
- Keep TradingView CSV as the supported baseline and fallback.

Revisit paid provider evaluation only if one of these becomes true:

- The operator accepts a non-zero monthly provider budget.
- `4H`/intraday provider automation becomes mandatory for day-to-day usefulness.
- Manual CSV preparation becomes the main bottleneck after shortlist workflow polish.
- Storage/licensing terms, rate limits, and coverage are acceptable for the target
  asset universe.

## v4.4 Work Package

Planned issues:

- #625: record this practical operator workflow decision.
- #626: add a daily and weekly operator playbook.
- #627: add trigger-focused Import page guidance.
- #628: add an active review shortlist.
- #629: improve Trigger Radar operator workflow.

Recommended order:

1. Decision record.
2. Daily and weekly operator playbook.
3. Import guidance for targeted CSV updates.
4. Active review shortlist.
5. Trigger Radar workflow polish.

## Safety Boundaries

- No broker integration.
- No automatic order execution.
- No automatic trade creation.
- No automatic analysis or signal generation from data import.
- No scheduler-driven market-data sync in this decision.
- No live/realtime market-data claim.
- No provider-reliance, production-readiness, strategy-validation, or profitability
  claim.
- No secrets, `.env` values, provider keys, request URLs, raw payloads, private
  watchlists, cookies, broker data, account data, or fill data should be recorded in
  evidence.

## Done Criteria

v4.4 is done when the owner/operator can answer these questions quickly in the app or
docs:

- Which symbols should be reviewed today?
- Which symbols need `1W`, `1D`, or `4H` CSV refresh?
- Which near-trigger symbols deserve focused manual review?
- Which data problems block a setup from being considered?
- What remains manual-only and outside the system's execution boundary?

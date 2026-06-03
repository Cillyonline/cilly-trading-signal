# Cockpit Review Workflow

## Purpose

This document explains the intended manual review flow across the trading cockpit. It is a workflow guide for stored data, setup review, alerts, manual trade documentation, journal review, and historical R-multiple analysis.

It is not trading advice, a production-readiness claim, a live/realtime data claim, a broker-readiness claim, strategy validation, a profitability claim, or permission for automatic order execution.

For task-oriented navigation, start with [Owner/Operator Wiki](OWNER_OPERATOR_WIKI.md). For a practical browser walkthrough, use [Owner/Operator Cockpit Manual](OWNER_OPERATOR_COCKPIT_MANUAL.md). For dashboard-specific interpretation, use [Dashboard User Guide](DASHBOARD_USER_GUIDE.md).

## Safety Boundaries

- The app supports review and documentation only.
- Signals and alerts are prompts to review, not buy/sell instructions.
- `No Setup` and `No Trade` are valid conservative outcomes.
- Manual provider sync is disabled by default, guarded, and not a live market-data feed.
- No screen in this workflow creates broker orders or connects to a broker.
- Trades are records of external manual execution, not app-executed positions.
- Performance views summarize documented historical/paper records in R; they do not forecast results.

## Review Cadence

Use the cockpit in two loops:

- Daily or session review: check data freshness, current setup candidates, alert events, open trades, and trades needing review.
- Weekly review: audit stale symbols, closed trades without journal review, performance by documented R, and process notes.

Keep the sequence conservative:

1. Data context.
2. Setup review.
3. Trigger or alert review.
4. External manual execution if the user independently decides to act outside the app.
5. Manual trade log and management notes.
6. Close, journal, and performance review.

## End-To-End Flow

### 1. Dashboard Triage

Start on the Dashboard to identify the next review area:

- Stale or failed market-data context means the setup should not be treated as current.
- Active setup counts and review priorities are prompts to inspect details, not action instructions.
- Alerts, trades, and missing reviews should be handled before relying on summary metrics.
- If the Dashboard surfaces `No Setup`, `No Trade`, stale data, or missing review context, treat that as a valid stop point.

### 2. Watchlist And Data Context

Use Watchlist as the symbol universe, then verify data context before reviewing setups:

- CSV imports remain the manual baseline for `1W`, `1D`, and `4H` data.
- Provider sync, when configured, is a manual stored-data refresh for supported Daily/EOD data only.
- Source, sync status, and freshness should be checked before analysis output is interpreted.
- Failed, partial, stale, missing, or unknown data should push the workflow back to import/sync review or produce `No Trade`.

Do not infer live market state from stored candles. If current data is required, import or sync intentionally and rerun review steps after the stored data is updated.

### 3. Import And Provider Sync Review

For CSV imports:

- Verify symbol, asset class, timeframe, required OHLCV columns, candle count, and import result.
- Use the import result as stored historical context only.
- Run analysis only after the relevant timeframes are present and plausible.

For provider sync:

- Confirm provider sync is deliberately enabled in the environment.
- Review sanitized sync result, data source, provider context, freshness, and errors.
- Treat skipped, failed, partial, or unsupported timeframe results as review blockers, not silent success.
- Do not treat provider sync as scheduler behavior, realtime data, or automatic signal generation.

### 4. Signal Review

Use the Signal Radar to filter and group review candidates by German Ampel
decision, status, setup type, score band, and freshness context.

Ampel interpretation:

- `Paper-Kandidat` / green: strong enough for manual paper review; still not a real trade instruction.
- `Beobachten` / yellow: interesting, but wait for cleaner confirmation or trigger context.
- `Kein Trade` / red: rejected by No-Trade logic or quality blockers.
- `Datenproblem` / gray: data must be fixed before the setup is reviewable.

Signal interpretation rules:

- `watchlist` means interesting but incomplete.
- `armed` means prepared for manual trigger review.
- `triggered` means a review event occurred; it is not an entry instruction.
- `invalidated`, `missed`, and `expired` are terminal or cleanup-oriented review states.
- `No Setup` and `No Trade` are expected conservative outcomes when requirements are not met.

On Signal Detail, inspect reasoning, risk flags, no-trade reasons, entry/stop/target context, invalidation, and review history. A score describes setup quality only; it is not a probability, edge claim, or instruction.

### 5. Alert Event Review

Use Alerts as an audit trail for webhook and notification events:

- Filter by delivery status, review status, type, priority, and symbol.
- `pending`, `failed`, and `skipped` states require visible manual review.
- Skipped states can be expected when routing is disabled, a policy blocks delivery, dedup suppresses noise, or rate limits apply.
- Delivery success only means notification delivery was recorded; it does not validate a trade decision.
- Alert messages must remain review-oriented and must not imply automatic execution.

When an alert references a signal, inspect the signal detail before making any external decision. If data is stale or the setup is invalidated, keep the conservative outcome.

### 6. Manual Trade Logging

Only log trades that were executed manually outside the app.

Before logging:

- Confirm the trade is external/manual.
- Enter factual entry, stop, target, position size, opened time, fees, and notes where available.
- Use calculated risk and R:R as documentation checks, not permission to trade.
- If the trade plan is incomplete, document that explicitly rather than forcing a false value.

The Trades page highlights follow-up areas such as missing notes, missing first target, open close documentation, and journal review status. These indicators are factual documentation prompts and should not be read as profitability judgments.

### 7. Trade Management And Close

Use Trade Detail to document management events:

- Stop updates, target updates, and notes record external manual management.
- Close flow records exit price, exit reason, close time, and optional notes.
- Result amount and result R are derived from the documented record.
- Management alerts or exit warnings are review prompts only; they do not execute exits.

If a trade is still open, journal review may remain pending. If a trade is closed, review follow-up should be visible until the journal entry is completed.

### 8. Journal Review

Journal review should focus on process quality:

- Setup rule followed.
- Entry, stop, exit, and discipline quality.
- Market context.
- Emotional notes.
- What went well, what went wrong, and lesson learned.

Journal completion changes review status, but it does not rewrite the historical result. Avoid hindsight claims that imply a strategy was proven by one record.

### 9. Performance Review

Use Performance after trades are documented and reviewed:

- Review total R, average R, win rate, and distribution as historical records.
- Segment by strategy only when enough documented records exist for useful review.
- Treat open trades, missing reviews, and incomplete notes as data-quality context.
- Do not interpret the view as forecast, production validation, or profitability promise.

For structured historical or paper signal-output review, use
`docs/HISTORICAL_PAPER_REVIEW_PROTOCOL.md` and create follow-up issues for repeated
`too_permissive`, `too_strict`, or unclear outcomes.

Weekly review should identify process follow-ups: stale symbols, repeated no-trade reasons, missing journals, incomplete trade plans, and alert routing noise.

## Conservative Stop Points

Stop or defer review when:

- Required timeframe data is missing, stale, failed, partial, or unknown.
- Signal reasoning is unclear or the setup is invalidated.
- Risk/reward does not meet configured rules.
- Alert delivery failed or was skipped and the underlying event has not been reviewed.
- A trade record lacks enough factual data to compute or interpret risk.
- Journal review is missing for closed trades.

Stopping at `No Trade`, `No Setup`, `stale`, `failed`, or `needs review` is correct behavior.

## Evidence And Privacy

When recording screenshots, smoke-test notes, issue comments, or PR evidence:

- Use sample/paper data whenever possible.
- Do not include provider API keys, Telegram tokens, chat IDs, webhook secrets, cookies, private journal text, personal trade details, raw logs with credentials, or backup dumps.
- Redact private VPS and operational evidence before sharing.

## Owner-Operator Cockpit Validation Checklist

Use this checklist after cockpit UI polish or before considering any VPS or
service-impacting rollout. This is local/sample validation evidence only. It is
not production approval, broker readiness, strategy validation, a profitability
claim, trading advice, or permission for automatic execution.

Validation setup:

| Field | Result |
| --- | --- |
| Date | YYYY-MM-DD |
| Commit or branch |  |
| Environment | local / sample / paper |
| Desktop viewport | pass / fail / blocked / not run |
| Mobile viewport | pass / fail / blocked / not run |
| Private data included | no |
| Secrets, cookies, raw logs, or `.env` values included | no |

Route checklist:

| Route | Desktop | Mobile | Evidence Notes |
| --- | --- | --- | --- |
| `/reviews/[id]` | pass / fail / blocked / not run | pass / fail / blocked / not run | Follow-up disposition is visible; draft remains manual evidence only. |
| `/screener` | pass / fail / blocked / not run | pass / fail / blocked / not run | Candidate status, validation, and explicit Watchlist conversion are scannable. |
| `/trades/[id]` | pass / fail / blocked / not run | pass / fail / blocked / not run | Manage, Close, and Journal groups are visually distinct. |

Safety boundary checks:

- Review follow-up drafts do not automatically create GitHub issues or change
  strategy rules.
- Screener candidates remain stored review candidates until the user explicitly
  confirms Watchlist conversion.
- Watchlist conversion does not create analysis, signals, trades, alerts, broker
  actions, or orders automatically.
- Trade Detail events, closes, and journal entries document external manual
  decisions only.
- No route claims live/realtime data, profitability, strategy validation, broker
  readiness, or trading advice.

Validation outcome:

| Finding | Follow-up |
| --- | --- |
| No blocking cockpit friction found | none |
| Minor wording/layout friction | create scoped UI/docs issue |
| Safety boundary unclear | create high-priority follow-up before rollout |
| Requires VPS or service restart | stop and request explicit operator approval |

## Related Docs

- `docs/MVP_SPEC.md`
- `docs/MVP_SMOKE_TEST.md`
- `docs/PROVIDER_SYNC_SMOKE_TEST.md`
- `docs/MARKET_DATA_FRESHNESS_MODEL.md`
- `docs/HISTORICAL_PAPER_REVIEW_PROTOCOL.md`
- `docs/STRATEGY_AND_ALERTS.md`
- `docs/DATA_MODEL.md`

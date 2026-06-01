# Trade Journal Privacy Review

## Purpose

This review identifies privacy and sensitivity risks around manual trades, trade events, journal entries, and performance records before private owner/operator trading data is considered. It does not approve routine private-data use, production-like exposure, broker readiness, real-money readiness, profitability validation, strategy validation, trading advice, or automatic execution.

## Current Decision

Status: Private trade and journal content remains No Go for shared evidence and routine private-data use.

Use sample, synthetic, paper, or explicitly sanitized records for issues, PRs, docs, logs, screenshots, and browser smoke evidence.

## Sensitive Fields

The following fields can identify strategy, account behavior, personal decision-making, or private financial context when real records are used:

| Area | Sensitive fields | Why sensitive |
| --- | --- | --- |
| Trade record | `symbol`, `entry_price`, `stop_loss`, `target_1`, `target_2`, `position_size`, `fees`, `opened_at`, `closed_at`, `exit_price`, `exit_reason`, `initial_risk_amount`, `initial_risk_percent`, `result_amount`, `result_r`, `notes` | Reveals private watchlists, timing, sizing, risk, realized outcome, and process notes. |
| Trade event | `event_time`, `price`, `quantity`, `old_value`, `new_value`, `reason`, `notes` | Reveals manual management decisions, stop/target changes, timing, and rationale. |
| Journal entry | `market_context`, `emotional_notes`, `what_went_well`, `what_went_wrong`, `lesson_learned`, quality scores, `reviewed_at` | Reveals personal process, emotional state, mistakes, lessons, and decision quality. |
| Performance summary | total/average R, win rate, winners/losers, drawdown-like sequences, strategy/asset grouping, active risk, concentration, correlation proxy, journal analytics | Aggregates can reveal private performance, exposure, strategy behavior, and account-level risk posture. |
| Related records | watchlist notes, screener imports, provider metadata, alerts, review notes, backup/restore rows | Can link private symbols and trading context across views. |

## Exposure Paths

Private trade and journal content can leak through:

- API responses from `/api/trades`, `/api/trades/{id}`, `/api/trades/{id}/events`, `/api/trades/{id}/journal`, and `/api/performance/summary`.
- Browser screenshots of `/trades`, `/trades/[id]`, `/performance`, Dashboard cards, alerts, and review workflows.
- Terminal output from curl/manual API checks, pytest failures, application logs, database queries, backup/restore verification, and smoke scripts.
- PostgreSQL dumps, Restic snapshots, restored row checks, CSV exports, copied local storage/session data, and raw provider/import payloads.
- Issue comments, PR descriptions, markdown evidence, incident notes, chat transcripts, and attached screenshots.

## Allowed Evidence

- Pass/fail status for trade, journal, and performance pages using sample, synthetic, fake, or paper-only records.
- Counts, status enums, route names, migration version, commit SHA, check links, and sanitized error-code categories.
- Ranges or redacted values when needed, for example `position_size=redacted`, `symbol=sample`, `result_r=present/not present`.
- Screenshots only when they contain sample/paper records and no private symbols, notes, account context, cookies, tokens, or local storage values.
- Follow-up issue links that describe the gap without reproducing private data.

## Forbidden Evidence

- Real private symbols, private watchlists, private screener rows, private trade notes, journal text, emotional notes, mistake/lesson text, account balances, broker statements, fill records, order IDs, or screenshots of broker/provider dashboards.
- Raw API responses, raw logs, database query output, PostgreSQL dump contents, restored rows, Restic repository URLs with credentials, cookies, tokens, database URLs, `.env` values, or local/session storage dumps.
- Performance exports or screenshots showing real private result amounts, R sequences, win/loss counts, active exposure, concentration, or strategy grouping unless explicitly approved and redacted.
- Claims that private trade/journal evidence proves profitability, strategy validity, live trading readiness, production readiness, broker readiness, or real-money readiness.

## Handling Guidance

- Prefer sample/paper records for every workflow check until the private-data gate is explicitly changed.
- If a private-data issue is suspected, document only the route/view, timestamp, environment class, sanitized symptom, and follow-up action.
- Do not paste raw request/response bodies for trade, journal, or performance endpoints when private records may exist.
- Do not run ad hoc SQL that prints private notes, result rows, account context, or restored row contents into terminal evidence.
- Before sharing a screenshot, check visible table rows, cards, browser address bar, cookies/devtools, local storage, account dashboards, and notification content.
- Treat backups and restored databases as sensitive even when they are encrypted; verify schema/version/counts without exposing row contents.

## Minimum Review Before Private-Data Gate Change

Before routine private owner/operator trading data use is reconsidered:

- This privacy review remains current for trade, journal, and performance fields.
- Private-data evidence rules are documented and linked from the owner/operator docs.
- Backup/restore recurrence and evidence rules are current.
- Incident rehearsal covers database restore, secret rotation, and private-data exposure handling.
- The owner/operator explicitly accepts residual risk without posting private data.

## Final Review Statement

Trade notes, journal entries, and performance records are sensitive private trading data when real owner/operator records are used. They must stay out of issues, PRs, docs, logs, screenshots, terminal evidence, and chat unless a later private-data gate explicitly approves a redacted evidence process. Current workflows should continue using sample, synthetic, paper, or sanitized records only.

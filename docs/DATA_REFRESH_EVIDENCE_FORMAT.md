# Data Refresh Evidence Format

## Purpose

This format defines sanitized evidence for manual CSV and guarded provider data
refresh checks. It applies to local checks and explicitly approved private-staging
checks.

Data refresh evidence is process evidence only. It is not a production-readiness
statement, live or realtime data claim, broker-readiness claim, profitability
claim, strategy-validation claim, trading advice, or approval for automatic
execution.

## When To Use

Use this format when recording evidence for:

- Manual CSV refresh of `1W`, `1D`, or `4H` data.
- Guarded manual provider sync as part of a refresh workflow.
- Import Readiness review after CSV or provider refresh.
- Fallback decisions for missing, stale, failed, partial, skipped, unsupported, or
  unknown data states.
- No-automation checks after refresh.

Do not use this format to paste CSV rows, private watchlist symbols, provider
payloads, request URLs, screenshots with private data, cookies, `.env` values,
provider keys, broker data, or account details.

## Required Evidence Fields

```markdown
## Data Refresh Evidence

- Date/time UTC:
- Operator or role:
- Environment class: local / private staging / other sanitized class
- Approval gate: not required for local / approved by owner-operator / not approved
- Branch or commit SHA:
- Refresh scope: universe / active review shortlist / trigger shortlist / sample-only
- Data source path: TradingView CSV / guarded provider sync / mixed / not run
- Symbol scope: fake sample / public sample / redacted private / aggregate only
- Timeframes checked: 1W / 1D / 4H / sanitized subset
- CSV import status: pass / fail / not run
- Provider sync status: success / skipped / failed / partial / not run
- Freshness state observed: fresh / stale / unknown / failed / partial / mixed / not run
- Readiness state observed: complete / missing timeframe / insufficient candles / data problem / not run
- CSV fallback used or recommended: yes / no / not applicable
- Sanitized error category: none / missing_timeframe / insufficient_candles / provider_rate_limited / provider_symbol_or_entitlement / provider_transport_error / provider_invalid_response / provider_empty_response / other sanitized category
- Import history updated: pass / fail / not run
- Manual analysis started: yes by explicit operator action / no / not applicable
- No automatic analysis, signal, trade, order, broker action, position sizing, or alert created: pass / fail / not run
- Follow-up issue or PR:
- Secrets, provider keys, request URLs, raw payloads, raw CSV rows, cookies, screenshots with sensitive data, private symbols, broker data, provider account details, or private trading records included: no
- Production-readiness, live/realtime, broker-readiness, profitability, strategy-validation, trading-advice, or automatic-execution claim made: no
```

## Allowed Evidence

Allowed refresh evidence is limited to:

- Date/time, operator role, branch, commit SHA, issue, PR, and CI links.
- Environment class such as `local` or `private staging`.
- Refresh scope such as `universe`, `active review shortlist`, `trigger
  shortlist`, or `sample-only`.
- Symbol scope such as `fake sample`, `public sample`, `redacted private`, or
  `aggregate only`; avoid private symbol names.
- Timeframe labels: `1W`, `1D`, `4H`, or a sanitized subset.
- Status enums and categories: `pass`, `fail`, `not run`, `success`, `skipped`,
  `failed`, `partial`, `fresh`, `stale`, `unknown`, `complete`, `missing
  timeframe`, `insufficient candles`, and `data problem`.
- Sanitized error categories only, with no copied provider or CSV payload.
- Aggregate counts, for example number of symbols checked or number missing a
  timeframe, when those counts do not reveal private strategy or account data.
- Follow-up issue or PR links.

## Forbidden Evidence

Never include these in issues, PRs, docs, logs, screenshots, terminal output, or
chat:

- `.env` values, API keys, bearer tokens, cookies, session headers, database URLs,
  provider keys, provider secrets, or password-manager contents.
- Raw CSV rows, private CSV files, broker exports, provider payloads, request URLs,
  query strings, copied logs, HTTP headers, stack traces with sensitive context, or
  database rows.
- Private watchlist symbols, private screener rows, private notes, broker/account
  data, order IDs, fills, balances, journal text, performance exports, provider
  account details, dashboards, subscription tiers, billing details, or quota
  dashboards.
- Screenshots by default. If a later approved workflow permits screenshots, they
  must be sample-only and sanitized before they are used as evidence.
- Claims that refresh evidence proves production readiness, live or realtime data,
  broker readiness, profitability, strategy validity, real-money readiness,
  trading advice, or approval for automatic execution.

## Refresh Status Categories

Use only sanitized categories in shared evidence:

| Category | Meaning | Operator-safe recovery |
| --- | --- | --- |
| `complete` | Required `1W`, `1D`, and `4H` context is present for the checked symbol scope. | Manual analysis may be started only by explicit operator action. |
| `missing_timeframe` | At least one required timeframe is absent. | Import CSV or use guarded provider sync only when symbol/timeframe coverage is clear. |
| `insufficient_candles` | Stored data has too few candles for the intended review. | Import more CSV history or skip the symbol. |
| `stale` | Stored data is older than the review window expects. | Refresh the timeframe or skip this cycle. |
| `failed` | Import or provider sync failed. | Use CSV fallback or record a sanitized blocker. |
| `partial` | Refresh produced incomplete usable data. | Fill gaps with CSV before analysis. |
| `skipped` | Provider sync did not run, usually disabled or not configured. | Use CSV fallback; do not treat skipped as coverage evidence. |
| `unknown` | Freshness or source cannot be trusted. | Verify source or use CSV fallback. |

## Environment Boundaries

Local checks may use local sample data and local secrets that stay outside git and
outside evidence. Private-staging checks require explicit owner/operator approval
before any environment change, provider-key setup, restart, smoke run, rollback, or
cleanup operation.

For both local and private staging:

- Keep refresh checks sample-only or sanitized when evidence is shared.
- Prefer aggregate or redacted symbols when private watchlist composition is
  sensitive.
- Use CSV fallback when provider coverage, entitlement, freshness, mapping,
  payload shape, or rate-limit status is unclear.
- Do not infer broad watchlist coverage from one provider or CSV refresh sample.
- Do not add scheduler-driven sync, automatic refresh, or automatic analysis as
  part of evidence collection.

## Downstream Safety Boundary

Every refresh evidence record should include a no-automation check. Data refresh
must not create analysis, signals, trades, alerts, orders, broker actions, position
sizing, or executions automatically.

If any downstream object is created unexpectedly, stop the run, record only a
sanitized failure category, and create a follow-up issue.

## Related Docs

- `docs/DAILY_WEEKLY_OPERATOR_PLAYBOOK.md`
- `docs/OWNER_OPERATOR_COCKPIT_MANUAL.md`
- `docs/PRIVATE_DATA_EVIDENCE_HANDLING.md`
- `docs/PROVIDER_OPERATIONAL_EVIDENCE_FORMAT.md`
- `docs/BROWSER_SMOKE_EVIDENCE_FORMAT.md`

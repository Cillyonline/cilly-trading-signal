# Provider Operational Evidence Format

## Purpose

This format defines sanitized evidence for future provider-smoke, private-staging,
or broader provider-reliance decisions. It applies to local and explicitly
approved private-staging checks.

Provider operational evidence is process evidence only. It is not a production
readiness statement, live or realtime data claim, broker-readiness claim,
profitability claim, strategy-validation claim, trading advice, or approval for
automatic execution.

## When To Use

Use this format when recording:

- Disabled provider-sync checks.
- Configured provider-smoke checks with an operator-owned key outside git.
- Private-staging provider checks after explicit owner/operator approval.
- Follow-up investigations for provider rate limits, entitlement, symbol mapping,
  unsupported timeframe, transport, invalid response, or empty response outcomes.

Do not use this format to paste raw provider payloads, request URLs, logs, keys,
account screens, private symbols, private CSVs, or screenshots with sensitive data.

## Required Evidence Fields

```markdown
## Provider Operational Evidence

- Date/time UTC:
- Operator or role:
- Environment class: local / private staging / other sanitized class
- Approval gate: not required for local / approved by owner-operator / not approved
- Branch or commit SHA:
- Provider identifier: twelve_data / alpha_vantage / not configured / redacted
- Provider key location: local env only / staging env only / not configured / not inspected
- Symbol scope: fake sample / public provider-recognized sample / redacted private
- Timeframes checked: 1W / 1D / 4H / other sanitized list
- Check type: disabled / configured provider / failure-path / private-staging
- Observed sync_status: success / skipped / failed / partial / not run
- Observed freshness_status: fresh / stale / unknown / failed / partial / not run
- Sanitized error category: none / unsupported_timeframe / provider_rate_limited / provider_symbol_or_entitlement / provider_transport_error / provider_invalid_response / provider_empty_response / other sanitized category
- Latest candle timestamp visible: pass / fail / not run
- Import history updated: pass / fail / not run
- No automatic analysis, signal, trade, order, broker action, or alert created: pass / fail / not run
- CSV fallback guidance shown or documented: pass / fail / not run
- Follow-up issue or PR:
- Secrets, provider keys, request URLs, raw payloads, cookies, screenshots with sensitive data, private symbols, provider account details, broker data, or private trading records included: no
- Production-readiness, live/realtime, broker-readiness, profitability, strategy-validation, trading-advice, or automatic-execution claim made: no
```

## Allowed Evidence

Allowed provider evidence is limited to:

- Date/time, operator role, branch, commit SHA, issue, PR, and CI links.
- Environment class such as `local` or `private staging`; do not include hostnames,
  account identifiers, provider dashboards, private paths, or secrets.
- Provider identifier such as `twelve_data` or `alpha_vantage`; do not include
  provider account, billing, subscription, or dashboard details.
- Symbol scope such as `fake sample`, `public provider-recognized sample`, or
  `redacted private`; do not include private watchlist symbols.
- Timeframe labels: `1W`, `1D`, `4H`, or sanitized unsupported labels.
- Status enums: `success`, `skipped`, `failed`, `partial`, `fresh`, `stale`,
  `unknown`, and `not run`.
- Sanitized error categories, including `unsupported_timeframe`,
  `provider_rate_limited`, `provider_symbol_or_entitlement`,
  `provider_transport_error`, `provider_invalid_response`, and
  `provider_empty_response`.
- Boolean or pass/fail checks for latest timestamp visibility, Import history,
  downstream no-automation, CSV fallback guidance, and redaction review.
- Follow-up issue or PR links when a provider gap needs separate work.

## Forbidden Evidence

Never include these in issues, PRs, docs, logs, screenshots, terminal output, or
chat:

- `.env` values, API keys, bearer tokens, cookies, session headers, database URLs,
  SSH keys, provider keys, provider secrets, or password-manager contents.
- Raw provider payloads, request URLs, query strings, HTTP headers, copied logs,
  stack traces with sensitive context, database rows, or private CSV contents.
- Provider account IDs, dashboards, subscription tiers, billing details, quota
  dashboards, invoices, or entitlement screens.
- Private watchlist symbols, private notes, broker exports, order IDs, fills,
  balances, account data, journal text, performance exports, or screenshots that
  expose private trading records.
- Claims that provider evidence proves production readiness, live or realtime
  data, broker readiness, profitability, strategy validity, trading advice,
  real-money readiness, or approval for automatic execution.

## Status And Error Categories

Use only sanitized categories in shared evidence:

| Category | Meaning | Operator-safe recovery |
| --- | --- | --- |
| `success` | Stored provider data was accepted for the tested environment and timeframe. | Review freshness and history before any separate manual analysis. |
| `skipped` | Sync did not run, usually because provider sync is disabled or not configured. | Use TradingView CSV fallback or verify configuration outside evidence channels. |
| `partial` | Provider returned incomplete or unusable-enough data for a full review cycle. | Fill gaps with TradingView CSV before analysis. |
| `unsupported_timeframe` | Current provider path does not support the requested timeframe. | Use TradingView CSV or a supported provider/timeframe path. |
| `provider_rate_limited` | Provider rate limit or quota blocked the request. | Wait, reduce manual scope, or use TradingView CSV. |
| `provider_symbol_or_entitlement` | Symbol mapping, asset coverage, timeframe, or plan entitlement blocked the request. | Verify coverage outside evidence channels or use TradingView CSV. |
| `provider_transport_error` | Network or provider transport failed. | Retry later or use TradingView CSV. |
| `provider_invalid_response` | Provider response shape could not be used safely. | Do not paste payload; use TradingView CSV until reviewed. |
| `provider_empty_response` | Provider returned no usable candles. | Verify symbol coverage outside evidence channels or use TradingView CSV. |

## Environment Boundaries

Local checks may be run by the operator with local secrets outside git. Private
staging checks require explicit owner/operator approval before any environment
change, provider-key setup, restart, smoke run, rollback, or cleanup operation.

For both local and private staging:

- Keep provider secrets outside git, issues, PRs, docs, terminal output, and chat.
- Record only sanitized status evidence after the check.
- Do not include screenshots by default; if a later approved workflow permits them,
  screenshots must be sample-only and sanitized.
- Do not infer broad watchlist, asset-class, exchange, plan-entitlement, or
  production-like reliability from a single public-symbol smoke.
- Keep TradingView CSV as the fallback when coverage, entitlement, freshness,
  mapping, payload shape, or rate-limit status is unclear.

## Downstream Safety Boundary

Every provider operational evidence record should include an explicit no-automation
check. Provider sync must not create analysis, signals, trades, alerts, orders,
broker actions, position sizing, or executions automatically.

If any downstream object is created unexpectedly, stop the run, record only a
sanitized failure category, and create a follow-up issue.

## Related Docs

- `docs/PROVIDER_SYNC_SMOKE_TEST.md`
- `docs/PRIVATE_DATA_EVIDENCE_HANDLING.md`
- `docs/BROWSER_SMOKE_EVIDENCE_FORMAT.md`
- `docs/MARKET_DATA_PROVIDER_DECISION.md`

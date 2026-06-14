# Post-Refresh Validation Evidence Format

## Purpose

This format defines sanitized evidence for post-refresh operator validation checks.
It complements `docs/POST_REFRESH_OPERATOR_VALIDATION_CHECKLIST.md` and applies to
local or explicitly approved private-staging checks with sample, synthetic, or
paper data only.

Post-refresh validation evidence is process evidence only. It is not production
readiness, live or realtime data evidence, broker-readiness evidence,
profitability evidence, strategy-validation evidence, trading advice, real-money
readiness, or approval for automatic execution.

## Required Evidence Fields

```markdown
## Post-Refresh Validation Evidence

- Date/time UTC:
- Operator or role:
- Environment class: local / private staging / disposable test / other sanitized class
- Approval gate: not required for local / approved by owner-operator / not approved
- Branch or commit SHA:
- Browser and viewport class: desktop / narrow mobile / both / not run
- Data scope: sample / synthetic / paper only
- Sample symbol scope: fake sample / public sample / aggregate only / redacted
- Checklist used: `docs/POST_REFRESH_OPERATOR_VALIDATION_CHECKLIST.md`
- Routes or workflows checked: `/login`, `/`, `/watchlist`, `/import`, `/signals`, `/signals/[id]`, `/trades`, `/trades/[id]`, `/performance`, `/alerts`, logout
- Refresh path checked: CSV / guarded provider sync / mixed / not run
- Import Readiness status: pass / fail / blocked / not run
- CSV fallback guidance visible: pass / fail / blocked / not run
- Provider fallback guidance visible: pass / fail / blocked / not run
- Manual analysis boundary visible: pass / fail / blocked / not run
- Signal review boundary visible: pass / fail / blocked / not run
- Manual trade logging boundary visible: pass / fail / blocked / not run
- No automatic analysis, signal, trade, order, broker action, position sizing, or alert created: pass / fail / blocked / not run
- Failed or blocked steps:
- Sanitized failure category: none / route_unavailable / refresh_guidance_unclear / fallback_guidance_missing / manual_boundary_missing / unexpected_downstream_creation / private_data_exposure / other sanitized category
- Follow-up issues or PRs:
- Screenshots captured: no / sanitized sample-only
- Secrets, `.env` values, provider keys, request URLs, raw payloads, raw CSV rows, cookies, local storage, screenshots with sensitive data, private symbols, broker data, provider account details, or private trading records included: no
- Production-readiness, live/realtime, broker-readiness, profitability, strategy-validation, trading-advice, real-money-readiness, or automatic-execution claim made: no
```

## Allowed Evidence

Allowed evidence is limited to:

- Date/time, operator role, branch, commit SHA, issue, PR, and CI links.
- Environment class and approval-gate status.
- Browser and viewport class.
- Route names and workflow names checked.
- Pass, fail, blocked, skipped, or not-run status.
- Fake/sample symbol scope or aggregate counts that do not reveal private strategy
  or account data.
- Sanitized failure categories and follow-up issue links.
- Explicit `no` confirmations for sensitive data and false readiness claims.

## Forbidden Evidence

Never include these in issues, PRs, docs, logs, screenshots, terminal output, or
chat:

- `.env` values, API keys, bearer tokens, cookies, session headers, local storage,
  database URLs, provider keys, provider secrets, or password-manager contents.
- Raw CSV rows, private CSV files, broker exports, provider payloads, request URLs,
  query strings, copied logs, HTTP headers, stack traces with sensitive context, raw
  API responses, or database rows.
- Private watchlist symbols, private screener rows, private notes, broker/account
  data, order IDs, fills, balances, journal text, performance exports, provider
  account details, dashboards, subscription tiers, billing details, or quota
  dashboards.
- Screenshots by default. If screenshots are explicitly allowed in a later check,
  they must be sample-only, sanitized, and free of browser storage, account data,
  private symbols, provider dashboards, and secrets.
- Claims that validation evidence proves production readiness, live or realtime
  data, broker readiness, profitability, strategy validity, trading advice,
  real-money readiness, or approval for automatic execution.

## Failure Categories

Use only sanitized categories in shared evidence:

| Category | Meaning | Expected handling |
| --- | --- | --- |
| `route_unavailable` | A route or page cannot be reached or loaded. | Record route class and create a follow-up. |
| `refresh_guidance_unclear` | Refresh state does not make the next manual action clear. | Create a focused UI/docs follow-up. |
| `fallback_guidance_missing` | CSV/provider fallback is not visible when data cannot be trusted. | Create a focused UI/docs follow-up. |
| `manual_boundary_missing` | UI copy could imply automatic analysis, trade, broker action, or advice. | Stop validation and create a safety follow-up. |
| `unexpected_downstream_creation` | Refresh creates downstream records without explicit operator action. | Stop validation and create a high-priority follow-up. |
| `private_data_exposure` | Evidence would expose private data, secrets, raw rows, or account context. | Stop and record only sanitized blocker metadata. |

## Relationship To Other Evidence Formats

- Use `docs/DATA_REFRESH_EVIDENCE_FORMAT.md` for refresh-specific evidence before
  or during data import/sync checks.
- Use `docs/BROWSER_SMOKE_EVIDENCE_FORMAT.md` for broader route-level browser
  smoke evidence.
- Use `docs/PRIVATE_DATA_EVIDENCE_HANDLING.md` for general privacy rules.
- Use `docs/PROVIDER_OPERATIONAL_EVIDENCE_FORMAT.md` for provider-smoke,
  entitlement, rate-limit, or broader provider-reliance evidence.

## Final Boundary

A passing post-refresh validation check proves only that the sampled manual
workflow behaved as expected in the tested environment. It does not approve private
trading data, real-money trading, production-like exposure, broker integration,
automatic execution, live/realtime data, profitability, or strategy validation.

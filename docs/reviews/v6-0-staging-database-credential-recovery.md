# v6.0 Staging Database Credential Recovery Evidence

## Scope

This evidence records the sanitized private-staging database credential recovery
performed after the v5.9 deploy and before the v5.9 sample/paper-only browser
validation.

It is operations evidence only. It is not production readiness, private trading
data readiness, broker-readiness evidence, live/realtime market-data evidence,
profitability evidence, strategy validation, trading advice, real-money readiness,
or approval for automatic execution.

## Context

- Date/time UTC: 2026-06-17
- Environment class: private staging
- Target class: private owner/operator VPS staging
- Repository path: `/srv/apps/cilly-trading-signal`
- Compose project: `cilly-trading-signal`
- Deployment commit checked before browser validation:
  `6539e4e482c8e35e68b84a60ffb2fc91bcafde94`
- Related validation evidence:
  `docs/reviews/v5-9-paper-trade-workflow-validation.md`
- Related issue: #785

## Failure Summary

During the private-staging update, the API container started and health/web checks
were reachable, but `alembic upgrade head` initially failed with a sanitized
database authentication category:

- Failure category: `db_auth_failed`
- Affected operation: Alembic migration check from the API container
- Sanitized cause: API database connection user/password state did not match the
  initialized PostgreSQL role state.
- Secrets included in evidence: no
- Database rows, dumps, or private trading records included: no

The update also showed an operations hygiene issue: running Docker Compose without
the intended project name can create a conflicting partial stack. This is handled
as a runbook follow-up in #786.

## Recovery Actions

The recovery was performed by the owner/operator on private staging with sanitized
commands and without sharing secret values.

| Check or action | Result | Sanitized notes |
| --- | --- | --- |
| Confirm repository path | Pass | Correct path identified as `/srv/apps/cilly-trading-signal`. |
| Confirm deployment commit | Pass | VPS commit matched `origin/main` for v5.9 validation. |
| Identify mistaken partial Compose stack | Pass | A partial default-project stack was identified and removed before continuing. |
| Restart intended Compose project | Pass | Intended project name: `cilly-trading-signal`. |
| Inspect API/Postgres env shape | Pass | Only redacted presence/user/db/host class was inspected; no secret value recorded. |
| Reset DB credential alignment | Pass | A new database password was generated and applied without publishing it. |
| Restore PostgreSQL client auth config | Pass | `pg_hba.conf` was confirmed restored to its normal header state after recovery. |
| Preserve database volume | Pass | No database volume deletion was performed. |
| Alembic `upgrade head` | Pass | Migration check completed after recovery. |
| API health | Pass | `https://trading.cillyonline.de/api/health` returned `ok`. |
| Web load | Pass | `https://trading.cillyonline.de` returned HTTP 200. |

## Final State

- Overall recovery result: pass
- `pg_hba.conf` temporary recovery state left active: no
- `pg_hba.conf.bak` leftover reported in final check: no
- Alembic `upgrade head`: pass
- API health: pass
- Web load: pass
- Follow-up required: yes, #786 should document a repeatable staging deploy and
  migration recovery runbook so this path is not rediscovered ad hoc.

## Evidence Boundaries

The following were not included in this evidence, PRs, or shared notes:

- `.env` contents or `DATABASE_URL` value
- Old or new database password
- API keys, provider keys, bearer tokens, cookies, SSH keys, or session data
- Raw database rows, database dumps, SQL query output with private records, backup
  contents, or restored row contents
- Private symbols, watchlists, notes, trades, journals, performance exports,
  broker/account records, order IDs, fills, balances, or screenshots
- Production-readiness, private-data-readiness, broker-readiness, profitability,
  strategy-validation, trading-advice, real-money-readiness, live/realtime, or
  automatic-execution claims

## Residual Risk

The credential state is recovered, but the previous ad hoc recovery path shows
that staging operations need a documented runbook. #786 should cover correct
repository path, Compose project naming, mistaken-stack cleanup, migration checks,
health checks, and safe DB credential mismatch triage without exposing secrets or
deleting database volumes.

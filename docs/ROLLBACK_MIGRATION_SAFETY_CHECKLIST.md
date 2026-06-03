# Rollback And Migration Safety Checklist

## Purpose

This checklist defines conservative decision points for app rollback, database
migration uncertainty, restore decisions, and deployment stop conditions.

It is guidance only. It does not run migrations, roll back code, restore data,
restart services, approve production-like exposure, approve private-data use,
make a production-readiness claim, or approve automatic execution.

## Current Decision

Status: checklist only.

Production-like exposure remains No Go until a separate current decision gate
records target-specific rollback, migration, restore, monitoring, backup, and
owner/operator acceptance evidence.

## Pre-Deployment Decision Points

Before a production-like candidate deployment, record these decisions without
including secrets, database URLs, raw logs, private data, or dump contents:

| Decision | Required answer before rollout | Stop if unclear |
| --- | --- | --- |
| Target environment | Exact Compose project, domain, data class, and operator are known. | Yes |
| Intended commit | Current commit and previous known-good commit are recorded. | Yes |
| Migration delta | Expected Alembic head and whether migrations are included are known. | Yes |
| Backup freshness | Recent backup exists outside the repository and expected backup target class is known. | Yes |
| Restore path | Disposable restore procedure and target class are known before any destructive repair. | Yes |
| App rollback path | Previous app version can be checked out and rebuilt if database remains compatible. | Yes |
| DB compatibility assumption | Owner/operator knows whether previous app version is expected to work with the post-migration schema. | Yes |
| Data-changing freeze | Operator knows when imports, analysis, trade logging, provider sync, and review workflows must stop. | Yes |
| Evidence boundary | Pass/fail evidence can be recorded without exposing secrets or private data. | Yes |

## Decision Matrix

| Situation | First response | App rollback acceptable? | Restore decision point | Required evidence |
| --- | --- | --- | --- | --- |
| Deploy fails before migration starts | Stop rollout, keep current running version if healthy, inspect sanitized build/container status. | Usually yes if DB was untouched. | Restore normally not needed. | Commit, services status, health pass/fail, migration not started. |
| Migration command fails before applying changes | Stop rollout and data-changing workflows, inspect sanitized migration output. | Possibly, only if schema is confirmed unchanged. | Restore only if schema state is uncertain or changed. | Expected head, current head, failure category, backup freshness. |
| Migration partially applied or schema state unclear | Stop immediately, do not rerun blindly, freeze data-changing workflows. | No, not until schema compatibility is understood. | Test restore or repair on disposable target before touching live data. | Current head if safe, backup status, disposable-test plan. |
| App starts but DB-backed pages fail | Stop data-changing workflows, check health/details if safe, inspect migration version. | Only if schema is compatible with previous app. | Consider restore if migration changed schema and rollback cannot run safely. | Health category, migration version, affected workflow. |
| New app has business/UI regression with no migration | Stop affected workflow, roll back app commit if previous version is known-good. | Yes, if DB was untouched and previous image builds. | Restore not needed unless data was corrupted. | Previous commit, current commit, health after rollback. |
| New app has data corruption suspicion | Stop reliance and all data-changing workflows, preserve evidence. | No blind rollback; rollback may hide symptoms but not repair data. | Disposable restore/diagnosis required before live repair. | Affected workflow, backup freshness, incident record. |
| Backup missing or stale during failure | Stop rollout and data-changing workflows. | Only non-destructive app rollback may be considered if DB untouched. | Live destructive repair is No Go until backup state is understood. | Backup status, owner/operator decision. |
| Evidence would expose secrets or private data | Stop sharing evidence and redact locally. | Not a rollback decision by itself. | Not a restore decision by itself. | Sanitized summary only or private operator note. |

## Stop Conditions

Stop the rollout and freeze data-changing workflows when any of these are true:

- Alembic head is unexpected or migration output is ambiguous.
- A migration may have partially applied.
- API health fails because of database or migration errors.
- DB-backed pages fail after deployment.
- Backup freshness, backup target, or restore path is unknown.
- The previous app version's schema compatibility is unknown.
- Logs or evidence cannot be reviewed without exposing secrets or private data.
- The selected Compose project or restore target might affect unrelated `staging`,
  private staging, production-like data, or real records.

Data-changing workflows include imports, provider sync, analysis runs, alert
routing changes, trade logging, journal/performance edits, review corrections,
database repair, backup deletion, and restore attempts.

## Rollback Evidence Template

```markdown
## Rollback And Migration Safety Evidence

- Date/time UTC:
- Environment: private staging / production-like candidate / disposable target
- Current commit:
- Previous known-good commit:
- Expected Alembic head:
- Current Alembic head: <version only>/not checked
- Migration included in rollout: yes/no
- Migration state: not started / completed / failed before change / partial or unclear
- API health: pass/fail/not checked
- DB-backed workflow status: pass/fail/not checked
- Backup freshness checked: yes/no
- App rollback considered: yes/no
- App rollback run: yes/no
- Restore considered: yes/no
- Restore target class: disposable / not selected / not applicable
- Data-changing workflows frozen: yes/no/not needed
- Follow-up issue or incident:
- Secrets/private data/raw logs/dump contents included: no
- Production-like approval granted by this evidence: no
```

## No-Go Conditions

Production-like reliance remains blocked when any of these are true:

- Target-specific rollback evidence is missing for the intended release.
- Migration compatibility is assumed but not documented.
- Restore decision points are unclear for schema-changing releases.
- A backup is missing, stale, or unverified before a potentially destructive
  repair.
- Rollback or restore evidence requires exposing secrets, private data, raw logs,
  dump contents, database URLs, or restored rows.
- Owner/operator acceptance is absent for residual rollback, restore-time,
  migration, and data-loss risks.

## Final Statement

This checklist makes rollback and migration decisions explicit. It does not prove
the current target is production-like ready and does not approve private-data
use, broker integration, automatic execution, live/realtime claims,
profitability claims, or trading advice.

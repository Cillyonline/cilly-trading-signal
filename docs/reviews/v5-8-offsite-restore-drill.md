# v5.8 Offsite Restore Drill Evidence

Date: 2026-06-14

## Scope

This file records the v5.8 offsite restore-drill status for issue #757.

This is a private-staging operations artifact only. It is not production-readiness
evidence, public SaaS readiness, broker-readiness evidence, profitability
evidence, strategy-validation evidence, trading advice, real-money readiness, or
approval for automatic execution.

## Dependency

The offsite restore drill depends on a configured owner/operator-controlled
offsite encrypted backup repository.

Issue #756 is blocked/not configured because no offsite backup target or
credentials were provided for v5.8. Therefore, the offsite restore drill cannot be
run safely in this milestone.

## Safe Restore-Drill Procedure

Do not run this procedure until issue #756 has a passing offsite encrypted backup
configuration and sanitized snapshot evidence.

When an offsite backup exists, run the restore drill only on a disposable target:

1. Confirm the live `cilly-trading-signal` private-staging stack is healthy.
2. Confirm the unrelated `staging` project is separate and will not be touched.
3. Load Restic credentials from the private environment file or password manager;
   never print the values.
4. Restore the latest `cilly-postgres` snapshot into a disposable filesystem path,
   not the live app checkout or live database volume.
5. Verify only sanitized facts such as non-zero dump presence, migration/schema
   version, and sample marker presence if available.
6. Restore into a disposable database project if database-level verification is
   needed.
7. Clean up the disposable restore container, network, volume, and temporary files.
8. Re-check live staging API and web health.

Forbidden during the drill:

- Restoring into the live staging database.
- Printing dump contents, raw SQL rows, database URLs, Restic credentials,
  `RESTIC_PASSWORD`, repository URLs with credentials, private symbols, journal
  text, broker/account data, screenshots with sensitive data, or private trading
  records.
- Touching the unrelated `staging` Compose project.

## Sanitized Evidence

- Date/time UTC: not run in v5.8
- Operator or role: owner/operator
- Environment class: private staging
- Repository category: not available; blocked by #756
- Snapshot ID prefix: not applicable
- Snapshot count: not applicable
- Restore target: not run
- Disposable target isolation: not run
- Restored dump non-zero: not run
- Restored schema version: not run
- Cleanup completed: not run
- Live staging API health after drill: not run
- Live staging HTTPS web health after drill: not run
- Existing unrelated `staging` project unaffected: not touched by this issue
- Failed or blocked steps: no configured offsite encrypted backup repository exists
  for v5.8
- Follow-up issues or PRs: required if private-data readiness remains a goal
- Secrets, repository credentials, dump contents, restored rows, database URLs,
  backup provider account details, private notes, screenshots with sensitive data,
  or private trading records included: no
- Production-readiness, live/realtime, broker-readiness, profitability,
  strategy-validation, trading-advice, real-money-readiness, or
  automatic-execution claim made: no

## Current Status

Status: blocked by #756 / not run in v5.8.

No offsite restore drill was executed. Local VPS backups and unverified offsite
backup procedures remain insufficient for approving private trading data or
broader VPS reliance.

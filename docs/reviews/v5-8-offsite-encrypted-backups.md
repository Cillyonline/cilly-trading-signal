# v5.8 Offsite Encrypted Backups Evidence

Date: 2026-06-14

## Scope

This file records the v5.8 offsite encrypted backup configuration status for issue
#756.

This is a private-staging operations artifact only. It is not production-readiness
evidence, public SaaS readiness, broker-readiness evidence, profitability
evidence, strategy-validation evidence, trading advice, real-money readiness, or
approval for automatic execution.

## Existing Procedure

The offsite encrypted backup operating model is already documented in
`docs/DEPLOYMENT_RUNBOOK.md#offsite-encrypted-backups`:

- Use client-side encrypted Restic backups.
- Store the repository on an owner/operator-controlled offsite target such as SFTP,
  S3-compatible object storage, or another approved private target.
- Keep Restic credentials and `RESTIC_PASSWORD` outside the repository, for example
  in `/etc/cilly-trading-signal/offsite-backup.env` with mode `600`.
- Store the Restic password or recovery key in the operator password manager.
- Record only sanitized evidence: target category, snapshot count, snapshot ID
  prefix if needed, `restic check` status, and no-secret confirmation.

## Required Operator Inputs

Offsite encrypted backups cannot be configured from repository-only context. The
owner/operator must provide, outside GitHub/chat/docs, all of the following:

- Approved target category: offsite SFTP, offsite S3-compatible, or another private
  target.
- Restic repository location and credentials.
- Restic password or recovery key stored in a password manager.
- Agreement on retention and access boundaries.

No repository PR, issue, or chat message may contain repository credentials,
access keys, `RESTIC_PASSWORD`, bucket URLs containing secrets, private account
details, provider dashboards, dump contents, database URLs, or private trading
data.

## Sanitized Evidence

- Date/time UTC: not configured in v5.8
- Operator or role: owner/operator
- Environment class: private staging
- Repository category: blocked / not selected for v5.8
- Target class approved by owner/operator: not provided
- Restic credential path created: not run in v5.8
- Restic repository initialized: not run in v5.8
- Latest local PostgreSQL dump source checked: not run in v5.8
- Offsite backup executed: not run in v5.8
- Latest snapshot ID prefix: not applicable
- Snapshot count for `cilly-postgres` tag: not applicable
- Retention policy observed: not run in v5.8
- `restic check`: not run in v5.8
- Restore drill target: not run; tracked separately by issue #757
- Existing unrelated `staging` project unaffected: not touched by this issue
- Failed or blocked steps: owner/operator offsite target and credentials not provided
- Follow-up issues or PRs: required if private-data readiness remains a goal
- Secrets, repository credentials, dump contents, restored rows, database URLs,
  backup provider account details, private notes, screenshots with sensitive data,
  or private trading records included: no
- Production-readiness, live/realtime, broker-readiness, profitability,
  strategy-validation, trading-advice, real-money-readiness, or
  automatic-execution claim made: no

## Current Status

Status: blocked / not configured in v5.8.

The safe operating model exists, but no offsite target or credentials were approved
for execution in this session. Local VPS backups alone remain insufficient for
private trading data or broader VPS reliance.

Do not treat this issue as private-data readiness pass evidence until an
owner/operator configures the offsite encrypted target and records sanitized backup
evidence.

# Offsite Backup And Restore Acceptance Checklist

## Purpose

This checklist defines the evidence needed before offsite encrypted backups can
support future private-data or production-like readiness reconsideration.

It does not select a provider, configure backups, run Restic, run Docker, perform
a restore, rotate secrets, approve private-data use, approve production-like
exposure, make a production-readiness claim, or approve automatic execution.

## Current Decision

Status: checklist only.

No offsite/geographic backup target has been accepted as complete readiness
evidence. Private-data reliance and production-like exposure remain No Go until a
separate gate records current sanitized evidence and explicit owner/operator
acceptance.

## Acceptance Checklist

| Area | Required evidence before reliance | Status before operator run |
| --- | --- | --- |
| Target class | Target category selected from operator-controlled SFTP, private S3-compatible, managed Restic-compatible, or another explicitly reviewed private target. | `operator-required` |
| Geographic separation | Target is outside the VPS host and outside the local workstation failure domain. | `operator-required` |
| Encryption | Restic client-side encryption is used before data leaves the source environment. | `operator-required` |
| Credential handling | `RESTIC_PASSWORD`, repository credentials, access keys, SSH keys, and provider credentials are stored outside git, issues, PRs, screenshots, logs, docs, and chat. | `operator-required` |
| Password recovery | Restic password or recovery key exists in the operator password manager and is not stored only on the VPS. | `operator-required` |
| Backup source | Source path is the external PostgreSQL backup directory, not the repository checkout or raw database volume. | `operator-required` |
| Backup freshness | Latest offsite backup exists, is non-zero at the source, has a snapshot ID prefix, and has a recorded timestamp. | `operator-required` |
| Repository check | `restic check` passes after initial setup and on the accepted recurrence. | `operator-required` |
| Retention | Retention follows at least 14 daily and 8 weekly snapshots unless a stricter owner/operator policy is recorded. | `operator-required` |
| Restore target | Restore drill uses a disposable target that is not `cilly-trading-signal`, `staging`, or any production-like database. | `operator-required` |
| Restore proof | Restored dump is non-zero and can be restored into a disposable database with sanitized schema/version evidence only. | `operator-required` |
| Cleanup | Disposable restore project, network, volume, and restore directory are cleaned up after evidence is recorded. | `operator-required` |
| Monitoring | Backup freshness, failed backup, failed `restic check`, stale restore drill, and storage pressure have operator-visible escalation. | `operator-required` |
| Evidence handling | Evidence contains pass/fail status only and excludes secrets, repository URLs with credentials, dump contents, restored rows, database URLs, private symbols, trade notes, journal notes, provider account data, and raw sensitive logs. | repo rule plus `operator-required` |
| Residual-risk acceptance | Owner/operator accepts target/provider/account recovery, retention, ransomware, restore-time, and evidence-handling residual risks. | `operator-required` |

## Minimum Recurrence Before Reconsideration

- Backup run: after each successful PostgreSQL dump during active reliance,
  normally daily when the backup timer is enabled.
- `restic check`: at least weekly and after any target, credential, password,
  timer, source-path, restore-procedure, or backup-host change.
- Restore drill: at least monthly, before private-data or production-like
  approval, and after target class, retention policy, repository password,
  database major version, or deployment-host changes.
- Evidence review: before any decision gate changes private-data or
  production-like status from No Go.

## Accepted Evidence Template

```markdown
## Offsite Backup And Restore Acceptance Evidence

- Date/time UTC:
- Environment: private staging / disposable restore / production-like candidate
- Commit SHA:
- Target category: SFTP / S3-compatible / managed Restic-compatible / other private target
- Geographic separation from VPS and local workstation: yes/no
- Restic client-side encryption: pass/fail
- Credential storage outside git/issues/docs/logs/screenshots/chat: yes/no
- Password-manager recovery recorded by operator: yes/no
- Latest source dump non-zero before offsite backup: pass/fail/not checked
- Latest snapshot ID prefix: <prefix only>
- Snapshot count for app backup tag: <number>
- Retention policy observed: pass/fail
- Restic check: pass/fail
- Restore target class: disposable / not run
- Restored dump non-zero: pass/fail/not run
- Restored schema version: <version only>/not run
- Cleanup completed: yes/no/not run
- Monitoring/escalation for backup freshness reviewed: yes/no
- Owner/operator accepted residual risk: yes/no
- Secrets/repository credentials/dump contents/restored rows/DB URLs/private data/raw logs included: no
- Private-data or production-like approval granted by this evidence: no
```

## No-Go Conditions

Private-data reliance and production-like exposure remain blocked when any of
these are true:

- The target is local-only, same-host-only, or in the same broad failure domain
  without an explicit accepted limitation.
- Restic encryption, password recovery, credential storage, backup freshness,
  `restic check`, retention, or restore evidence is missing.
- The restore target is not disposable or could affect `cilly-trading-signal`,
  `staging`, production-like data, or private records.
- Evidence includes secrets, repository credentials, dump contents, restored rows,
  database URLs, private trading records, raw sensitive logs, or provider/account
  details.
- Owner/operator residual-risk acceptance is absent.

## Operator-Required Actions

These actions require explicit owner/operator approval and must not be performed
as unattended repo-only work:

- Choose or configure an offsite provider or storage target.
- Create, edit, inspect, rotate, or paste backup credentials or Restic passwords.
- Run `restic init`, `restic backup`, `restic check`, `restic forget`, or
  `restic restore`.
- Run Docker Compose restore drills, create restore directories, copy dump files,
  or clean up restore volumes on a live host.
- Change backup timers, retention behavior, filesystem permissions, or monitoring
  routes.

## Final Statement

This checklist defines what must be proven later. It is not proof that offsite
backup or restore readiness is complete, and it does not approve private-data
use, production-like exposure, broker integration, automatic execution,
live/realtime claims, profitability claims, or trading advice.

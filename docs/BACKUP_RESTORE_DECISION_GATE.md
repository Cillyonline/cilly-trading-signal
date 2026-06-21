# Backup And Restore Decision Gate

## Purpose

This document records the v6.1 decision for encrypted offsite backup and restore
drill scope after the v6.0 staging operations rebaseline.

It does not configure backups, run Restic, run Docker, perform a restore, rotate
secrets, approve private trading data, approve production-like exposure, make a
production-readiness claim, or approve automatic execution.

## Decision

Status: Deferred.

Encrypted offsite backup and offsite restore drill remain deferred for the current
controlled owner/operator sample/paper-only private-staging scope.

The project should not implement an offsite backup repository, backup credentials,
Restic commands, retention commands, or restore drill as part of v6.1. If the
owner/operator later wants broader staging reliance, private-data readiness, or
production-like readiness, backup and restore must become a separate explicit
operations gate with scoped implementation issues.

## Rationale

- v5.8 recorded offsite encrypted backup as blocked/not configured because no
  offsite target or credentials were provided.
- v5.8 recorded offsite restore drill as blocked because no configured offsite
  encrypted backup repository existed.
- v6.0 improved staging deploy and migration recovery, but it did not configure an
  offsite target, backup repository, Restic credentials, retention policy, backup
  monitoring, or restore drill.
- Private trading data remains No-Go under
  `docs/PRIVATE_DATA_READINESS_DECISION_GATE.md`.
- Current usage remains controlled owner/operator sample/paper-only private staging,
  where the residual backup/restore risk is accepted as a known limitation rather
  than treated as pass evidence.

## Options Reviewed

| Option | Decision | Reason |
| --- | --- | --- |
| Keep backup/restore deferred | Selected | Matches current owner/operator sample/paper-only scope and avoids unsafe credential or repository setup without explicit target approval. |
| Backup-only next | Not selected now | Would still require owner-selected target, credentials, password-manager recovery, and sanitized evidence before any command is run. |
| Backup plus disposable restore drill next | Not selected now | Correct future readiness path, but requires the backup-only prerequisites plus a disposable restore target and explicit owner/operator acceptance. |

## Required Future Gate Before Implementation

If backup/restore becomes the next explicit operations gate, create separate scoped
issues before any server or credential operation:

- Define encrypted offsite backup target and credential handling.
- Define backup runbook and sanitized evidence format for the chosen target.
- Define disposable restore drill runbook and cleanup boundaries.
- Run operator-approved backup/check/retention/restore commands only after
  credentials are prepared outside git, issues, PRs, docs, screenshots, logs, and
  chat.
- Record sanitized evidence using
  `docs/OFFSITE_BACKUP_RESTORE_ACCEPTANCE_CHECKLIST.md`.

## Evidence Boundaries

Allowed shared evidence:

- Decision status: deferred / backup-only next / backup-plus-restore next.
- Target category only, if selected later: SFTP / S3-compatible / managed
  Restic-compatible / other reviewed private target.
- Check status, command names, environment class, issue/PR links, and sanitized
  pass/fail fields.

Forbidden shared evidence:

- `.env` values, `RESTIC_PASSWORD`, backup repository URLs, access keys, SSH keys,
  provider account IDs, bucket names if private, invoices, billing details,
  database URLs, database dumps, restored rows, raw logs, screenshots with
  sensitive data, private symbols, broker/account records, or private trading data.

## Current Boundary

This deferred decision is not pass evidence for offsite backup readiness, restore
readiness, private-data readiness, production-like exposure, broker readiness,
profitability, strategy validation, trading advice, real-money readiness, or
automatic execution.

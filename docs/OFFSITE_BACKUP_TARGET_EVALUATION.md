# Offsite Backup Target Evaluation

## Purpose

This document evaluates stronger offsite or geographic backup targets beyond the current local encrypted Restic repository. It does not select or configure a provider, rotate secrets, perform a restore, approve private-data use, or make a production-readiness claim.

## Current Decision

Status: No offsite/geographic target selected.

Current local encrypted Restic repository: useful as operator-controlled encrypted redundancy, but local-only backup remains a blocker for private-data reliance and production-like exposure.

Local-only encrypted backup limitations:

- Not geographic redundancy.
- Not ransomware-resistant if the same workstation, credentials, or mounted storage can be affected.
- Not sufficient evidence for production-like exposure or routine private trading data use.
- Still requires recurring restore evidence and safe password-manager recovery handling.

## Evaluation Criteria

| Criterion | Requirement before reliance |
| --- | --- |
| Geographic separation | Backup target is outside the VPS host and outside the local workstation failure domain. |
| Client-side encryption | Restic encryption is used before data leaves the source environment. |
| Credential isolation | Repository credentials and `RESTIC_PASSWORD` are stored outside git, issues, PRs, docs, logs, screenshots, and chat. |
| Restore evidence | Latest backup can be restored into a disposable target with sanitized evidence only. |
| Retention support | Target supports at least the documented 14 daily / 8 weekly snapshot expectation or a stricter accepted policy. |
| Operational simplicity | Owner/operator can run, monitor, rotate, and restore without fragile manual steps. |
| Cost and lock-in | Cost, provider dependency, and account recovery risks are understood. |
| Privacy | Provider/account metadata, repository URLs, and restored data are not exposed in shared evidence. |

## Candidate Options

| Option | Strengths | Tradeoffs | Fit |
| --- | --- | --- | --- |
| Operator-controlled SFTP storage on a separate host | Simple Restic support, easy restore model, clear filesystem semantics, can be geographically separate. | Requires host hardening, SSH key management, patching, disk monitoring, and provider/account recovery planning. | Good first offsite option if the operator already controls a separate host. |
| S3-compatible object storage | Mature Restic support, lifecycle controls, geographic regions, durable storage, common provider tooling. | Requires access-key handling, bucket privacy configuration, cost monitoring, and provider-specific recovery process. | Good default for durable offsite storage when configured privately and tested. |
| Managed backup/storage provider with Restic-compatible backend | May reduce infrastructure maintenance and improve durability. | Provider lock-in, account recovery dependency, unclear restore semantics until tested, pricing surprises. | Acceptable if Restic restore drill and secret handling are verified. |
| Encrypted removable/offline media | Can improve ransomware resistance if kept disconnected and offsite. | Manual process, higher risk of stale backups, physical loss, harder recurrence evidence. | Useful as secondary offline redundancy, not sufficient alone for routine operations. |
| Current local Windows encrypted Restic repository | Already accepted as local encrypted redundancy and operator-controlled. | Same broad failure domain as local workstation; not geographic; not ransomware-resistant by itself. | Keep as secondary/local redundancy only. |

## Recommended Direction

Preferred path before private-data or production-like reliance is reconsidered:

1. Choose either operator-controlled SFTP on a separate host or private S3-compatible object storage as the first offsite/geographic target.
2. Configure Restic client-side encryption from the VPS backup source path using a server-local env file with mode `600` and password-manager recovery.
3. Run `restic init`, first backup, `restic check`, retention command, and a restore drill into a disposable target.
4. Record only sanitized evidence: target category, snapshot ID prefix, snapshot count, check pass/fail, restore target class, schema version, and cleanup status.
5. Keep the local Windows encrypted Restic repository as secondary redundancy, not as the primary readiness target.

## Secret Handling Boundary

- Do not commit or paste `RESTIC_PASSWORD`, repository URLs containing credentials, access keys, SSH private keys, bucket names if private, provider account IDs, invoices, billing identifiers, database URLs, dump contents, or restored rows.
- Store Restic password/recovery key in the operator password manager and not only on the VPS.
- Store target credentials in a root-only or deploy-user-only environment file outside the repository, such as `/etc/cilly-trading-signal/offsite-backup.env` with mode `600`.
- Rotate or replace credentials only with explicit operator approval because this can break backup and restore access.

## Residual Risks Until Replaced

Until an offsite/geographic target is selected, configured, backed up, checked, and restored from successfully:

- Private-data readiness remains No Go.
- Production-like exposure remains No Go.
- Local encrypted Restic remains a useful secondary backup but not geographic or ransomware-resistant evidence.
- A successful local restore drill does not prove offsite recovery.
- Shared evidence must continue to avoid secrets, private trading data, dump contents, restored rows, and sensitive provider/account context.

## Acceptance Evidence Template

```markdown
## Offsite Backup Target Evaluation Evidence

- Date/time UTC:
- Selected target category: SFTP / S3-compatible / managed Restic-compatible / offline secondary / none
- Geographic separation from VPS and local workstation: yes/no/not selected
- Client-side Restic encryption planned: yes/no
- Credential storage plan outside git: yes/no
- Restore drill completed from this target: yes/no
- Snapshot retention policy supported: yes/no
- Local-only encrypted Restic limitation still applies: yes/no
- Follow-up issue:
- Secrets, repository credentials, dump contents, restored rows, DB URLs, or private data included: no
```

## Final Evaluation Statement

The current local encrypted Restic repository should remain secondary redundancy only. A stronger offsite/geographic target, successful encrypted backup, `restic check`, retention evidence, and disposable restore drill are required before private-data or production-like reliance can be reconsidered.

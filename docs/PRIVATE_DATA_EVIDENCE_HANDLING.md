# Private Data Evidence Handling

## Purpose

This document defines how evidence may be captured for private-data readiness without leaking secrets or private trading records. It applies to GitHub issues, PRs, docs, logs, screenshots, terminal output, smoke evidence, incident notes, and chat excerpts.

It is not a production-readiness statement, live/realtime market-data claim, broker-readiness claim, profitability claim, strategy-validation claim, trading advice, or approval for automatic execution.

## Default Rule

Use sample, synthetic, fake, paper, or explicitly sanitized data for all shared evidence. If evidence cannot be shared without revealing secrets or private trading data, do not share the evidence; record the blocker and create a follow-up issue with sanitized metadata only.

## Allowed Evidence

Allowed evidence may be posted in issues, PRs, docs, and checklists when it contains no secrets or private records:

| Evidence type | Allowed examples |
| --- | --- |
| Check status | `pass`, `fail`, `not run`, `skipped with reason`, CI links, command names. |
| Environment class | `local`, `private staging`, `disposable restore target`, `sample-only browser smoke`. |
| Version context | Commit SHA, branch name, migration revision, PR number, issue number. |
| Sanitized app state | Status enums, counts, route names, timestamps rounded or redacted when private, fake/sample symbol names. |
| Backup evidence | Repository category, snapshot ID prefix, snapshot count, `restic check` pass/fail, disposable restore target class. |
| Incident evidence | Affected workflow, severity, health pass/fail, data-changing operations stopped yes/no, follow-up issue link. |
| Screenshots | Sample/paper-only screenshots with no private symbols, notes, account data, cookies, tokens, devtools, or browser storage. |

## Redacted Evidence

Redacted evidence may be used only when the private value is removed before sharing:

| Original type | Redacted format |
| --- | --- |
| Symbol or watchlist name | `symbol=sample`, `symbol=redacted`, or a fake public symbol used only for smoke testing. |
| Trade sizing/result | `position_size=redacted`, `result_amount=redacted`, `result_r=present/not present`. |
| Private notes | `notes=present/redacted`; do not summarize sensitive journal content. |
| Provider or backup target | `target_category=SFTP`, `provider_name=<configured provider>` without account IDs, request URLs, or credentials. |
| Error details | Sanitized error-code category, for example `provider_rate_limited`, `auth_failed`, `restore_target_not_disposable`. |
| Logs | Minimal lines after removing tokens, cookies, database URLs, private rows, request URLs, and account context. |

Redaction must remove the sensitive value, not merely blur it in a screenshot when the original file might still contain readable text or metadata.

## Forbidden Evidence

Never include these in issues, PRs, docs, logs, screenshots, terminal output, attachments, or chat:

- `.env` files, API keys, bearer tokens, cookies, session headers, database URLs, SSH keys, provider keys, Telegram tokens/chat IDs, backup repository credentials, `RESTIC_PASSWORD`, or password-manager contents.
- Raw API responses, raw provider payloads, raw application logs with private rows, SQL query output containing records, local/session storage dumps, browser devtools storage screenshots, or copied request headers.
- PostgreSQL dumps, Restic repository URLs with credentials, restored row contents, backup file contents, private restore directories, or screenshots of backup tooling that reveal account/path context.
- Private watchlists, private symbols, private screener rows, trade notes, journal notes, emotional notes, lesson/mistake text, fill records, order IDs, broker statements, account balances, provider dashboards, or billing/subscription details.
- Performance exports or screenshots showing private result amounts, R sequences, win/loss counts, active exposure, concentration, or strategy grouping unless a later gate explicitly approves a redacted evidence process.
- Any wording that presents private-data evidence as production readiness, live/realtime readiness, broker readiness, profitability validation, strategy validation, trading advice, or real-money readiness.

## Channel Rules

| Channel | Rule |
| --- | --- |
| GitHub issues | Use sanitized facts, checkboxes, route names, pass/fail, and follow-up links only. Do not attach private screenshots or logs. |
| Pull requests | Summarize behavior and verification commands. Do not include secrets, private rows, raw logs, or private screenshots. |
| Docs | Document procedures and boundaries, not private operational values or copied private records. |
| Terminal output | Before pasting, inspect for tokens, cookies, database URLs, request URLs, private notes, row contents, paths, and account context. Prefer pass/fail summaries. |
| Logs | Share only short, redacted excerpts needed to explain the issue. Prefer sanitized error categories. |
| Screenshots | Use sample/paper data; crop browser chrome/devtools; verify no cookies, local storage, account dashboards, or private records are visible. |
| Chat | Treat chat as shared evidence. Do not paste secrets, private trading content, raw logs, or raw provider responses. |

## Evidence Templates

Safe generic evidence:

```markdown
- Date/time UTC:
- Environment class: local / private staging / disposable target
- Workflow:
- Commit SHA:
- Check or command: <name only>
- Result: pass/fail/skipped
- Sanitized details:
- Follow-up issue:
- Secrets/private data/raw logs/screenshots with sensitive data included: no
```

Safe screenshot evidence:

```markdown
- Page/view:
- Data class: sample / synthetic / fake / paper
- Private symbols or notes visible: no
- Cookies/tokens/local storage/devtools visible: no
- Account/provider/broker dashboard visible: no
- Production/live/profitability/broker claim implied: no
```

Safe backup/restore evidence:

```markdown
- Repository category: local encrypted / offsite SFTP / offsite S3-compatible / other private target
- Snapshot ID prefix: <prefix only>
- Snapshot count: <number>
- Restore target: disposable / not run
- Schema version: <version only> / not checked
- Cleanup completed: yes/no/not applicable
- Secrets, repository credentials, dump contents, restored rows, DB URLs, private notes included: no
```

## Final Evidence Boundary

Private-data readiness evidence is process evidence only. It can show that checks, runbooks, backups, restores, incident rehearsal, and privacy rules were reviewed without leaking sensitive content. It does not make the app production-ready, live/realtime, broker-ready, profitability-validated, strategy-validated, real-money-ready, or approved for automatic execution.

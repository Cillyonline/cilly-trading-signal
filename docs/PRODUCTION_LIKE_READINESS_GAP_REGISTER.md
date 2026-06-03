# Production-Like Readiness Gap Register

## Purpose

This register consolidates the current production-like readiness gaps into one
reviewable evidence map. It supports future planning only.

It is not a production-readiness approval, private-data approval, security
certification, broker-readiness claim, live/realtime claim, profitability claim,
trading advice, or approval for automatic execution.

## Current Decision

Status: No Go for production-like exposure.

Private owner/operator staging remains Conditional Go only under the existing
gates and only for controlled sample, synthetic, paper, or separately sanitized
workflows.

Routine private owner/operator trading data use remains No Go under
`docs/PRIVATE_DATA_READINESS_DECISION_GATE.md`.

## Status Definitions

| Status | Meaning |
| --- | --- |
| `ready` | Sufficient documented evidence exists for the current private-staging boundary. |
| `partial` | Guidance or baseline evidence exists, but production-like evidence is incomplete. |
| `blocked` | Required evidence is missing or a current gate explicitly blocks reliance. |
| `operator-required` | Completion requires live operator action, explicit approval, secret handling, private infrastructure access, or service-impacting work. |

## Gap Register

| Area | Current status | Current evidence | Missing evidence before production-like reconsideration | Next action class |
| --- | --- | --- | --- | --- |
| Scope and owner acceptance | `blocked` | Existing gates define local review and private owner/operator staging boundaries. | Exact intended exposure, data class, user model, domain, operator responsibility model, residual-risk acceptance, and explicit disallowed use. | `operator-required` |
| Deployment smoke | `partial` | Local and private VPS smoke evidence exists for controlled owner/operator validation. | Current target-environment production-like smoke on the intended release commit, including migration status, HTTPS routing, app login path, and rollback readiness. | `operator-required` |
| API/Web verification | `ready` for repo review, `partial` for production-like | PR CI and local/docs checks are used for merged work. | Current CI on the intended release commit plus target-specific smoke evidence. | repo plus `operator-required` |
| Dependency and container security scans | `partial` | Visibility workflow and review policy exist. | Current scan output reviewed under `docs/SECURITY_SCAN_REVIEW_POLICY.md`, with critical/high treatment, reachability, mitigation, accepted-risk notes, and follow-up ownership. | repo review plus owner acceptance |
| Monitoring and alerting | `partial` | `docs/APPLICATION_MONITORING_CHECKLIST.md` defines expectations. | Target monitoring or operator-equivalent checks, alert destinations, thresholds, response windows, backup freshness alerting, certificate expiry coverage, and failed-job escalation. | repo plan plus `operator-required` |
| Backups and restore | `partial` | Local/VPS backup and disposable restore guidance exists; local encrypted Restic backup evidence exists outside repo. | Offsite/geographic encrypted backup target, backup freshness evidence, retention expectation, and restore drill from that offsite path into a disposable target. | `operator-required` |
| Rollback and data compatibility | `partial` | Deployment and incident runbooks include rollback and restore guidance. | Target-specific app rollback evidence, migration compatibility decision, restore decision point for schema-changing releases, and stop conditions accepted before rollout. | repo plan plus `operator-required` |
| Incident response | `partial` | `docs/OPERATIONAL_INCIDENT_RUNBOOK.md` covers conservative private-staging incidents. | Production-like incident ownership, communication boundaries, rehearsal or explicit owner/operator acceptance for restore, rollback, secret rotation, and private-data exposure scenarios. | repo plan plus `operator-required` |
| Secret handling and rotation | `partial` | Deployment runbook documents secret expectations and rotation cautions. | Environment-specific rotation plan and accepted procedure for app secrets, database credentials, provider keys, backup credentials, deploy credentials, and session impact. | `operator-required` |
| Privacy and evidence handling | `blocked` | Private-data evidence boundaries and gate exist. | Evidence package proving screenshots, logs, backups, restores, issue comments, and review artifacts can be handled without exposing private records. | repo plan plus `operator-required` |
| Private owner/operator trading data | `blocked` | Private-data gate explicitly says No Go. | Current privacy review, offsite restore evidence, incident rehearsal, secret-rotation acceptance, and owner/operator residual-risk acceptance. | `operator-required` |
| Product safety boundary | `ready` for current scope | Product docs preserve decision-support, manual execution, No Trade, no broker, and no automatic execution boundaries. | Production-like gate must re-confirm that no wording or workflow implies trading advice, profitability, broker readiness, live/realtime readiness, or automatic execution. | repo review |

## Repo-Only Work

The following work can be completed in repository-only issues:

- Keep this gap register current.
- Define monitoring escalation expectations and sanitized evidence boundaries.
- Define offsite backup and restore acceptance criteria without running backup or
  restore commands.
- Harden rollback and migration safety decision guidance.
- Add a security scan acceptance evidence template.
- Review whether real follow-up issues are needed after each readiness pack.

## Operator-Required Work

The following work must not be performed without explicit owner/operator approval
and the appropriate maintenance context:

- VPS deployment, restart, migration, rollback, restore, DNS, firewall, or host
  package changes.
- Secret rotation, credential inspection, provider key handling, backup password
  handling, or environment-file changes.
- Offsite backup configuration, backup upload, backup deletion, restore drill, or
  retention changes.
- Any use of private trading data, private watchlists, private journal notes,
  raw logs, screenshots with private records, or restored row contents.

## Evidence Boundaries

Allowed evidence:

- Pass/fail status, date/time, commit SHA, workflow links, issue/PR references,
  status categories, migration version, route category, snapshot ID prefix, and
  follow-up links.

Forbidden evidence:

- `.env` files, secrets, database URLs, cookies, tokens, backup credentials,
  provider keys, raw logs with sensitive content, backup dump contents, restored
  rows, private watchlists, trade notes, journal notes, account records, or
  screenshots containing private data.

## Final Statement

This register organizes evidence gaps only. Production-like exposure remains No
Go until a separate current decision gate records complete sanitized evidence and
explicit owner/operator residual-risk acceptance.

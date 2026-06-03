# Security Scan Acceptance Template

## Purpose

This template defines the sanitized evidence expected when dependency and
container scan output is reviewed for a future production-like readiness gate.

It does not change scanner configuration, suppress findings, remediate
vulnerabilities, accept current risk, certify security, approve production-like
exposure, approve private-data use, or approve automatic execution.

## Required Review Scope

Before production-like reconsideration, review the intended release commit for:

- Web dependency scan: `npm audit --audit-level=moderate`.
- API Python dependency scan: `pip-audit`.
- API image scan: Trivy high and critical OS/library findings.
- Web image scan: Trivy high and critical OS/library findings.

The review must use the latest relevant GitHub Actions run for the intended
release commit or a documented manual rerun. A green workflow is useful evidence,
but it is not a security certification or production-like approval.

## Acceptance Rules

| Finding class | Required treatment before production-like reconsideration |
| --- | --- |
| Critical | Remediate, or document owner/operator accepted risk with reachability, mitigation, expiry/review date, and follow-up. |
| High | Remediate, prove not reachable in the intended deployed context, or document owner/operator accepted risk with mitigation and follow-up. |
| Moderate | Review reachability when the finding touches runtime, auth, session, dependency install, network, persistence, database, backup/restore, Docker, Caddy/TLS, or operator-data paths. Create follow-up when reachable or unclear. |
| Low/info | Track when relevant to auth, secrets, cryptography, logging, Docker runtime, private-data handling, or operational tooling. |

Any finding affecting authentication, sessions, secrets, database access,
backup/restore, provider credentials, Caddy/TLS, Docker runtime, or private-data
exposure must be treated conservatively even if severity is lower.

## Evidence Template

```markdown
## Security Scan Acceptance Evidence

- Date/time UTC:
- Intended release commit SHA:
- Workflow run URL:
- Scanners reviewed: npm audit / pip-audit / Trivy API image / Trivy web image
- Scan run freshness accepted by owner/operator: yes/no
- Critical findings: count
- Critical treatment: remediated / not reachable / accepted risk / blocked / none
- High findings: count
- High treatment: remediated / not reachable / accepted risk / blocked / none
- Moderate findings requiring follow-up: count/link
- Findings affecting auth/session/secrets/database/backup/restore/Caddy/Docker/private-data paths: yes/no/unknown
- Reachability notes: sanitized summary only
- Mitigations recorded: yes/no/not applicable
- Accepted-risk expiry or review date: date/not applicable
- Follow-up issues:
- Owner/operator accepted residual scan risk: yes/no/not applicable
- Secrets/private data/raw logs/credentialed URLs included: no
- Production-like exposure approved by this scan review alone: no
```

## Per-Finding Review Template

```markdown
### Finding Review

- Scanner: npm audit / pip-audit / Trivy API image / Trivy web image
- Component: public package or image component name only
- Severity: critical / high / moderate / low
- Affected path category: build / runtime / auth / session / database / backup-restore / Caddy-TLS / Docker / provider / private-data / unknown
- Reachability in intended deployment: reachable / not reachable / unknown
- Current mitigation:
- Remediation available: yes/no/unknown
- Decision: remediate before gate / create follow-up / owner-accepted risk / blocked
- Follow-up issue:
- Accepted-risk expiry or review trigger:
- Sensitive evidence excluded: yes
```

## No-Go Conditions

Production-like exposure remains blocked when any of these are true:

- Scan output has not run recently on the intended release commit.
- Any critical finding is open without remediation or explicit owner/operator
  accepted risk.
- Any high finding is reachable without mitigation or accepted risk.
- Reachability is unknown for findings touching auth, sessions, secrets,
  database, backup/restore, provider credentials, Caddy/TLS, Docker runtime, or
  private-data exposure.
- Raw logs or scanner output cannot be reviewed without exposing secrets,
  credentialed URLs, private paths, provider/account data, database URLs, or
  private trading data.
- Accepted-risk notes have no expiry, review trigger, or follow-up owner.

## Forbidden Evidence

Do not include:

- `.env` values, API keys, cookies, tokens, database URLs, backup repository
  credentials, SSH keys, provider credentials, private hostnames if sensitive, or
  account identifiers.
- Raw logs containing secrets, headers, environment variables, local private
  paths, dump paths with sensitive context, restored row contents, provider
  dashboards, or private trading data.
- Statements that a green scan or accepted finding means production readiness,
  security certification, broker readiness, real-money readiness, profitability
  validation, or permission for automatic execution.

## Final Statement

Security scan acceptance is required evidence before production-like exposure can
be reconsidered, but it is not sufficient by itself. The separate production-like
gate must also record deployment smoke, monitoring, backup/restore, rollback,
incident response, privacy, secret handling, and owner/operator residual-risk
acceptance.

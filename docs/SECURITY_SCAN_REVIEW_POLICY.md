# Security Scan Review Policy

## Purpose

This policy defines how dependency and container scan findings should be interpreted before production-like exposure is reconsidered. It does not make the app production-ready, security-certified, broker-ready, live/realtime-ready, profitability-validated, strategy-validated, real-money-ready, or approved for automatic execution.

## Current Scan Coverage

The `Security Scans` GitHub Actions workflow currently provides visibility for:

- Web dependencies with `npm audit --audit-level=moderate`.
- API Python dependencies with `pip-audit`.
- API and web container images with Trivy for `HIGH` and `CRITICAL` OS/library findings, ignoring unfixed findings in the action output.

The workflow runs on pull requests, pushes to `main`, a weekly schedule, and manual dispatch. Current scan jobs are visibility checks; the production-like gate still requires reviewed and accepted scan output.

## Severity Thresholds

Before production-like exposure can be reconsidered:

| Severity | Expected treatment |
| --- | --- |
| Critical | Blocks production-like exposure unless remediated or explicitly accepted by the owner/operator with documented reachability, mitigation, and expiry/review date. |
| High | Blocks production-like exposure unless remediated, proven not reachable in the deployed context, or explicitly accepted with documented mitigation and follow-up. |
| Moderate | Requires review and follow-up issue or remediation plan when reachable in runtime, auth, network, persistence, dependency install, build, or operator-data paths. |
| Low/info | Track when relevant, especially if it affects auth, secrets, database, Docker base images, cryptography, logging, or private-data handling. |

Any finding affecting authentication, session handling, secret handling, dependency installation, database access, backup/restore tooling, provider credentials, Caddy/TLS, Docker runtime, or private-data exposure should be treated conservatively even if the reported severity is lower.

## Remediation Expectations

- Prefer upgrading the affected package, base image, or transitive dependency when the fix is compatible and scoped.
- If no fix is available, document the affected component, deployed reachability, current mitigation, and the next review trigger.
- Do not suppress or ignore findings silently. Any ignore/suppression needs a dated owner/operator acceptance note and a follow-up review date.
- Re-run the relevant scan after remediation and record only sanitized evidence.
- Do not introduce new dependencies solely to silence scan output unless the replacement materially reduces risk and matches project scope.

## Production-Like No-Go Conditions

Production-like exposure remains No Go if any of these are true:

- Any critical finding is open without documented owner/operator acceptance.
- Any high finding is reachable in the intended target environment without mitigation or accepted risk.
- Scan output has not run recently on `main` or the intended release commit.
- Scan logs cannot be reviewed without exposing secrets, private data, raw provider output, database URLs, credentials, or private paths.
- The finding affects broker/account integration, automatic execution, public SaaS exposure, auth, sessions, secret handling, database access, backup/restore, or private-data handling and the impact is unclear.

## Sanitized Evidence

Allowed evidence:

- Workflow run link, job names, commit SHA, date/time, pass/fail status, and scanner names.
- Count by severity when it does not expose secrets or private paths.
- Package or image component name and fixed version when public and non-sensitive.
- Reachability decision: `reachable`, `not reachable in current private-staging context`, `unknown`, or `accepted risk`.
- Follow-up issue link and remediation owner/status.

Forbidden evidence:

- Secrets, `.env` values, database URLs, cookies, tokens, provider keys, backup repository URLs with credentials, private hostnames if sensitive, raw private logs, or private trading data.
- Screenshots or pasted logs that include environment variables, request headers, local paths with private context, account details, provider dashboards, or restored data.
- Statements that a green scan means production readiness, security certification, broker readiness, real-money readiness, or permission for automatic execution.

## Review Template

For the production-like acceptance evidence format, use
`docs/SECURITY_SCAN_ACCEPTANCE_TEMPLATE.md`. That template expands this policy
into a concrete review record but does not change scanner behavior, suppress
findings, or approve production-like exposure by itself.

```markdown
## Security Scan Review

- Date/time UTC:
- Commit SHA:
- Workflow run:
- Scanners reviewed: npm audit / pip-audit / Trivy API image / Trivy web image
- Critical findings: count, remediation/accepted-risk status
- High findings: count, remediation/accepted-risk status
- Moderate findings requiring follow-up: count/link
- Reachability notes: sanitized summary only
- Follow-up issues:
- Owner/operator accepted residual risk: yes/no/not applicable
- Secrets/private data/raw logs included: no
- Production-like exposure approved by this review: no
```

## Final Policy Statement

Security scan review is required evidence before any future production-like gate can be reconsidered, but it is not sufficient by itself. Production-like exposure remains blocked until the separate gate also records current deployment smoke, monitoring, incident response, backup/restore, rollback, privacy handling, secret rotation, and explicit owner/operator residual-risk acceptance.

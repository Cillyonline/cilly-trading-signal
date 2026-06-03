# v3.5 Security Scan Acceptance Evidence

## Purpose

This document records sanitized security scan acceptance evidence for the v3.5
private-staging smoke scope.

It is not a security certification, production-like approval, private-data
approval, broker-readiness claim, live/realtime claim, profitability claim,
trading advice, or approval for automatic execution.

## Scope

Target decision: `docs/V3_5_TARGET_AND_OWNER_ACCEPTANCE.md`.

Intended target: existing VPS for `trading.cillyonline.de`.

Exposure: controlled private owner/operator staging only.

Data class: sample, synthetic, and paper data only.

Production-like/public exposure: No Go.

Routine private trading data: No Go.

## Security Scan Acceptance Evidence

- Date/time UTC: 2026-06-03 15:40-15:43.
- Intended release commit SHA: `d94a59a5a32e3bcfa743be1a3de606b0969a040d`.
- Workflow run URL: `https://github.com/Cillyonline/cilly-trading-signal/actions/runs/26895772908`.
- Scanners reviewed: npm audit / pip-audit / Trivy API image / Trivy web image.
- Scan run freshness accepted by owner/operator: yes for this private-staging
  smoke scope only.
- Critical findings: 0 blocking findings in completed workflow status.
- Critical treatment: none.
- High findings: 0 blocking findings in completed workflow status.
- High treatment: none.
- Moderate findings requiring follow-up: 0 from completed dependency visibility
  job status.
- Findings affecting auth/session/secrets/database/backup/restore/Caddy/Docker/private-data paths: none requiring follow-up from completed workflow status.
- Reachability notes: the workflow completed successfully for the intended
  release commit; no raw scanner logs are reproduced here.
- Mitigations recorded: not applicable.
- Accepted-risk expiry or review date: review again before any future
  production-like gate, private-data gate, dependency change, Docker base image
  change, or target exposure change.
- Follow-up issues: none from this scan review.
- Owner/operator accepted residual scan risk: yes for private-staging smoke only;
  not for production-like exposure or routine private-data reliance.
- Secrets/private data/raw logs/credentialed URLs included: no.
- Production-like exposure approved by this scan review alone: no.

## Workflow Job Evidence

Security Scans workflow, run `26895772908`, commit
`d94a59a5a32e3bcfa743be1a3de606b0969a040d`:

| Job | Result | Sanitized coverage |
| --- | --- | --- |
| Dependency visibility | Pass | Web dependencies installed; `npm audit --audit-level=moderate` step completed; API dependencies installed; `pip-audit` step completed. |
| Container visibility | Pass | API image built and scanned with Trivy for high/critical OS/library findings; web image built and scanned with Trivy for high/critical OS/library findings. |

CI workflow, run `26895772842`, same commit:

| Job | Result | Sanitized coverage |
| --- | --- | --- |
| API lint and tests | Pass | Ruff, Alembic migration smoke, and pytest completed. |
| Web build | Pass | Frontend dependency install and build completed. |

## Boundaries

This evidence does not include raw logs, package vulnerability details, private
paths, credentials, database URLs, provider details, private trading records, or
screenshots.

The Security Scans workflow is still a visibility and review mechanism. A
successful scan review is required evidence before broader reconsideration, but
it is not sufficient for production-like approval. Production-like exposure still
requires target smoke, monitoring, offsite backup/restore, rollback, incident,
privacy, secret-handling, and owner/operator acceptance evidence.

## Final Statement

For the current v3.5 private-staging smoke scope, the intended release commit has
fresh successful CI and Security Scans workflow evidence. No security-scan
follow-up issue is required from this review. Production-like exposure and
routine private trading data remain No Go.

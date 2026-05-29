# MVP Release Checklist

## Purpose

This checklist records the current MVP release-candidate posture for review and handoff. It is not a production-readiness statement, strategy validation, profitability claim, trading advice, or trading recommendation.

## Release Candidate Status

- Version / candidate: v1.2 release candidate.
- Evidence source: [2026-05-26 MVP smoke-test latest run](MVP_SMOKE_TEST.md#latest-run).
- Status: Internal RC handoff is acceptable and ready for internal review. This is not production-ready, broker-ready, profitability-validated, or real-money trading evidence.
- Decision gate: [v1.2 Release Candidate Decision Gate](V1_2_RC_DECISION_GATE.md) accepts the RC for controlled internal handoff only.
- Reason: the latest documented rerun rebuilt and started the Docker Compose proxy stack, passed direct and Caddy-routed API health checks, loaded the web app through Caddy, completed the authenticated browser workflow, confirmed protected API data was not accessible after logout, and verified PostgreSQL backup/restore mechanics on a disposable sample-data Compose project. Follow-up issue `#143` then fixed the protected-route UX after logout, issue `#144` completed a light MVP security review, and issue `#145` documented the disposable demo data reset procedure.
- Boundary: this status is not a production-readiness statement, strategy validation, profitability claim, trading advice, or trading recommendation.

## v1.2 Release Candidate Handoff Summary

### Status

- Internal RC handoff: acceptable / ready for internal review.
- Not production-ready.
- Not broker-ready.
- Not profitability-validated.
- Decision-support only, manual execution only, no broker integration, no automatic order execution, no profitability claims, no trading advice, and no production-readiness claim.

### Passed Evidence

- Staging/VPS-like deployment path evidence passed in the latest smoke-test run. See [MVP Smoke Test](MVP_SMOKE_TEST.md#latest-run).
- Caddy HTTPS path evidence passed through Caddy-routed API health and web load checks. See [Deployment Runbook](DEPLOYMENT_RUNBOOK.md#deployment-smoke-test-checklist).
- Browser MVP workflow evidence passed for login/session, dashboard, watchlist, CSV import, analysis, signals, signal detail, trades page, logout, and protected API data denial after logout. See [MVP Smoke Test](MVP_SMOKE_TEST.md#coverage-matrix).
- PostgreSQL backup/restore evidence passed on disposable sample data. See [PostgreSQL Backup/Restore Evidence](#postgresql-backuprestore-evidence) and [Deployment Runbook](DEPLOYMENT_RUNBOOK.md#postgresql-backups).
- Protected-route UX after logout was fixed in `#143`.
- Light MVP security review was completed in `#144`. See [v1.2 Light MVP Security Review](reviews/v1-2-light-security-review.md).
- Disposable demo data reset procedure was documented in `#145`. See [Deployment Runbook - Disposable Demo Data Reset](DEPLOYMENT_RUNBOOK.md#disposable-demo-data-reset).

### Known Gaps

- The direct API/web host port exposure follow-up (`#150`) has been addressed by binding direct API and web ports to localhost in the provided Compose file.
- The backup output path follow-up (`#151`) has been addressed by making backup output safer by default and documenting that PostgreSQL dumps must stay outside the repository. Broader or production-like exposure still requires separate operational readiness decisions.
- Dashboard, Journal, Performance, Alerts, and Settings remain MVP-level views, not full analytics or operations consoles.
- Risk enforcement covers core manual trade logging rules, not full portfolio exposure, correlation, or account-level risk management.
- Production monitoring and operational alerting are not documented as passed.
- Private VPS staging has a separate Conditional Go for controlled owner/operator use only. See [Private VPS Staging Decision Gate](VPS_STAGING_DECISION_GATE.md).
- v1.3 alert routing has local secret-free smoke evidence. See [v1.3 Alert Routing Smoke Test](V1_3_ALERT_ROUTING_SMOKE_TEST.md).
- v1.4-v1.6 added market-data source/freshness visibility and guarded manual provider sync. This is disabled-by-default provider support for stored Daily/EOD data, not live/realtime market data, broker readiness, automatic analysis, or production-readiness evidence.

### Not Included

- No broker integration.
- No automatic order execution.
- No real-money trading.
- No production-readiness claim.
- No profitability claim.
- No trading advice.
- No full penetration test.
- No dependency/container vulnerability scan.

### Operational Notes

- Use [MVP Smoke Test](MVP_SMOKE_TEST.md) for RC validation evidence and future reruns.
- Use [Deployment Runbook](DEPLOYMENT_RUNBOOK.md) for local/Caddy/startup procedures, health checks, backups, restore, and operational handling.
- Use the [disposable demo data reset procedure](DEPLOYMENT_RUNBOOK.md#disposable-demo-data-reset) only for local/disposable data.
- Do not delete staging, production-like, or real-data volumes unless separately approved.
- Do not commit backups, dumps, `.env`, secrets, database URLs, cookies, logs, screenshots with sensitive data, or private trading data.

### Follow-Up Recommendations

- Continue to treat broader or production-like public exposure as requiring separate security and operational readiness decisions.
- Do not treat addressed medium findings as automatic production-readiness evidence.

### Final Handoff Assessment

- Ready for internal RC handoff / review.
- Hold production-like public exposure until remaining medium security follow-ups are addressed or explicitly accepted.
- A separate decision gate has been recorded in [v1.2 Release Candidate Decision Gate](V1_2_RC_DECISION_GATE.md); any broader release, production-like exposure, broker readiness, real-money use, or profitability claim still requires a follow-up decision.

## Passed

- Release boundary remains documented as a single-user, local or controlled staging review cockpit for long-only swing-trading analysis and manual documentation.
- Safety scope remains explicit: decision-support only, manual trade execution, no broker integration in MVP, no automatic order execution, no profitability claims, and no trading advice.
- Staging/VPS-like Docker Compose proxy path passed in the latest run: stack rebuild, PostgreSQL health, API running, web running, Caddy running, direct API health, Caddy API health, and Caddy web load. See [MVP smoke-test coverage matrix](MVP_SMOKE_TEST.md#coverage-matrix).
- Frontend API base URL verification passed: bundle grep for `http://localhost:8000/api` returned no output after the `#139` fix.
- Browser workflow passed for login/session, dashboard, watchlist, CSV import, analysis, signals, signal detail, trades page, logout, and protected API data denial after logout.
- Analysis produced a conservative `No Setup` / `No Trade` result. This is valid behavior under the strategy and risk rules, not a failed workflow.
- Protected-route UX after logout was fixed in `#143`.
- Light MVP security review was completed in `#144` and found the RC posture acceptable for internal handoff, not production readiness.
- Disposable demo data reset guidance was documented in `#145`.
- Operational deployment guidance remains documented in [Deployment Runbook](DEPLOYMENT_RUNBOOK.md), including health checks, deployment smoke steps, secret handling, backup/restore guidance, and safety boundaries.
- PostgreSQL backup/restore mechanics passed on a disposable Compose project using sample-only marker data. The backup and restore scripts created a custom-format dump, restored it into a fresh disposable volume, restarted app services, returned API health, and preserved the sample rows.

## Known Gaps

- The direct API/web host port exposure follow-up (`#150`) has been addressed by binding direct API and web ports to localhost in the provided Compose file; the backup output path follow-up (`#151`) has been addressed by making backup output safer by default and documenting that PostgreSQL dumps must stay outside the repository.
- Dashboard, Journal, Performance, Alerts, and Settings are MVP-level views, not full analytics or operations consoles.
- Risk enforcement covers core manual trade logging rules, not full portfolio exposure, correlation, or account-level risk management.
- Stale signal handling flags old saved signals, but does not refresh market data or re-run strategy automatically.
- Telegram support covers explicit operator test messages and policy-gated automatic review alerts with dedup/rate limiting; the real VPS Telegram provider smoke remains an operator-run sanitized check.
- TradingView webhook support persists review events and may route policy-allowed Telegram review prompts, but does not trigger broker execution, auto-trade creation, buy/sell instructions, or trading advice.
- Provider sync support is manual, guarded, and disabled by default. Current provider support starts with Daily/EOD data and does not cover promised `4H`/intraday sync, scheduler-driven imports, or automatic analysis refresh.
- Production monitoring and operational alerting are not documented as passed.
- Full mobile app/PWA hardening beyond responsive MVP layouts is not documented as passed.

## Blocked

- No active release-candidate blocker is documented for `#132` or `#139` in the latest smoke-test rerun.
- Production monitoring and operational alerting remain not completed for broader exposure, so production readiness is not claimed.

## Not Included

- Automatic order execution.
- Broker or exchange integration.
- Buy/sell recommendations, blind trading instructions, or trading advice.
- Profitability, win-rate, backtesting, benchmark, strategy-validation, or real-money readiness claims.
- Live market data, live account sync, or portfolio execution automation.
- Public SaaS operation, multi-tenant isolation, billing, or user onboarding.
- Options, leverage, margin, short-selling strategies, or automated position sizing.

## Release Review Gate Status

| Gate | Status | Evidence |
| --- | --- | --- |
| Release boundary and safety wording documented | Passed | This checklist, [MVP Smoke Test](MVP_SMOKE_TEST.md#safety-scope), and [Deployment Runbook](DEPLOYMENT_RUNBOOK.md#safety-boundaries) keep decision-support and no-execution boundaries explicit. |
| Docker Compose proxy stack startup | Passed | Latest smoke run recorded successful proxy stack rebuild with Postgres healthy and API, web, and Caddy running. |
| API health | Passed | Direct API health and Caddy-routed API health passed. |
| Web through Caddy | Passed | `curl.exe -k -I https://localhost` returned `HTTP/1.1 200 OK` through Caddy. |
| Frontend API base URL | Passed | Bundle grep for `http://localhost:8000/api` returned no output after `#139`. |
| Browser MVP workflow | Passed | Dashboard, login/session, watchlist, CSV import, analysis, signals, signal detail, trades page, and logout were reviewed in the latest smoke run. |
| Conservative signal behavior | Passed | Sample analysis produced `No Setup` / `No Trade` because of strategy/risk rules; this preserves No Trade as a first-class outcome. |
| Logout protected-data behavior | Passed | Protected API data was not accessible after logout in the smoke rerun; protected-route UX after logout was fixed in `#143`. |
| PostgreSQL backup/restore evidence | Passed | `#135` verified `scripts/backup_postgres.sh` and `scripts/restore_postgres.sh` against disposable sample data; API health and restored sample-row query passed after restore. |
| Release blocker tracking | Passed | `#132` and `#139` are no longer documented as active smoke-test blockers; `#143`, `#144`, and `#145` are completed for internal RC handoff context. |
| Production readiness | Not passed | No production-readiness gate is documented as passed; deployment docs remain operational guidance only. |

## PostgreSQL Backup/Restore Evidence

### VPS-Like Disposable Verification

Date: 2026-05-28

Status: Passed.

Evidence summary:

- GitHub issue: `#162`.
- Environment: existing VPS host, isolated disposable Docker Compose project `cilly_br_verify`.
- Existing projects: the unrelated `staging` Compose project remained separate and running.
- Data scope: disposable marker table only; no production data, personal trading data, real journal data, secrets, or committed dump contents.
- Repository checkout: `/root/repos/cilly-trading-signal`.
- Backup path: `/srv/backups/cilly-trading-signal/postgres`, outside the repository checkout.
- Backup: `scripts/backup_postgres.sh` created a PostgreSQL custom-format dump at the external backup path when run with explicit `COMPOSE_PROJECT_NAME`, `COMPOSE_FILE`, `BACKUP_DIR`, `POSTGRES_USER`, and `POSTGRES_DB` values.
- Restore: `scripts/restore_postgres.sh` restored the dump into the same disposable Compose project after the marker table was dropped.
- Verification:
  - Disposable API health returned `{"status":"ok","service":"Cilly Trading Signal API","version":"0.1.0","environment":"development"}` after restore.
  - Restored marker row was queryable: `SAMPLE-BR-162 / issue-162 disposable marker`.
  - `git status --short` in the VPS checkout returned no changes.
  - A repository search for `*.dump`, `*.sql`, `*.backup`, and `*.bak` returned no files.

Notes:

- The helper scripts were invoked through `bash` because the VPS checkout did not have executable bits set on the shell scripts.
- A first backup command without explicit environment variables failed safely because it targeted the default Compose project and reported that `postgres` was not running.
- The app database schema migrations were not required for this mechanics check; the verification used a disposable marker table created directly in PostgreSQL.
- The restore operation was intentionally limited to the disposable `cilly_br_verify` project. No restore was run against the existing `staging` project or any real data.
- No backup dump files, `.env` files, secrets, database URLs, credentials, or private data were committed.
- This evidence does not claim production readiness.

### Prior Disposable Verification

Date: 2026-05-26

Status: Passed.

Evidence summary:

- GitHub issue: `#135`.
- Environment: disposable Docker Compose project `cilly_backup_restore_test`.
- Data scope: sample-only marker rows; no production data, personal trading data, or secrets.
- Backup: `scripts/backup_postgres.sh` created a PostgreSQL custom-format dump in a temporary directory outside the repository.
- Restore: `scripts/restore_postgres.sh` restored the dump into a fresh disposable PostgreSQL volume.
- Verification:
  - API health returned `{"status":"ok"}` after restore.
  - Restored sample marker rows were queryable:
    - `manual_trade / SAMPLE-BR-001`
    - `watchlist / SAMPLE-BR-001`
- Cleanup: disposable containers, network, volume, temporary Compose override, and temporary backup dump were removed.

Notes:

- The Windows checkout had CRLF working-tree line endings for `.sh` files. The scripts were executed from normalized temporary copies inside an ephemeral Docker CLI helper container to match Linux/VPS execution semantics.
- Repository scripts were not modified.
- No backup dump files, `.env` files, secrets, database URLs, credentials, or private data were committed.
- This evidence does not claim production readiness.

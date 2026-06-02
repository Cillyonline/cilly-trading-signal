# MVP Release Checklist

## Purpose

This checklist records the current MVP release-candidate posture for review and handoff. It is not a production-readiness statement, strategy validation, profitability claim, trading advice, or trading recommendation.

## Current Rebaseline Status

- Version / candidate: final internal owner/operator review candidate during v2.9 current-state rebaseline.
- Evidence source: automated API/Web/Security Scan verification from merged v2.2-v2.9-prep PRs plus the v2.8 final internal workflow smoke recorded in [MVP Smoke Test](MVP_SMOKE_TEST.md#v28-final-internal-workflow-smoke). Current-main sample-only validation evidence is tracked as v2.9 follow-up work.
- Status: Conditional Go for controlled internal single-owner/operator review workflows with sample, synthetic, or paper data. This is not production-ready, broker-ready, profitability-validated, live/realtime, or real-money trading evidence.
- Current decision gate: [Final Internal Review Decision Gate](FINAL_INTERNAL_REVIEW_DECISION_GATE.md) records Conditional Go for controlled internal review only. [Deployment Readiness Decision Gate v2](DEPLOYMENT_READINESS_DECISION_GATE_V2.md) still governs local/private staging boundaries; [Private Data Readiness Decision Gate](PRIVATE_DATA_READINESS_DECISION_GATE.md) blocks routine private trading data use; production-like exposure remains No Go.
- Boundary: decision-support only, manual execution only, no broker integration, no automatic order execution, no profitability claims, no live/realtime claims, no trading advice, and no production-readiness claim.

## Final Internal Review Candidate Summary

### Implemented Since v2.1

- v2.2-v2.4 improved historical/paper review evidence workflows with correction support, correction audit history, auditable calibration finding categories, and repeated finding visibility.
- v2.5 added open portfolio risk review, max open risk warnings, asset concentration warnings, simple correlation proxy warnings, and process-oriented trade journal analytics.
- v2.6 added application monitoring checklist, structured health details, backup restore drill documentation, deployment readiness decision gate v2, dependency/container scan workflow, and operational incident runbook.
- v2.7 added mobile layout audit, improved mobile signal cards, improved mobile review batch entry/correction grouping, mobile Screener density improvements, mobile trade workflow grouping, responsive core-page header density reductions, and a basic PWA manifest/icons baseline.
- v2.8 rebaselined product docs, recorded final internal workflow smoke evidence, added smoke-runner migration handling, repeatable browser clickthrough guidance, and the final internal owner/operator review decision gate.
- v2.9-prep expanded the first paper calibration batch to 80 examples, added deterministic resistance/missing-context/trigger-confirmation coverage, improved review evidence templates and UI wording, documented a safe dry-run browser smoke contract, and added a non-invasive smoke evidence formatter.

### Current Known Gaps

- Final current-main internal workflow smoke evidence has passed for the local Docker Compose stack, current migrations, web HTTP load, and API-assisted sample-only workflow coverage; repeatable browser clickthrough guidance exists but remains operator-run rather than automated evidence.
- v2.9 current-main sample-only validation evidence is the next planned evidence update; until recorded, v2.8 smoke remains the latest full workflow evidence.
- Final internal go/no-go decision gate is recorded as Conditional Go for controlled internal owner/operator review only.
- Deployment readiness evidence, monitoring runbook links, review correction audit history, auditable finding categories, active-status portfolio risk treatment, and mobile Screener/trade/header follow-ups have been addressed for controlled internal review.
- Persistent local/private-staging volumes must still verify current migrations before workflow testing; the local smoke runner applies migrations and fails clearly on migration errors.
- Production-grade monitoring, offsite encrypted backup operations, recurring restore evidence, rollback evidence, stricter security-scan policy, private-data handling, and explicit production-like owner acceptance remain incomplete for broader exposure.

### Final Internal Review Boundary

- Internal owner/operator review only.
- Manual execution only.
- No broker integration, account sync, automatic order execution, automatic trade creation, or automatic position sizing.
- No production-like public exposure, public SaaS, multi-user onboarding, billing, support operation, real-money readiness, profitability claim, backtesting validation, live/realtime claim, or trading advice.

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
- v1.8 improved cockpit review usability across Dashboard, Signals, Alerts, Trades, and documentation while preserving manual review boundaries.
- v1.9 added TradingView screener CSV snapshots, validation, candidate review UI, and explicit Watchlist conversion. Screener results remain review candidates only and do not create analysis, signals, trades, alerts, orders, or broker actions automatically.
- v2.1 and follow-ups added professional strategy calibration, asset-specific overlays, benchmark-context visibility, analysis quality reports, calibration golden cases, end-to-end stored OHLCV/benchmark fixtures, and historical/paper review batches while preserving manual-review-only boundaries.
- v2.2-v2.7 added review evidence refinement, risk/portfolio review, operational readiness documentation and scans, mobile signal/review usability improvements, and a PWA manifest baseline while preserving manual-review-only boundaries.

### Not Included

- No broker integration.
- No automatic order execution.
- No real-money trading.
- No production-readiness claim.
- No profitability claim.
- No trading advice.
- No full penetration test.
- Dependency/container scanning is visibility-only unless a separate policy makes findings blocking.

### Operational Notes

- Use [MVP Smoke Test](MVP_SMOKE_TEST.md) for RC validation evidence and future reruns.
- Use [Deployment Runbook](DEPLOYMENT_RUNBOOK.md) for local/Caddy/startup procedures, health checks, backups, restore, the repeatable [Backup Restore Drill](DEPLOYMENT_RUNBOOK.md#backup-restore-drill), and operational handling.
- Use [Deployment Readiness Decision Gate v2](DEPLOYMENT_READINESS_DECISION_GATE_V2.md) before treating local, private staging, or production-like exposure as acceptable.
- Use [Application Monitoring Checklist](APPLICATION_MONITORING_CHECKLIST.md) for local, private staging, and production-like monitoring expectations before broader reliance.
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
- TradingView screener CSV workflow is implemented for stored snapshots, validation results, candidate review, explicit Watchlist conversion, and safe duplicate linking.
- Review cockpit usability has been improved for dashboard priorities, signal filters, alert review, and trade review completeness indicators.
- Strategy signal quality has been calibrated with improved setup gates, risk-plan checks, market regime/relative strength context, no-trade explanations, and quality reports.
- Stored benchmark-context requirements for stocks and crypto are visible in Watchlist.
- Focused calibration golden cases, end-to-end stored OHLCV/benchmark fixtures, and app-supported historical/paper review batches are available for future rule changes and process-evidence review.

## Known Gaps

- The direct API/web host port exposure follow-up (`#150`) has been addressed by binding direct API and web ports to localhost in the provided Compose file; the backup output path follow-up (`#151`) has been addressed by making backup output safer by default and documenting that PostgreSQL dumps must stay outside the repository.
- Dashboard, Journal, Performance, Alerts, and Settings are MVP-level views, not full analytics or operations consoles.
- Risk enforcement covers core manual trade logging rules, not full portfolio exposure, correlation, or account-level risk management.
- Stale signal handling flags old saved signals, but does not refresh market data or re-run strategy automatically.
- Telegram support covers explicit operator test messages and policy-gated automatic review alerts with dedup/rate limiting; the real VPS Telegram provider smoke remains an operator-run sanitized check.
- TradingView webhook support persists review events and may route policy-allowed Telegram review prompts, but does not trigger broker execution, auto-trade creation, buy/sell instructions, or trading advice.
- Provider sync support is manual, guarded, and disabled by default. Current provider support starts with Daily/EOD data and does not cover promised `4H`/intraday sync, scheduler-driven imports, or automatic analysis refresh.
- Screener CSV support does not yet include advanced filtering, bulk review actions, pagination beyond current row limits, candidate scoring, or automatic market-data refresh after Watchlist conversion.
- Historical/paper review batches are MVP-level and do not yet include advanced filtering, CSV export, or automated follow-up issue creation.
- Production monitoring and operational alerting are not documented as passed; the application monitoring checklist is documentation for operator review, not completed production monitoring evidence.
- Dependency/container scan workflow exists for visibility, but passing or non-blocking scan output is not production-readiness, security certification, or real-money-readiness evidence.
- Mobile signal cards, review batch entry, Screener density, trade workflow grouping, responsive header density, and PWA manifest baseline are implemented; native app behavior, push notifications, offline trading mode, and background sync are not documented as passed.

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

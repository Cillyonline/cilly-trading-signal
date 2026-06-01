# Owner/Operator Wiki

## Purpose

This wiki is the starting point for operating the cockpit as a controlled single owner/operator review tool. It organizes the existing documentation by task instead of by file name.

This wiki is not a production-readiness statement, strategy-validation claim, profitability claim, broker-readiness claim, trading advice, live/realtime market-data claim, or approval for automatic execution.

## Operating Boundaries

- Use the app as decision-support and process documentation only.
- Execute, manage, and close trades manually outside the app.
- Treat `No Trade`, stale data, missing benchmark context, failed or partial syncs, rejected screener rows, and unclear review outcomes as valid conservative stop points.
- Do not enter secrets, cookies, account data, broker data, private journal details, or screenshots with sensitive data into issues, PRs, docs, or shared evidence.
- Do not infer profitability, win rate, strategy validation, live/realtime readiness, or real-money readiness from any dashboard, signal, alert, review, trade, or performance view.

## Start Here

| Task | Primary Doc | Use When |
| --- | --- | --- |
| Understand current release posture | [MVP Release Checklist](MVP_RELEASE_CHECKLIST.md) | You need the current Conditional Go / No Go boundaries. |
| Understand final internal gate | [Final Internal Review Decision Gate](FINAL_INTERNAL_REVIEW_DECISION_GATE.md) | You need the current allowed and disallowed use cases. |
| Check private-data readiness | [Private Data Readiness Decision Gate](PRIVATE_DATA_READINESS_DECISION_GATE.md) | You need the current No Go boundary for routine private trading data use. |
| Run local smoke checks | [MVP Smoke Test](MVP_SMOKE_TEST.md) | You need local Docker/API/Web/migration smoke evidence. |
| Run browser workflow checks | [Final Browser Clickthrough Checklist](FINAL_BROWSER_CLICKTHROUGH_CHECKLIST.md) | You need repeatable sample-only browser evidence. |
| Operate the cockpit workflow | [Cockpit Review Workflow](COCKPIT_REVIEW_WORKFLOW.md) | You need the manual review flow and safety boundaries. |
| Prepare VPS staging | [VPS Staging Plan](VPS_STAGING_PLAN.md) | You are preparing controlled private staging with the operator. |

## Cockpit Workflow Docs

| Area | Doc | Notes |
| --- | --- | --- |
| Dashboard and review priorities | [Dashboard User Guide](DASHBOARD_USER_GUIDE.md) | Explains dashboard cards, priority panels, stop points, and non-claims. |
| End-to-end operator usage | [Owner/Operator Cockpit Manual](OWNER_OPERATOR_COCKPIT_MANUAL.md) | Practical browser workflow companion before VPS validation. |
| Watchlist, signals, alerts, trades | [Cockpit Review Workflow](COCKPIT_REVIEW_WORKFLOW.md) | Product workflow, safety framing, and review sequence. |
| Trading strategy boundaries | [Strategy And Alerts](STRATEGY_AND_ALERTS.md) | Strategy, alert, No-Trade, and manual-execution rules. |
| Professional playbook | [Professional Strategy Playbook](PROFESSIONAL_STRATEGY_PLAYBOOK.md) | Human review playbook for long-only swing setups. |
| Asset-specific filters | [Asset Specific Signal Filters](ASSET_SPECIFIC_SIGNAL_FILTERS.md) | Stock/crypto context differences and conservative filters. |

## Data And Calibration Docs

| Area | Doc | Notes |
| --- | --- | --- |
| Data model | [Data Model](DATA_MODEL.md) | Current persistence direction and entity relationships. |
| Market data freshness | [Market Data Freshness Model](MARKET_DATA_FRESHNESS_MODEL.md) | Fresh/stale/unknown/failed/partial semantics. |
| Provider sync | [Market Data Provider Decision](MARKET_DATA_PROVIDER_DECISION.md) | Provider support boundaries and disabled-by-default posture. |
| Provider sync smoke | [Provider Sync Smoke Test](PROVIDER_SYNC_SMOKE_TEST.md) | Sample-only sync evidence and provider privacy boundary. |
| Screener CSV | [Screener CSV Model](SCREENER_CSV_MODEL.md) | TradingView screener CSV as review candidates only. |
| Calibration workflow | [Strategy Calibration Workflow](STRATEGY_CALIBRATION_WORKFLOW.md) | How rule changes must be reviewed with evidence. |
| Historical/paper review | [Historical Paper Review Protocol](HISTORICAL_PAPER_REVIEW_PROTOCOL.md) | Review batches, labels, finding categories, and follow-up evidence. |
| First paper calibration batch | [First 80-Example Paper Calibration Batch](reviews/first-50-paper-calibration-batch.md) | First structured 80-example paper review with follow-up status snapshot for calibration issues. |
| Trade/journal privacy | [Trade Journal Privacy Review](TRADE_JOURNAL_PRIVACY_REVIEW.md) | Sensitive trade, journal, and performance fields and evidence boundaries. |

## Local/Internal Review Evidence

| Evidence Area | Doc | Notes |
| --- | --- | --- |
| Local Docker smoke | [MVP Smoke Test](MVP_SMOKE_TEST.md) | Smoke runner, migrations, API health, web load, and sample workflows. |
| Browser clickthrough | [Final Browser Clickthrough Checklist](FINAL_BROWSER_CLICKTHROUGH_CHECKLIST.md) | Manual browser evidence template for desktop/mobile. |
| Browser smoke automation | [Post-Deploy Browser Smoke Automation Evaluation](POST_DEPLOY_BROWSER_SMOKE_AUTOMATION_EVALUATION.md) | Current decision to keep post-deploy browser smoke manual for now. |
| Release checklist | [MVP Release Checklist](MVP_RELEASE_CHECKLIST.md) | Current implemented/gap/boundary summary. |
| Deployment readiness gate | [Deployment Readiness Decision Gate v2](DEPLOYMENT_READINESS_DECISION_GATE_V2.md) | Local/private staging boundaries; production-like remains No Go. |
| Production-like requirements | [Production-Like Requirements Review](PRODUCTION_LIKE_REQUIREMENTS_REVIEW.md) | Requirements and blockers for any future production-like reconsideration. |
| Private-data readiness gate | [Private Data Readiness Decision Gate](PRIVATE_DATA_READINESS_DECISION_GATE.md) | Routine private trading data remains blocked until separate evidence and owner acceptance. |
| Private-data evidence | [Private Data Evidence Handling](PRIVATE_DATA_EVIDENCE_HANDLING.md) | Allowed, redacted, and forbidden evidence for issues, PRs, logs, screenshots, terminal output, and chat. |

## Operations And VPS Docs

| Area | Doc | Use When |
| --- | --- | --- |
| General deployment operations | [Deployment Runbook](DEPLOYMENT_RUNBOOK.md) | You need deployment, Caddy, backup, restore, rollback, or smoke commands. |
| Offsite backup target | [Offsite Backup Target Evaluation](OFFSITE_BACKUP_TARGET_EVALUATION.md) | You need options, tradeoffs, and local-only backup residual risk. |
| Monitoring checklist | [Application Monitoring Checklist](APPLICATION_MONITORING_CHECKLIST.md) | You need local/private-staging/production-like monitoring expectations. |
| Incident response | [Operational Incident Runbook](OPERATIONAL_INCIDENT_RUNBOOK.md) | You need health, auth, data, alert, or deployment incident handling. |
| Security scan review | [Security Scan Review Policy](SECURITY_SCAN_REVIEW_POLICY.md) | You need dependency/container scan thresholds before any production-like reconsideration. |
| VPS plan | [VPS Staging Plan](VPS_STAGING_PLAN.md) | You are preparing the controlled private VPS staging path. |
| VPS environment | [VPS Environment Checklist](VPS_ENVIRONMENT_CHECKLIST.md) | You need host, Docker, DNS, firewall, and secret preflight checks. |
| VPS user runbook | [VPS Deploy User Runbook](VPS_DEPLOY_USER_RUNBOOK.md) | You need safe deploy-user setup guidance. |
| VPS firewall | [VPS Firewall Hardening Plan](VPS_FIREWALL_HARDENING_PLAN.md) | You need firewall exposure guidance. |
| VPS smoke evidence | [VPS Staging Smoke Test](VPS_STAGING_SMOKE_TEST.md) | You are recording controlled private staging smoke evidence. |
| VPS decision gate | [VPS Staging Decision Gate](VPS_STAGING_DECISION_GATE.md) | You are deciding whether private staging remains acceptable. |

## Product And Engineering Reference

| Area | Doc |
| --- | --- |
| Product scope | [MVP Spec](MVP_SPEC.md) |
| Product roadmap | [Product Roadmap](PRODUCT_ROADMAP.md) |
| Delivery roadmap | [Delivery Roadmap](DELIVERY_ROADMAP.md) |
| Architecture | [Tech Architecture](TECH_ARCHITECTURE.md) |
| Decisions | [Decisions](DECISIONS.md) |
| Engineering workflow | [Engineering Workflow](ENGINEERING_WORKFLOW.md) |

## VPS Validation Sequence

Use this sequence only after the operator docs are complete and reviewed:

1. Confirm preflight with [VPS Environment Checklist](VPS_ENVIRONMENT_CHECKLIST.md).
2. Confirm secrets are managed outside git and shared evidence.
3. Deploy current `main` only after explicit operator approval.
4. Apply and verify migrations before browser workflow testing.
5. Run health checks and web load checks.
6. Run [Final Browser Clickthrough Checklist](FINAL_BROWSER_CLICKTHROUGH_CHECKLIST.md) with sample/synthetic/paper data only.
7. Record sanitized smoke evidence in [VPS Staging Smoke Test](VPS_STAGING_SMOKE_TEST.md).
8. Refresh [VPS Staging Decision Gate](VPS_STAGING_DECISION_GATE.md) only after reviewing residual risks.

## Stop Conditions

Stop the workflow and create a sanitized follow-up issue if any of these occur:

- A workflow exposes secrets, cookies, tokens, private trading data, account data, database URLs, or raw sensitive logs.
- A page implies buy/sell instruction, trading advice, profitability, strategy validation, live/realtime market data, broker readiness, or automatic execution.
- A migration, health check, login, logout, protected-route, backup, restore, or browser workflow check fails without a clear accepted-risk note.
- A sample workflow creates an analysis, signal, trade, alert, broker action, or order automatically where explicit manual action is required.

# MVP Smoke Test

## Purpose

This document records the MVP smoke-test workflow and the latest validation result for the manual trading cockpit. The smoke test uses local/sample data only and does not make a production-readiness, profitability, or execution claim.

## Safety Scope

- Signals are review prompts, not buy/sell instructions.
- The app must not create broker orders or connect to a broker.
- Trades in this smoke test are manual documentation records only.
- Performance views show documented historical/paper results, not forecasts.

## Runner

The `scripts/smoke_test.ps1` runner automates preflight, stack startup, and
the API health check. It does not replace the browser portion of the smoke
test — it only reduces manual setup ambiguity.

```powershell
# Bring the stack up and wait for /api/health
.\scripts\smoke_test.ps1

# Bring the stack down (volumes preserved)
.\scripts\smoke_test.ps1 -Cleanup

# Bring the stack down and wipe the Postgres volume
.\scripts\smoke_test.ps1 -Cleanup -PurgeVolumes
```

The runner fails fast with a clear `[FAIL]` message when the Docker engine
pipe is unreachable. Browser steps (login, watchlist, CSV import, analysis,
trade log, journal, performance) continue manually using the fixtures under
`test-data/csv/`.

This script is release-validation tooling, not a production deployment claim.

## Target Workflow

1. Start the local stack with Docker Compose.
2. Verify API health.
3. Open the web app and log in with the local admin credentials.
4. Create or verify a watchlist item for sample/paper data.
5. Import TradingView-compatible CSV data for `1W`, `1D`, and `4H`.
6. Run analysis and review generated signal cards.
7. Review signal detail, stale wording, manual status actions, review notes, and review history.
8. Create a manual trade log from paper/sample values only.
9. Add trade events, close the trade, and add a journal review.
10. Verify dashboard, performance, settings, alerts, and safety wording remain decision-support only.

## Latest Run

Date: 2026-05-17

Environment:

- Windows workspace: `C:\repos\cilly-trading-signal`
- Docker CLI: available
- Docker Compose CLI: available
- Docker Desktop Linux engine: not running or not reachable
- Sample CSV fixtures: available under `test-data/csv/` (see "Sample Data" section)

Commands attempted:

```powershell
docker --version
docker compose version
Copy-Item .env.example .env
docker compose -f infra/docker-compose.yml up --build -d
Invoke-RestMethod http://localhost:8000/api/health
```

Results:

- `docker --version`: PASS
- `docker compose version`: PASS
- `.env` creation from `.env.example`: PASS, then removed after the blocked run
- Docker Compose stack startup: BLOCKED
- API health check: NOT RUN because stack startup was blocked
- Full browser workflow: NOT RUN because stack startup and sample CSV fixtures were unavailable

Observed blocker:

```text
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

Interpretation: Docker Desktop is installed, but the Linux engine was not reachable from this shell session. The full local smoke test cannot be claimed as passed from this run.

## Coverage Matrix

| Area | Result | Notes |
| --- | --- | --- |
| Docker CLI availability | PASS | CLI returned a version. |
| Docker Compose CLI availability | PASS | Compose returned a version. |
| Compose stack startup | BLOCKED | Docker Desktop Linux engine pipe unavailable. |
| API health | NOT RUN | Requires running stack. |
| Web login | NOT RUN | Requires running stack. |
| Watchlist workflow | NOT RUN | Requires running stack. |
| CSV import and analysis | NOT RUN | Requires running stack and sample CSV fixtures. |
| Signal review workflow | NOT RUN | Requires generated/persisted signals. |
| Manual trade logging | NOT RUN | Requires running stack and sample signal/trade data. |
| Journal and performance | NOT RUN | Requires manual trade records. |
| Settings and Telegram test UI | NOT RUN | Requires running stack and configured/mocked Telegram values. |
| Safety wording review | PARTIAL | Static documentation and UI wording have been reviewed incrementally in prior PRs; full browser review is still needed. |

## Sample Data

Deterministic paper/sample CSV fixtures live under `test-data/csv/` and are
the canonical input for the import + analysis portion of this smoke flow.
They are synthetic OHLCV curves — not market data — and exist only to make
this workflow reproducible without exposing personal trading data.

| File | Timeframe | Candles |
| --- | --- | --- |
| `test-data/csv/sample_paper_1w.csv` | 1W | 60 |
| `test-data/csv/sample_paper_1d.csv` | 1D | 250 |
| `test-data/csv/sample_paper_4h.csv` | 4H | 250 |

Suggested smoke workflow with these fixtures:

1. In the web app, add a watchlist item with a clearly fake symbol (for
   example `SMOKE-PAPER-001`, asset class `stock`, exchange `SAMPLE`).
2. Upload each CSV from the Import page, selecting the matching timeframe.
3. From the import history, run analysis to generate signals.
4. Continue through the manual trade/journal/performance steps using only
   sample values.

Regenerate the fixtures with `python scripts/generate_smoke_fixtures.py`
if they are ever removed; output is deterministic.

See `test-data/csv/README.md` for the full safety scope of these fixtures.

## Follow-Up Issues

- `#117` Add deterministic MVP smoke test fixture data.
- `#118` Add repeatable MVP smoke test runner.

## Next Smoke-Test Requirements

Before marking the MVP smoke flow as passed, rerun this document with:

- Docker Desktop Linux engine running and reachable.
- Deterministic sample/paper CSV files for `1W`, `1D`, and `4H` (committed under `test-data/csv/`).
- A browser pass through the complete manual workflow.
- Follow-up issues opened for any material product defects discovered.

## Cleanup Notes

The temporary local `.env` created during this run was removed and must not be committed. If future smoke runs create local data, logs, screenshots, or exports, review them for secrets or personal trading data before sharing.

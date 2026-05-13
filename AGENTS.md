# AGENTS.md

Guidance for OpenCode and other coding agents working in this repository.

## Project Context

This repo contains a web-based trading signal platform for stocks and crypto. The product is a professional long-only swing-trading cockpit for setup analysis, explainable signals, alerts, manual trade logging, trade management, and performance analysis in R-multiples.

Core product principles:

- Context first, setup second, trigger third, risk always.
- No automatic order execution.
- No broker integration in the MVP.
- Signals are decision support, not blind buy/sell instructions.
- Trading execution stays manual.
- Strategy, scores, and alerts must be explainable.

## Repository Structure

- `apps/web/`: Next.js App Router frontend with React, TypeScript, and Tailwind CSS.
- `apps/api/`: FastAPI backend using Python 3.12, SQLAlchemy, Alembic, and Pydantic.
- `docs/`: Product, strategy, architecture, data model, and workflow documentation.
- `infra/`: Docker Compose, Caddy, and deployment-related files.
- `scripts/`: Operational helper scripts.

## Important Documentation

Read the relevant docs before changing product behavior, architecture, or trading logic:

- `README.md`: local setup, commands, current status.
- `docs/ENGINEERING_WORKFLOW.md`: issue, branch, PR, and review expectations.
- `docs/TECH_ARCHITECTURE.md`: architecture decisions and system boundaries.
- `docs/DATA_MODEL.md`: data model direction.
- `docs/STRATEGY_AND_ALERTS.md`: trading strategy and alert rules.
- `docs/MVP_SPEC.md`: MVP scope.
- `docs/DECISIONS.md`: recorded decisions.

## Working Rules

- Keep changes small, scoped, and reviewable.
- Prefer existing patterns over new abstractions.
- Do not introduce new dependencies without a concrete need.
- Do not manually edit generated output such as `.next/`, build artifacts, caches, or lockfile-derived output unless the task explicitly requires it.
- Do not modify secrets or local environment files. `.env` and `.env.*` are ignored; `.env.example` may be updated when configuration changes.
- Do not add automatic trading, broker execution, or profitability claims.
- For trading-related behavior, prefer conservative, explainable decisions and preserve `No Trade` as a first-class outcome.
- If a task is based on a GitHub issue, respect its allowed and disallowed file boundaries.

## Commands

Run commands from the indicated directories.

Frontend setup and development:

```powershell
cd apps/web
npm install
npm run dev
```

Frontend verification:

```powershell
cd apps/web
npm run build
```

Backend development:

```powershell
cd apps/api
uv run --with "fastapi[standard]" --with pydantic-settings --with sqlalchemy --with "psycopg[binary]" fastapi dev app/main.py
```

Backend verification:

```powershell
cd apps/api
uv run --no-project --with ruff ruff check --select E,F,UP,B .
uv run --no-project --with pytest --with "fastapi[standard]" --with pydantic-settings --with sqlalchemy --with "psycopg[binary]" pytest
```

Full local smoke test with Docker Compose:

```powershell
Copy-Item .env.example .env
docker compose -f infra/docker-compose.yml up --build
Invoke-RestMethod http://localhost:8000/api/health
docker compose -f infra/docker-compose.yml down
```

## Verification Expectations

- For frontend changes, run `npm run build` in `apps/web` when feasible.
- For backend changes, run Ruff and pytest in `apps/api` when feasible.
- For infra or integration changes, prefer the Docker Compose smoke test when feasible.
- If a check cannot be run, state the reason and the residual risk clearly.
- For UI changes, consider desktop and mobile behavior.

## Code Style

- Python targets 3.12. Ruff uses line length 100 and lint rules `E,F,UP,B`.
- TypeScript/React should follow the existing Next.js 14 App Router patterns.
- Tailwind CSS is the frontend styling system.
- Keep comments rare and useful; explain non-obvious decisions, not obvious assignments.

## Git And PR Guidance

- Use one branch per issue, named like `issue-<number>-short-description`.
- PRs should include linked issue, summary, verification commands/results, known risks or follow-ups, and screenshots for UI changes when useful.
- Do not commit or push unless explicitly requested.
- Never include secrets, credentials, or local `.env` files in commits.

## Definition Of Done

- The change matches the requested scope.
- Relevant docs are updated when behavior, setup, architecture, or strategy changes.
- Relevant checks pass, or skipped checks are explained.
- No unrelated files are changed intentionally.
- Trading logic remains explainable, conservative, and aligned with `docs/STRATEGY_AND_ALERTS.md`.

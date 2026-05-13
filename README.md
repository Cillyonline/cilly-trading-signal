# Trading Signal Tool

Webbasierte Trading- und Signal-Plattform fuer Aktien und Krypto.

Ziel ist ein professionelles Trading-Cockpit fuer Long-only Swingtrading: Setups analysieren, Trigger vorbereiten, Alerts empfangen, manuelle Trades loggen, Trades managen und Performance in R-Multiples auswerten.

## Grundprinzipien

- Context first, Setup second, Trigger third, Risk always.
- Keine automatische Orderausfuehrung.
- Keine Broker-Anbindung im MVP.
- Signale sind Entscheidungsunterstuetzung, keine blinden Buy-/Sell-Anweisungen.
- Trading-Ausfuehrung bleibt manuell, z.B. ueber Trade Republic.
- Strategie, Score und Alerts muessen erklaerbar sein.

## Geplanter Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: Python, FastAPI, SQLAlchemy, Alembic, Pydantic
- Database: PostgreSQL
- Deployment: Docker Compose auf VPS
- Reverse Proxy: Caddy
- Auth: HttpOnly Cookie Auth
- Notifications: Telegram Bot

## Struktur

```text
docs/   Produkt-, Strategie- und Architekturplanung
apps/   spaetere Web- und API-Anwendungen
infra/  Deployment- und Infrastrukturdateien
scripts/ Hilfsskripte fuer Betrieb und Backups
```

## Lokaler Start

Voraussetzungen:

- Docker Desktop
- Node.js 20 fuer lokale Web-Entwicklung ohne Docker
- Python 3.12 und uv fuer lokale API-Entwicklung ohne Docker

Mit Docker Compose:

```powershell
Copy-Item .env.example .env
docker compose -f infra/docker-compose.yml up --build
```

Danach:

- Web: `http://localhost:3000`
- API Health: `http://localhost:8000/api/health`

Mit Caddy-Profil:

```powershell
docker compose -f infra/docker-compose.yml --profile proxy up --build
```

## Qualitaetschecks

Frontend:

```powershell
cd apps/web
npm run build
```

Backend:

```powershell
cd apps/api
uv run --no-project --with ruff ruff check --select E,F,UP,B .
uv run --no-project --with pytest --with "fastapi[standard]" --with pydantic-settings --with sqlalchemy --with "psycopg[binary]" pytest
```

## Dokumente

- `docs/PRODUCT_ROADMAP.md`
- `docs/MVP_SPEC.md`
- `docs/STRATEGY_AND_ALERTS.md`
- `docs/DECISIONS.md`
- `docs/DATA_MODEL.md`
- `docs/TECH_ARCHITECTURE.md`

## Aktueller Stand

- FastAPI Backend Skeleton mit Health Endpoint
- Next.js App Router Frontend Skeleton mit Dashboard-Startseite
- Docker Compose fuer Web, API und PostgreSQL
- Caddy-Konfiguration fuer spaeteres VPS-Routing
- `.env.example` fuer lokale Konfiguration

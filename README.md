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

## Dokumente

- `docs/PRODUCT_ROADMAP.md`
- `docs/MVP_SPEC.md`
- `docs/STRATEGY_AND_ALERTS.md`
- `docs/DECISIONS.md`
- `docs/DATA_MODEL.md`
- `docs/TECH_ARCHITECTURE.md`

# Tech Architecture

## Ziel

Dieses Dokument definiert die technische Architektur der Trading- und Signal-Web-App.

Die Architektur soll als Web-App auf einem VPS laufen, von ueberall erreichbar sein, TradingView Webhooks empfangen, Telegram Alerts senden, TradingView CSV-Dateien importieren, Signale und Trades nachvollziehbar speichern und spaeter PWA/Mobile sowie weitere Datenquellen ermoeglichen.

## Architektur-Uebersicht

```text
Browser / Mobile
  -> Web App
  -> Backend API
  -> PostgreSQL

TradingView
  -> Webhook
  -> Backend API
  -> Alert Engine
  -> Telegram Bot

User
  -> Trade Republic manuell
  -> Trade Logging in Web App
```

## Tech Stack

Frontend:

- Next.js
- React
- TypeScript
- Tailwind CSS
- Next.js App Router

Backend:

- Python
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- uv

Datenbank:

- PostgreSQL

Deployment:

- Docker Compose
- Caddy
- HTTPS via Let's Encrypt
- VPS

Notifications:

- Telegram Bot API

## Services

Minimal produktives Setup:

- frontend
- backend
- postgres
- reverse-proxy

Spaeter optional:

- worker
- scheduler
- redis
- backup

## Domain-Struktur

Empfehlung fuer Start:

```text
trading.deinedomain.de
```

Pfade:

```text
/                       Web-App
/api                    Backend API
/api/webhooks/tradingview TradingView Webhook
```

Eine Subdomain ist fuer den Start einfacher als getrennte `app.` und `api.` Subdomains.

## Repo-Struktur

```text
trading-signal-tool/
  README.md
  docs/
    PRODUCT_ROADMAP.md
    MVP_SPEC.md
    STRATEGY_AND_ALERTS.md
    DECISIONS.md
    DATA_MODEL.md
    TECH_ARCHITECTURE.md

  apps/
    web/
    api/

  infra/
    docker-compose.yml
    caddy/
      Caddyfile

  scripts/
```

## Backend-Struktur

```text
apps/api/app/
  main.py
  core/
    config.py
    security.py
    auth.py
  db/
    session.py
    base.py
  models/
  schemas/
  api/routes/
  services/
  strategies/
  indicators/
  alerts/
  trades/
```

## Frontend-Struktur

```text
apps/web/src/
  app/
    dashboard/
    watchlist/
    signals/
    trades/
    journal/
    performance/
    import/
    settings/
    login/
  components/
  lib/
  types/
```

## API-Bereiche

Auth:

- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`

Watchlist:

- `GET /api/watchlist`
- `POST /api/watchlist`
- `GET /api/watchlist/{id}`
- `PATCH /api/watchlist/{id}`
- `DELETE /api/watchlist/{id}`

CSV Import:

- `POST /api/imports/csv`
- `GET /api/imports/{id}`
- `POST /api/imports/{id}/analyze`

Signals:

- `GET /api/signals`
- `POST /api/signals`
- `GET /api/signals/{id}`
- `PATCH /api/signals/{id}`
- `POST /api/signals/{id}/arm`
- `POST /api/signals/{id}/invalidate`
- `POST /api/signals/{id}/create-trade`

Trades:

- `GET /api/trades`
- `POST /api/trades`
- `GET /api/trades/{id}`
- `PATCH /api/trades/{id}`
- `POST /api/trades/{id}/events`
- `POST /api/trades/{id}/close`
- `POST /api/trades/{id}/review`

Alerts:

- `GET /api/alerts`
- `POST /api/alerts/test-telegram`
- `PATCH /api/alerts/{id}`

Webhooks:

- `POST /api/webhooks/tradingview`

Performance:

- `GET /api/performance/summary`
- `GET /api/performance/by-strategy`
- `GET /api/performance/by-asset-class`

Settings:

- `GET /api/settings`
- `PATCH /api/settings`

## Webhook Flow

TradingView sendet JSON an `/api/webhooks/tradingview`:

```json
{
  "secret": "DEIN_SECRET",
  "symbol": "{{ticker}}",
  "exchange": "{{exchange}}",
  "price": "{{close}}",
  "time": "{{time}}",
  "timeframe": "4H",
  "trigger": "long_entry",
  "setup_id": "123"
}
```

Backend prueft Secret, Payload, Setup, Symbol, Timeframe, Status, Risk/Reward und offene Trades. Wenn gueltig, wird Signal auf `triggered` gesetzt, ein Alert erstellt, Telegram gesendet und ein Event geloggt.

## Telegram Flow

Benötigt:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Nachrichtentypen:

- Entry Trigger
- Management
- Exit Warning
- Exit Signal
- Invalidation
- Test Message

## CSV Import Flow

1. Nutzer waehlt CSV-Datei.
2. Nutzer waehlt Symbol und Timeframe.
3. Backend liest CSV.
4. Backend validiert Pflichtfelder.
5. Backend normalisiert Datum und Zahlen.
6. Backend speichert MarketDataSeries und Candles.
7. Backend berechnet Indikatoren.
8. Backend erzeugt IndicatorSnapshot.
9. Backend fuehrt Signal Engine aus.
10. Backend erzeugt Signal-Karte.

Pflichtfelder:

- time
- open
- high
- low
- close
- volume

## Signal Engine Flow

1. Relevante MarketDataSeries laden.
2. Indikatoren berechnen oder laden.
3. Market Context pruefen.
4. Trend Pullback Long pruefen.
5. Base Breakout Long pruefen.
6. No-Trade-Regeln anwenden.
7. Score berechnen.
8. Entry/Stop/Targets berechnen.
9. R:R berechnen.
10. Signal-Karte mit Reasoning erzeugen.

## Trade Flow

1. Nutzer erhaelt Signal oder prueft Setup.
2. Nutzer handelt manuell bei Trade Republic.
3. Nutzer loggt Trade im Tool.
4. Tool berechnet Risiko und R:R.
5. Trade Status wird Open.
6. Nutzer kann Stop/Targets/Events loggen.
7. Tool kann spaeter Management-/Exit-Hinweise geben.
8. Nutzer schliesst Trade manuell.
9. Tool berechnet Ergebnis in R.
10. Nutzer reviewed Trade.

## Security

Pflicht:

- HTTPS
- Admin Login
- Password Hashing
- HttpOnly Cookie Auth
- Webhook Secret
- Environment Variables
- Telegram Token nicht im Code
- Datenbank nicht oeffentlich erreichbar
- Backups

Zusatzempfehlungen:

- Rate Limiting fuer Webhooks
- Request Logging
- CSRF Schutz bei Cookie Auth
- restriktives CORS
- starke Passwoerter
- regelmaessige Updates

Keine Secrets im Repo:

- `.env`
- Telegram Bot Token
- Webhook Secret
- Datenbank Passwort
- Admin Passwort

## Environment Variables

Backend:

- DATABASE_URL
- SECRET_KEY
- ADMIN_EMAIL
- ADMIN_INITIAL_PASSWORD
- TRADINGVIEW_WEBHOOK_SECRET
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
- CORS_ORIGINS

Frontend:

- NEXT_PUBLIC_API_BASE_URL

Postgres:

- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB

## Deployment Auf VPS

Operational deployment steps are documented in `docs/DEPLOYMENT_RUNBOOK.md`.

Zielsetup:

- VPS
- Docker
- Docker Compose
- Caddy
- PostgreSQL volume
- Backend container
- Frontend container
- HTTPS
- Domain DNS A Record auf VPS-IP

Spaetere Deployment-Schritte:

1. DNS vorbereiten.
2. Docker auf VPS installieren.
3. Repo auf VPS klonen.
4. `.env` auf VPS erstellen.
5. Docker Compose starten.
6. Migrationen ausfuehren.
7. Admin-User initialisieren.
8. Telegram Test senden.
9. TradingView Webhook Test durchfuehren.

## Backups

MVP Mindestanforderung:

- regelmaessiger PostgreSQL Dump
- Backup ausserhalb des Containers
- manuelle Restore-Anleitung
- Restore-Verifikation auf nicht-produktiver Kopie

The current backup and restore workflow is documented in `docs/DEPLOYMENT_RUNBOOK.md` and supported by `scripts/backup_postgres.sh` and `scripts/restore_postgres.sh`.

Spaeter:

- automatisierte taegliche Backups
- verschluesselte Offsite-Backups
- Backup Monitoring

## Testing

Backend Tests:

- Indicator Calculation
- CSV Validation
- Signal Engine
- Risk Calculator
- Webhook Validation
- Trade R Calculation

Manuelle Tests:

- CSV Upload
- Signal erzeugen
- Trade loggen
- Trade schliessen
- Review ausfuellen
- Telegram Test senden
- Webhook Test senden

## MVP Scope Technisch

Enthalten:

- Single-User Auth
- Watchlist API/UI
- CSV Import
- Indicator Calculation
- Signal Engine
- Signals UI
- Manual Trade Logging
- Trade Detail
- Journal Review
- Basic Performance
- Settings

MVP+:

- TradingView Webhook
- Telegram Alerts
- Alert History
- Exit Warnings

Nicht im MVP:

- Broker Integration
- Automatic Trading
- Multi-User
- Native Android
- Complex Backtesting
- Screenshot AI
- Discord
- Live Market Data API

## Technische Entscheidungen

- Monorepo fuer Frontend, Backend, Infra und Docs
- FastAPI separat von Next.js
- PostgreSQL statt SQLite
- Docker Compose statt manueller Installation
- Caddy statt Nginx
- HttpOnly Cookie Auth statt LocalStorage JWT
- Next.js App Router
- uv fuer Python Dependencies
- Tailwind + eigene Komponenten
- erst lokal entwickelbar, dann VPS Deployment

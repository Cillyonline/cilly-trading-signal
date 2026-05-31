# Trading Signal Tool

Webbasierte Trading- und Signal-Plattform fuer Aktien und Krypto.

Ziel ist ein professionelles Trading-Cockpit fuer Long-only Swingtrading: Setups analysieren, Trigger vorbereiten, Alerts pruefen, extern ausgefuehrte Trades manuell loggen, Trades dokumentieren und historische Performance in R-Multiples auswerten.

## Grundprinzipien

- Context first, Setup second, Trigger third, Risk always.
- Keine automatische Orderausfuehrung.
- Keine Broker-Anbindung im MVP.
- Signale sind Entscheidungsunterstuetzung, keine blinden Buy-/Sell-Anweisungen.
- Trading-Ausfuehrung bleibt manuell, z.B. ueber Trade Republic.
- Performance zeigt dokumentierte historische Ergebnisse, keine Prognosen oder Gewinnzusagen.
- Strategie, Score und Alerts muessen erklaerbar sein.

## MVP Auth

Das MVP nutzt Single-User Login mit einem HttpOnly Session-Cookie. Es gibt keine oeffentliche Registrierung und keine clientseitige Token-Speicherung.

Konfiguration in `.env`:

- `ADMIN_EMAIL`: Login-E-Mail fuer den einzelnen Admin-User.
- `ADMIN_INITIAL_PASSWORD`: Initiales Passwort, mit dem der Admin-User beim ersten Login angelegt wird.
- `SECRET_KEY`: Signiert Session-Cookies und muss ausserhalb lokaler Entwicklung eindeutig gesetzt sein.
- `AUTH_COOKIE_SECURE`: In produktiven HTTPS-Umgebungen auf `true` setzen.

In `staging` und `production` bricht die API beim Start ab, wenn lokale Platzhalter-Secrets, Default-Credentials, unsichere Datenbank-Zugangsdaten, Wildcard-CORS oder unsichere Auth-Cookies konfiguriert sind.

Details zu produktionsnahen Umgebungsvariablen, sicheren Werten und Secret-Rotation stehen in `docs/DEPLOYMENT_RUNBOOK.md`. Die Werte aus `.env.example` sind lokale Platzhalter und ausserhalb von `development`/`test` absichtlich unsicher.

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
- GitHub CLI optional fuer Issue-/PR-Arbeit

Hinweis: Das Backend ist aktuell auf Python 3.12 ausgelegt. Wenn `python --version` lokal Python 3.13 oder neuer zeigt, fuer lokale API-Entwicklung Python 3.12 installieren oder Docker Compose verwenden.

Empfohlene Versionschecks:

```powershell
docker --version
docker compose version
node --version
npm --version
python --version
uv --version
```

Falls `uv` fehlt:

```powershell
winget install astral-sh.uv
```

### MVP Smoke Runner

Fuer den dokumentierten MVP Smoke Test gibt es einen Runner, der Preflight-Checks,
Stack-Start, lokale Datenbankmigrationen und API-Health automatisiert. Der Runner
ersetzt nicht den Browser-Teil des Smoke Tests und macht keine Produktionsfreigabe-
Aussage:

```powershell
.\scripts\smoke_test.ps1                       # hochfahren + Health-Check
.\scripts\smoke_test.ps1 -Cleanup              # herunterfahren (Volumes bleiben)
.\scripts\smoke_test.ps1 -Cleanup -PurgeVolumes # herunterfahren + Volumes loeschen
```

Details und Browser-Workflow stehen in `docs/MVP_SMOKE_TEST.md`; die wiederholbare
Browser-Clickthrough-Checkliste steht in `docs/FINAL_BROWSER_CLICKTHROUGH_CHECKLIST.md`.

### Docker Compose

Docker Compose ist der bevorzugte lokale Smoke-Test, weil Web, API und Postgres zusammen starten.

Einmalig lokale Umgebung anlegen:

```powershell
Copy-Item .env.example .env
```

Start:

```powershell
docker compose -f infra/docker-compose.yml up --build
```

Smoke-Checks in einem zweiten Terminal:

```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

Danach im Browser pruefen:

- Web: `http://localhost:3000`
- API Health: `http://localhost:8000/api/health`

Stop:

```powershell
docker compose -f infra/docker-compose.yml down
```

Mit Caddy-Profil:

```powershell
docker compose -f infra/docker-compose.yml --profile proxy up --build
```

### Lokale Entwicklung Ohne Docker

Web:

```powershell
cd apps/web
npm install
npm run dev
```

API:

```powershell
cd apps/api
uv run --with "fastapi[standard]" --with pydantic-settings --with sqlalchemy --with "psycopg[binary]" fastapi dev app/main.py
```

Hinweis: Die API erwartet standardmaessig Postgres unter dem Docker-Service-Namen `postgres`. Fuer API-Entwicklung ohne Docker Compose muss `DATABASE_URL` passend auf eine erreichbare lokale Datenbank gesetzt werden.

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
- `docs/DELIVERY_ROADMAP.md`
- `docs/MVP_SPEC.md`
- `docs/COCKPIT_REVIEW_WORKFLOW.md`
- `docs/SCREENER_CSV_MODEL.md`
- `docs/PROFESSIONAL_STRATEGY_PLAYBOOK.md`
- `docs/ASSET_SPECIFIC_SIGNAL_FILTERS.md`
- `docs/STRATEGY_CALIBRATION_WORKFLOW.md`
- `docs/HISTORICAL_PAPER_REVIEW_PROTOCOL.md`
- `docs/STRATEGY_AND_ALERTS.md`
- `docs/DECISIONS.md`
- `docs/DATA_MODEL.md`
- `docs/TECH_ARCHITECTURE.md`
- `docs/DEPLOYMENT_RUNBOOK.md`
- `docs/MVP_SMOKE_TEST.md`
- `docs/MVP_RELEASE_CHECKLIST.md`
- `docs/VPS_STAGING_DECISION_GATE.md`
- `docs/V1_3_ALERT_ROUTING_SMOKE_TEST.md`

Operational deployment, PostgreSQL backup/restore, healthcheck, logging, and deployment smoke-test steps are documented in `docs/DEPLOYMENT_RUNBOOK.md`. Backup files and logs may contain sensitive app data and must not be committed or shared without review.

The intended manual cockpit review flow is documented in `docs/COCKPIT_REVIEW_WORKFLOW.md`. The local MVP smoke-test history is documented in `docs/MVP_SMOKE_TEST.md`. Private VPS staging smoke evidence and the conditional staging-only decision gate are documented in `docs/VPS_STAGING_SMOKE_TEST.md` and `docs/VPS_STAGING_DECISION_GATE.md`; this is not a production-readiness claim.

The current MVP release posture is summarized in `docs/MVP_RELEASE_CHECKLIST.md`. The checklist separates Done, Partial, Missing, Blocked, and Not Included areas and must not be read as a production or profitability claim.

## Aktueller Stand

Das Projekt ist ueber den Skeleton hinaus und bildet den MVP-Kernfluss bereits ab. Es ist weiterhin ein Review- und Entscheidungsunterstuetzungs-Tool, keine produktionsfertige Trading-Plattform.

Implementiert:

- FastAPI Backend mit SQLAlchemy-Modellen, Alembic-Migrationen und geschuetzten MVP-Routen.
- Next.js App Router Frontend mit Login, Dashboard, Watchlist, CSV Import, Signals, Trades, Trade Detail und Settings.
- Single-User Auth mit HttpOnly Session-Cookie, ohne oeffentliche Registrierung und ohne clientseitige Token-Speicherung.
- Watchlist-Verwaltung fuer Aktien und Krypto.
- TradingView CSV Import fuer `1W`, `1D` und `4H` mit Pflichtfeld-, Plausibilitaets- und Kerzenanzahl-Pruefung.
- TradingView Screener CSV Import als gespeicherte Review-Snapshots mit expliziter manueller Watchlist-Uebernahme und sichtbarer Duplikatbehandlung.
- Marktdaten-Source/Freshness/Sync-Metadaten fuer CSV- und Provider-Serien, inklusive konservativer Stale-/Failed-/Partial-Anzeige.
- Manueller, serverseitig geschuetzter Provider-Sync fuer Daily/EOD-Daten ueber den ersten Alpha-Vantage-Adapter, disabled-by-default und ohne Scheduler.
- Persistierte Multi-Timeframe-Analyse mit echten `1W`, `1D` und `4H` Daten als Grundlage fuer konservative Signale.
- Indikator-Basis fuer EMA, RSI, ATR, Volumen, Relative Volume und Swing-Struktur.
- Erklaerbare Signal-Erzeugung fuer Trend Pullback Long und Base Breakout Long mit Score, Status, Risk Flags, No-Trade-Reasons und Next Action.
- Manuelles Trade Logging mit Risk/R:R-Berechnung, Events, Close-Flow, Journal und Performance-Kennzahlen in R.
- Risk Settings fuer Account Size, maximales Risiko, Mindest-R:R und maximale offene Trades.
- TradingView Webhook-Ingestion, Alert Events UI, expliziter Telegram-Testversand und policy-gesteuerte automatische Telegram-Alert-Zustellung mit Dedup/Rate-Limit ohne Ausfuehrung.
- Docker Compose fuer Web, API und PostgreSQL sowie Caddy-Konfiguration fuer spaeteres VPS-Routing.
- CI fuer API lint/tests, Web build und PostgreSQL/Alembic Migration Smoke.
- Private VPS Staging Smoke Test und Conditional-Go-Entscheidung fuer kontrollierte Owner/Operator-Nutzung.

Teilweise umgesetzt oder noch MVP-limitiert:

- TradingView CSV bleibt die manuelle Baseline und der Fallback; Provider-Sync ist optional, manuell ausgeloest und nicht als Live- oder Realtime-Datenquelle zu verstehen.
- Screener CSV bleibt ein Kandidaten-Review-Workflow; daraus entstehen nicht automatisch Analysen, Signale, Trades, Alerts oder Orders.
- Der aktuelle Provider-Pfad deckt Daily/EOD zuerst ab; `4H`/Intraday-Providerdaten bleiben nicht zugesagt.
- Analyse und Signale sind deterministisch und konservativ, aber keine validierte Strategie und keine Gewinnprognose.
- Auth ist bewusst Single-User; Multi-User, Rollenmodell und Self-Service-Registrierung sind nicht Teil des MVP.
- Risk Settings erzwingen Basisregeln beim manuellen Trade Logging, ersetzen aber kein vollstaendiges Portfolio-Risikomanagement.
- Dashboard, Journal und Performance sind funktional, aber noch Basisansichten.
- Alerting ist fuer v1.3 als Review-Routing implementiert; echter Telegram-Provider-Smoke auf dem VPS bleibt ein operator-run Schritt mit redigierter Evidenz.

Nicht enthalten:

- Automatische Orderausfuehrung.
- Broker- oder Exchange-Integration.
- Live Market Data, Realtime-Signale, Backtesting Engine, Mobile App oder Multi-User SaaS-Betrieb.

Aktuelle Blocker und offene Punkte:

- Keine Produktionsfreigabe: Deployment, Monitoring, Backups, Secrets-Betrieb und Security Review sind noch offen.
- Private VPS Staging ist nur conditional-go fuer kontrollierte Owner/Operator-Nutzung; breitere oder produktionsnahe Nutzung braucht weiterhin separate Operational-Readiness-Entscheidungen.
- Dokumentation und Roadmap muessen nach jedem groesseren Slice weiter synchron gehalten werden.

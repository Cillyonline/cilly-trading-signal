# Product Roadmap

## Vision

Wir bauen eine webbasierte Trading- und Signal-Plattform fuer Aktien und Krypto. Das Tool soll Swingtrading-Setups professionell analysieren, Trigger ueberwachen, gestartete Trades dokumentieren und Management-/Exit-Signale ausgeben.

Das Ziel ist kein automatisches Trading, sondern ein strukturiertes Trading-Cockpit fuer bessere Entscheidungen, bessere Disziplin und messbare Performance.

## Grundprinzipien

- Context first, Setup second, Trigger third, Risk always.
- Keine blinden Buy-/Sell-Signale.
- Jedes Signal braucht Begruendung, Risiko, Stop, Ziel und Invalidierung.
- Manuelle Ausfuehrung bleibt beim Trader.
- Keine Broker-Anbindung im Startumfang.
- Keine automatische Orderausfuehrung.
- Fokus auf Qualitaet statt Quantitaet.
- Performance wird in R-Multiples gemessen, nicht nur in EUR.

## Zielnutzer

Primaer:

- Single-User: privater Trader
- Aktien und Krypto
- Swingtrading
- gelegentlich Investing
- manuelle Ausfuehrung ueber Trade Republic oder andere Plattformen

Spaeter moeglich:

- Multi-User
- Team-/Community-Modus
- weitere Broker-/Exchange-Integrationen
- erweiterte Mobile/PWA-Nutzung ueber die aktuelle installierbare Baseline hinaus

## Asset-Klassen

Version 1:

- Aktien
- Krypto

Empfohlener Fokus:

- liquide US-Aktien
- grosse Krypto-Coins
- keine illiquiden Pennystocks
- keine extrem kleinen Altcoins

## Trading-Stil

Primaer:

- Long-only Swingtrading

Timeframes:

- 1W: uebergeordneter Kontext
- 1D: Setup-Erkennung
- 4H: Trigger und Trade Management

Nicht im Startfokus:

- Scalping
- Daytrading auf 5m/15m
- Short-Trading
- News-Trading
- automatische Ausfuehrung

## Kernstrategien

Version 1:

- Trend Pullback Long
- Base Breakout Long

Spaeter optional:

- Reclaim Long
- Investing-Modus
- Short-Setups
- Marktregime-basierte Screener

## Trade Lifecycle

Ein Setup oder Trade kann folgende Zustaende durchlaufen:

- Scanned
- Watchlist
- Armed
- Triggered
- Entered
- Open
- Managed
- Exit Warning
- Exit Signal
- Closed
- Reviewed
- Invalidated
- Missed
- Expired

Fuer Version 1 sind besonders wichtig:

- Watchlist
- Armed
- Triggered
- Open
- Closed
- Reviewed
- Invalidated

## Alert-System

Alerts sind handlungsorientierte Signale, nicht nur Preisalarme.

Farben:

- Grau: Info
- Gelb: Watch / Armed
- Gruen: Triggered
- Blau: Management
- Rot: Warning / Exit / Invalidated

Prioritaeten:

- P1: sofort pruefen
- P2: zeitnah pruefen
- P3: Information

## Current Internal Review Candidate Scope

Der aktuelle Stand ist ein kontrolliertes Owner/Operator-Review-Cockpit, kein produktionsreifes Trading-System. Implementiert sind:

- Watchlist fuer Aktien und Krypto.
- TradingView OHLCV CSV Import als manuelle Baseline.
- Guarded manual Daily/EOD provider sync mit Source/Freshness-Kontext, disabled-by-default.
- Deterministische Multi-Timeframe-Analyse mit erklaerbaren Long-only Setups.
- Benchmark-Kontext fuer gespeicherte Daily-Kontexte (`SPY`/`QQQ`, `BTC`/`ETH`).
- Explainable Signal Review mit Reasoning, Risk Flags, No-Trade-Gruenden, Next Action und stale Signal Visibility.
- Alert Event Review mit policy-gated Telegram Routing, Dedup und Rate Limit, ohne Buy/Sell-Anweisung.
- Manuelles Trade Logging, Management Events, Close Flow, Journal und Performance in R-Multiples.
- Open Portfolio Risk, Risk-Warnungen, Asset-Konzentration, einfache Correlation-Proxies und Trade Journal Analytics.
- TradingView Screener CSV Snapshots, Review-Kandidaten, Bulk Review und explizite Watchlist-Konvertierung.
- Historical/Paper Review Batches fuer Prozess-Evidence, nicht fuer Profitabilitaetsvalidierung.
- Mobile Review Verbesserungen fuer Signals und Review Batches plus installierbare PWA-Manifest-Baseline.
- Operational Readiness Docs: Monitoring Checklist, Health Details, Backup Restore Drill, Security Scan Workflow und Incident Runbook.

Weiterhin nicht enthalten:

- Produktionseinsatz oder Public SaaS.
- Broker-/Exchange-Integration, Account Sync oder automatische Orders.
- Live-/Realtime-Marktdatenversprechen.
- Automatische Marktaktualisierung oder scheduler-driven Analyse.
- Backtesting-/Profitabilitaetsvalidierung.
- Multi-User, Rollenmodell, Registrierung, Billing oder Support-Prozesse.

## Datenquellen

Version 1:

- TradingView CSV Upload
- manuelle Watchlist
- manuelle Trade-Eingabe

MVP+:

- TradingView Webhook Alerts
- Telegram Notifications
- manueller Provider-Sync fuer Daily/EOD-Marktdaten, disabled-by-default und mit Source/Freshness-Kontext

Spaeter:

- weitere Kursdaten-APIs und Provider-Timeframes nach Kosten-, Lizenz- und Rate-Limit-Pruefung
- automatische Marktaktualisierung
- Broker-/Exchange-Import optional

## Technische Zielarchitektur

- Frontend: responsive Web-App mit installierbarer PWA-Manifest-Baseline
- Backend: API, Signal Engine, Alert Engine, Trade Manager, Exit Engine
- Datenbank: PostgreSQL
- Deployment: VPS, Docker Compose, Domain, HTTPS, Caddy
- Notifications: Telegram Bot zuerst

## Sicherheit

- Single-User Login
- HTTPS Pflicht
- Webhook Secret
- Telegram Bot Token geheim halten
- keine Broker API Keys im MVP
- keine automatische Orderausfuehrung
- Datenbank-Backups
- Rate Limiting fuer Webhooks

## Roadmap

### Phase 0: Planung & Infrastruktur

- Produktumfang festhalten
- Strategien definieren
- Alert-System definieren
- VPS-/Domain-/Deployment-Konzept planen
- Telegram Bot vorbereiten

### Phase 1: Web-App Basis

- Single-User Login
- Dashboard-Grundstruktur
- Navigation
- Settings
- Risk Settings

### Phase 2: CSV Import & Datenpruefung

- TradingView CSV hochladen
- OHLCV-Daten speichern
- Datenqualitaet pruefen
- Symbol und Timeframe zuordnen
- EMA20, EMA50, EMA200, RSI14, ATR14, Volume Average berechnen

### Phase 3: Signal Engine

- Trend Pullback Long erkennen
- Base Breakout Long erkennen
- Signal-Karte erzeugen
- Score berechnen
- No-Trade-Regeln anwenden

### Phase 4: Watchlist & Armed Setups

- Setups speichern
- Setups manuell bewerten
- Setups auf Armed setzen
- Trigger-Level verwalten
- TradingView Alert Text vorbereiten

### Phase 5: Trade Logging

- manuelle Trades erfassen
- Entry, Stop, Targets und Positionsgroesse speichern
- Risiko berechnen
- Trade Status verwalten
- Basis-Journal im Trade Detail

### Phase 6: TradingView Webhooks & Telegram Alerts

- Webhook-Endpunkt bereitstellen
- TradingView Payload verarbeiten
- Secret pruefen
- Setup erneut validieren
- Telegram Alert senden
- Alert-Historie speichern

### Phase 7: Exit Engine & Trade Management

- Stop erreicht erkennen
- Target erreicht erkennen
- Break-even-Hinweise geben
- Trailing Stop Hinweise geben
- Exit Warning generieren
- Exit Signal generieren

### Phase 8: Journal & Performance

- Trades reviewen
- R-Multiple berechnen
- Setup-Qualitaet bewerten
- Execution-Qualitaet bewerten
- Performance nach Strategie auswerten

### Phase 9: Screener & Automation

- TradingView Screener CSV importieren
- viele Symbole vorfiltern
- manuell bestaetigte Watchlist-Kandidaten erzeugen
- Marktregime beruecksichtigen

### Phase 10: PWA / Mobile

- Web-App mobil optimieren
- installierbar auf Android
- schnelle Alert-Ansichten
- Trade Management mobil nutzbar

Status: Phase 9 ist als Screener-CSV-Reviewworkflow umgesetzt, aber ohne automatische Analyse- oder Trade-Erstellung. Phase 10 hat eine mobile Audit-Baseline, verbesserte mobile Signal- und Review-Batch-Workflows sowie ein PWA Manifest; weitere mobile Screener-/Trade-/Header-Politur bleibt Follow-up.

## Nicht-Ziele Fuer Den Start

- automatische Orderausfuehrung
- Broker-Anbindung
- Short-Trading
- native Android-App
- Multi-User
- KI-Screenshot-Analyse
- komplexe Backtesting Engine
- Intraday-Scalping
- Optionshandel
- Hebel-/Margin-Automatisierung

## Erfolgsdefinition

Das Projekt ist fuer den finalen internen Review Candidate erfolgreich, wenn das Tool Long-only Swingtrading-Setups strukturiert und erklaerbar zur manuellen Pruefung aufbereitet, schlechte oder unvollstaendige Setups konservativ als No Trade sichtbar macht, manuelles Trade Logging und Review-Batches erlaubt, offene Risiken und Performance in R nachvollziehbar dokumentiert und dabei keine Broker-Aktionen, automatische Orders, Profitabilitaetsversprechen oder Trading Advice erzeugt.

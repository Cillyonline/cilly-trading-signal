# MVP Spec

## Ziel Des MVP

Das MVP soll eine erste nutzbare Web-App liefern, mit der Long-only Swingtrading-Setups fuer Aktien und Krypto strukturiert analysiert, gespeichert, bewertet und manuell dokumentiert werden koennen.

Der Fokus liegt auf:

- Watchlist
- CSV Import
- Signal-Karte
- Trend Pullback Long
- Base Breakout Long
- manuelles Trade Logging
- Basis-Journal
- Basis-Performance in R
- Risk Settings

Der praktische Tages-/Wochenablauf ueber Dashboard, Watchlist, Import/Provider Sync,
Signals, Alerts, Trades, Journal und Performance ist in
`docs/COCKPIT_REVIEW_WORKFLOW.md` beschrieben.

Nicht enthalten sind automatische Orderausfuehrung, Broker-Anbindung und Kauf-/Verkaufsanweisungen.

## Nutzer

Version 1 ist fuer einen Single-User gedacht. Der Nutzer handelt manuell ausserhalb der App, nutzt Trade Republic oder andere Broker/Exchanges, prueft Signale und Trigger eigenverantwortlich, dokumentiert Trades und wertet historische Performance in R aus.

## Safety Boundaries

- Signale sind Entscheidungshilfe fuer manuelle Pruefung, keine Kauf- oder Verkaufsanweisung.
- Ein Signal erzeugt keinen Trade und fuehrt keine Order aus.
- Trade Logging dokumentiert extern ausgefuehrte Trades; die App hat keine Broker-Aktion.
- Performance zeigt historische, dokumentierte R-Multiples und keine Prognose oder Gewinnzusage.
- `No Setup` und `No Trade` sind vollwertige konservative Ergebnisse.

## Kernworkflow

### 1. Watchlist Pflegen

Der Nutzer legt relevante Symbole an, z.B. `AAPL`, `MSFT`, `NVDA`, `BTCUSDT`, `ETHUSDT`, `SOLUSDT`.

Pro Symbol werden gespeichert:

- Symbol
- Name optional
- Asset Class: Stock / Crypto
- Exchange optional
- aktiv/inaktiv
- Notizen

### 2. Marktdaten Bereitstellen

Der Nutzer laedt TradingView CSV-Daten hoch. Optional kann ein manueller, serverseitig
geschuetzter Provider-Sync fuer unterstuetzte Daily/EOD-Daten angefragt werden, wenn
die Umgebung bewusst dafuer konfiguriert ist. Provider-Sync ist disabled-by-default,
kein Live-Datenfeed und erzeugt keine automatische Analyse, kein Signal und keinen
Trade.

Pflichtfelder:

- time
- open
- high
- low
- close
- volume

Zusatzangaben:

- Symbol
- Timeframe: 1W / 1D / 4H
- Asset Class

Das Tool prueft Pflichtfelder, ausreichend Kerzen, fehlende Werte, Plausibilitaet und Timeframe-Zuordnung. Gespeicherte Marktdaten tragen Source-, Freshness- und Sync-Status, damit stale, failed, partial oder unknown Daten konservativ behandelt werden.

### 3. Analyse Starten

Das Tool berechnet:

- EMA20
- EMA50
- EMA200
- RSI14
- ATR14
- Volume Average
- Relative Volume
- Swing Highs
- Swing Lows

Danach bewertet es Trend, Struktur, Momentum, Volumen, Volatilitaet, Risk/Reward und No-Trade-Regeln.

### 4. Signal-Karte Erzeugen

Eine Signal-Karte enthaelt:

- Symbol
- Asset Class
- Timeframe
- Setup Type
- Bias
- Status
- Score
- Entry Zone
- Trigger Level
- Stop Loss
- Target 1
- Target 2
- Risk/Reward
- Invalidierung
- Begruendung
- Naechster Pruefschritt

Status:

- Watchlist
- Armed
- Invalidated
- No Setup

### 5. Setup Bewerten

Moegliche Aktionen:

- Setup speichern
- Setup auf Armed setzen
- Setup invalidieren
- Setup verwerfen
- Notiz hinzufuegen

### 6. Trade Manuell Loggen

Trade Logging ist reine Dokumentation eines extern ausgefuehrten Trades. Die App platziert keine Orders.

Pflichtfelder:

- Symbol
- Setup Type
- Entry Price
- Stop Loss
- Position Size
- Opened At

Optionale Felder:

- Target 1
- Target 2
- Fees
- Screenshot
- Notiz

Das Tool berechnet Risiko pro Einheit, Gesamtrisiko, Risiko in Prozent, Initial R:R, 1R und Potenzial zu Targets.

### 7. Trade Verwalten

Der Nutzer kann Stop-Anpassungen, Target-Anpassungen, Teilgewinn-Notizen, Trade Close und Notizen dokumentieren.

### 8. Trade Schliessen

Beim Schliessen werden Exit Price, Exit Date, geschlossene Menge, Exit Reason und optional Kommentar erfasst. Das Tool berechnet dokumentiertes Ergebnis, Ergebnis in R, Haltedauer und Setup-Ergebnis.

### 9. Review / Journal

Nach Abschluss beantwortet der Nutzer kurze Review-Fragen:

- War das Setup regelkonform?
- War der Entry sauber?
- War der Stop logisch?
- War der Exit planmaessig?
- Wurde das Risiko eingehalten?
- Gab es emotionale Fehler?
- Was war die wichtigste Lesson Learned?

## MVP-Seiten

### Dashboard

- offene Trades
- aktuelle Setups
- Armed Setups
- zuletzt importierte CSVs
- Performance Kurzueberblick
- Warnungen oder fehlende Reviews

MVP-Kennzahlen:

- Open Trades
- Armed Setups
- Closed Trades
- Total R
- Winrate
- Average R

### Watchlist

Spalten:

- Symbol
- Asset Class
- Exchange
- Active
- Last Imported
- Current Status
- Notes

### CSV Import

Funktionen:

- Datei auswaehlen
- Symbol zuordnen
- Timeframe waehlen
- Daten pruefen
- Import starten
- Analyse starten

### Provider Sync

Funktionen:

- manuelle Sync-Anfrage fuer ein Watchlist-Symbol und einen Timeframe
- Anzeige von Sync-Status, Freshness, Provider-Kontext und sanitisierten Fehlern
- keine Scheduler, keine Live-/Realtime-Anzeige, keine automatische Analyse und keine Trade-Erstellung

### Signals

Spalten:

- Symbol
- Setup Type
- Status
- Score
- Trigger Level
- Entry Zone
- Stop
- Target 1
- Target 2
- R:R
- Created At

### Signal Detail

- Setup-Zusammenfassung
- Strategie-Begruendung
- Trend-Bewertung
- Struktur-Bewertung
- Momentum-Bewertung
- Volumen-Bewertung
- Risk/Reward
- No-Trade-Checks
- Entry/Stop/Targets
- Invalidierung
- Naechste Aktion

### Trades

- Symbol
- Status
- Setup Type
- Entry
- Stop
- Target 1
- Target 2
- Position Size
- Risk %
- Result R
- Opened At
- Closed At

### Trade Detail

- urspruenglich dokumentierter Trade Plan
- aktuelle Trade-Daten
- Risk Calculation
- Management Events
- Notes
- Journal Review
- Ergebnis in R

### Performance

- Total R
- Winrate
- Average R
- Best Trade
- Worst Trade
- Anzahl Trades
- offene Trades
- abgeschlossene Trades

### Settings

- Account
- Risk Settings
- Strategy Settings
- Notification Settings placeholder

Risk Defaults:

- Default Risk: 0.5% bis 1.0%
- Minimum R:R: 2.0
- Max Open Trades: 3 bis 5

## MVP-Strategien

### Trend Pullback Long

MVP-Erkennung:

- Close > EMA200
- EMA20 > EMA50 oder EMA50 steigend
- Preis korrigiert Richtung EMA20/EMA50 oder Support
- RSI ideal zwischen 40 und 60
- Pullback nicht parabolisch
- R:R >= 1:2

MVP-Trigger:

- 4H Close ueber kleinem Lower High
- oder 4H Close zurueck ueber EMA20/EMA50

### Base Breakout Long

MVP-Erkennung:

- Preis ueber EMA200
- klare mehrtaegige Konsolidierung
- Base High erkennbar
- EMA20/EMA50 steigend oder stabil
- Volumen idealerweise ruecklaeufig in der Base
- R:R >= 1:2

MVP-Trigger:

- 4H Close ueber Base High
- oder Daily Close ueber Base High

## Scoring Im MVP

- Trend: 0-25
- Struktur: 0-25
- Momentum: 0-15
- Volumen: 0-15
- Risk/Reward: 0-15
- Risiko-/Ausschlussfilter: -20 bis 0

Signal-Klassen:

- 80-100: A-Setup
- 65-79: B-Setup
- 50-64: Watchlist
- unter 50: No Trade

Der Score ist keine Gewinnwahrscheinlichkeit und keine Handlungsempfehlung. Er bewertet die Setup-Qualitaet.

## No-Trade-Regeln Im MVP

Kein Trade, wenn:

- R:R < 1:2
- Weekly oder Daily Kontext klar bearish
- Preis direkt unter starkem Widerstand liegt
- Stop technisch nicht sinnvoll platzierbar ist
- Setup bereits invalidiert wurde
- Kurs zu weit ueber Trigger gelaufen ist
- Asset illiquide ist
- Datenqualitaet schlecht ist

Fuer Aktien wird Earnings-Risiko mindestens als Warnung angezeigt. Fuer Krypto wird extrem hohe ATR als Risiko-Warnung angezeigt.

## MVP+ Erweiterungen

- TradingView Webhook Endpoint
- Telegram Bot Alerts fuer policy-erlaubte Review-Ereignisse (`near_trigger`, `entry_trigger`, `invalidation`, `exit_warning`)
- Alert-Historie
- Triggered Status automatisch setzen
- Exit Warning Basisregeln
- Management Alerts
- TradingView Alert Text Generator

## Nicht Im MVP

- automatische Orderausfuehrung
- Broker-/Trade-Republic-Anbindung
- Kauf-/Verkaufsanweisungen
- Short-Signale
- Multi-User
- native Android-App
- komplexer Screener
- vollstaendiges Backtesting
- KI-Screenshot-Analyse
- Discord Integration
- automatische Kursdaten-API
- Optionshandel
- Hebel-/Margin-Automatisierung

## Akzeptanzkriterien

Das MVP ist erfolgreich, wenn Login, Watchlist, CSV Upload, OHLCV Validierung, Indikatorberechnung, Signal-Karten, Armed Setups, manuelle Trade-Dokumentation, Risiko-/R-Berechnung, Trade Review und Basis-Performance funktionieren, ohne automatische Orderausfuehrung oder Broker-Anbindung.

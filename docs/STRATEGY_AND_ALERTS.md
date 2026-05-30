# Strategy And Alerts

## Ziel

Dieses Dokument definiert Trading-Strategien, Trigger, Alarme, Scoring-Regeln, No-Trade-Regeln und den Trade-Lifecycle des Tools.
Das professionelle Zielmodell fuer die v2.1 Strategie-Kalibrierung ist in
`docs/PROFESSIONAL_STRATEGY_PLAYBOOK.md` beschrieben.

Das Tool erzeugt keine Kauf- oder Verkaufsempfehlungen. Es bewertet Setups strukturiert,
ueberwacht Trigger und liefert erklaerbare Pruefpunkte fuer manuelle Entscheidungen.

Grundprinzip:

```text
Context first, Setup second, Trigger third, Risk always.
```

## Timeframe-Modell

### 1W: Kontext

Der Weekly Timeframe dient zur uebergeordneten Einschaetzung:

- langfristiger Trend
- wichtige Weekly Supports und Resistances
- Ueberdehnung
- grobe Marktphase
- strukturelle Higher Highs / Higher Lows

Bewertung:

- Bullish: Long-Setups erlaubt
- Neutral: nur starke Setups erlaubt
- Bearish: kein Long-Trade

### 1D: Setup

Der Daily Timeframe ist der Haupt-Timeframe fuer Setup-Erkennung:

- Trend
- Pullback
- Base
- Breakout-Zone
- Support / Resistance
- Momentum
- Volumen
- Risk/Reward

### 4H: Trigger Und Management

Der 4H Timeframe dient fuer Entry-Timing und Trade Management:

- Trigger Close
- kleinere Swing Highs / Swing Lows
- 4H Struktur
- Reversal
- Stop-Logik
- Exit Warning
- Trailing Stop

Regel:

- Price Touch = Voralarm
- 4H Close = Entry Trigger
- Daily Close = staerkere Bestaetigung

## Signal Freshness

MVP-Signale basieren auf gespeicherten Analysen aus TradingView CSV-Daten oder
provider-backed Daten, die zuvor manuell synchronisiert und persistiert wurden. Die
App behauptet keine Live-Freshness.

The source/freshness model is documented in `docs/MARKET_DATA_FRESHNESS_MODEL.md`.
It keeps CSV and provider-backed data explicit and treats stale, failed, partial,
missing, or unknown data conservatively.

Konservative Regel:

- aktive Review-Kandidaten (`watchlist`, `armed`, `triggered`) gelten nach 7 Tagen seit dem letzten gespeicherten Signal-Update als stale.
- stale bedeutet: nicht als aktuellen Review-Kandidaten behandeln, bis neue Daten importiert oder manuell synchronisiert und anschliessend bewusst analysiert wurden.
- stale erzeugt keine automatische Order, keinen Alert und keine Strategie-Neubewertung.
- terminale Review-Zustaende wie `invalidated`, `missed` oder `expired` werden nicht als stale markiert, weil sie bereits manuell eingeordnet sind.
- provider-backed data that is stale, failed, partial, missing, or unknown must not be treated as current without explicit freshness checks.
- insufficient freshness should add clear no-trade reasons such as `market_data_stale`, `market_data_missing_timeframe`, `market_data_sync_failed`, `market_data_partial`, or `market_data_source_unknown`.

## Strategie A: Trend Pullback Long

### Idee

Ein Asset befindet sich in einem gesunden Aufwaertstrend und korrigiert kontrolliert zurueck. Der Einstieg erfolgt erst nach Bestaetigung durch einen Trigger.

### Kontext-Bedingungen

- Weekly Kontext ist nicht bearish
- Daily Close liegt ueber EMA200
- EMA50 steigt oder EMA20 liegt ueber EMA50
- keine extreme Ueberdehnung direkt davor
- Asset ist ausreichend liquide

### Setup-Bedingungen

- Preis korrigiert Richtung EMA20, EMA50 oder Support
- Pullback wirkt kontrolliert
- RSI liegt ideal zwischen 40 und 60
- Pullback-Volumen ist nicht aggressiver als Aufwaertsvolumen
- vorheriger Trend ist klar erkennbar
- R:R mindestens 1:2 moeglich

### Positive Merkmale

- Pullback haelt ueber EMA50
- Preis haelt ueber vorherigem Daily Support
- Volumen nimmt im Ruecksetzer ab
- 4H macht erstes Higher Low
- relative Staerke gegenueber Markt/Sektor bleibt stabil
- Stop kann technisch sauber gesetzt werden

### Negative Merkmale

- Preis faellt mit hohem Volumen
- Daily Close unter EMA50
- Bruch des letzten wichtigen Higher Lows
- Preis steht direkt unter starkem Widerstand
- RSI bleibt schwach trotz Bounce
- R:R wird schlechter als 1:2

### Trigger

Gueltige Trigger:

- 4H Close ueber letztem kleinen Lower High
- 4H Close zurueck ueber EMA20
- 4H Close zurueck ueber EMA50
- bullische Reversal-Kerze an Support
- Bruch einer Pullback-Trendlinie mit Close-Bestaetigung

Nicht ausreichend:

- nur Price Touch
- RSI steigt leicht
- MACD Cross ohne Struktur
- gruene Kerze ohne Trigger-Level
- Trigger nach zu starkem Preissprung

### Stop-Logik

Der Stop liegt unter letztem 4H Swing Low, unter Daily Support oder unter EMA50-Zone mit ATR-Puffer. Der Stop darf nicht willkuerlich gesetzt werden.

### Target-Logik

- Target 1: vorheriges Daily Swing High oder 1.5R bis 2R
- Target 2: naechster Daily/Weekly Widerstand, 2.5R bis 3R oder Trailing Stop fuer Restposition

### Invalidation

Das Setup wird ungueltig, wenn Daily Close unter relevantem Support liegt, Daily Close unter EMA50 mit Strukturbruch erfolgt, R:R unter 1:2 faellt, der Preis den Trigger stark ueberschiesst oder der Weekly Kontext bearish wird.

## Strategie B: Base Breakout Long

### Idee

Ein Asset konsolidiert in einer klaren Base oder Range und bricht anschliessend mit Staerke ueber das Base High aus.

### Kontext-Bedingungen

- Weekly Kontext bullish oder neutral-stark
- Daily Close ueber EMA200
- Preis nicht in klarem Abwaertstrend
- Asset liquide genug
- Base nicht direkt unter massivem Widerstand

### Setup-Bedingungen

- mehrere Tage Konsolidierung
- klar erkennbares Base High
- nicht zu weite Range
- EMA20/EMA50 steigend oder stabil
- Volumen trocknet idealerweise in der Base aus
- vorherige Bewegung war konstruktiv
- R:R mindestens 1:2 moeglich

### Trigger

Gueltige Trigger:

- 4H Close ueber Base High
- Daily Close ueber Base High
- Breakout mit Volumenbestaetigung
- Close nahe Tageshoch

Nicht ausreichend:

- kurzer Spike ueber Base High
- Wick ohne Close-Bestaetigung
- Breakout bei sehr niedrigem Volumen
- Trigger nach bereits zu grosser Bewegung

### Stop-Logik

Der Stop liegt unter Breakout-Level mit Puffer, unter Base-Mitte oder unter Base Low bei groesserem Setup.

### Target-Logik

- Target 1: Hoehe der Base nach oben projiziert oder 1.5R bis 2R
- Target 2: naechster Daily/Weekly Widerstand, 2.5R bis 3R oder Trailing Stop

### Invalidation

Das Setup wird ungueltig, wenn der Close zurueck in die Base faellt, Base Low bricht, R:R unter 1:2 faellt, der Breakout zu weit gelaufen ist oder der Weekly Kontext kippt.

## Optional Spaeter: Reclaim Long

Ein Reclaim Long entsteht, wenn ein Asset kurz ein wichtiges Level verliert und es schnell zurueckerobert. Das kann auf einen Shakeout hindeuten. Dieses Setup ist nicht Teil des MVP, weil es mehr Kontext braucht und sonst viele Fehlsignale erzeugt.

## Scoring-System

Der Score bewertet die Setup-Qualitaet. Er ist keine Gewinnwahrscheinlichkeit und keine Handlungsempfehlung.

- Trend: 0 bis 25 Punkte
- Struktur: 0 bis 25 Punkte
- Momentum: 0 bis 15 Punkte
- Volumen: 0 bis 15 Punkte
- Risk/Reward: 0 bis 15 Punkte
- Risiko- und Ausschlussfilter: -20 bis 0 Punkte

Signal-Klassen:

- A-Setup: 80 bis 100 Punkte
- B-Setup: 65 bis 79 Punkte
- Watchlist: 50 bis 64 Punkte
- No Trade: unter 50 Punkte

## No-Trade-Regeln

Kein Long-Trade, wenn:

- R:R unter 1:2 liegt
- Weekly Kontext klar bearish ist
- Preis direkt unter starkem Widerstand steht
- Stop technisch nicht sinnvoll platzierbar ist
- Setup bereits invalidiert wurde
- Kurs zu weit ueber Trigger gelaufen ist
- Asset illiquide ist
- Datenqualitaet schlecht ist
- Preis nach parabolischer Bewegung keinen Pullback hatte
- Risiko durch Volatilitaet unverhaeltnismaessig hoch ist

Fuer Aktien zusaetzlich:

- Earnings-Risiko als harte Warnung
- bei Earnings unmittelbar bevorstehend kein neues Setup ohne manuelle Freigabe

Fuer Krypto zusaetzlich:

- extreme ATR als Warnung
- illiquide Altcoins vermeiden
- starke Wick-Struktur als Risiko-Flag

## Safety Boundaries Fuer Signale Und Alerts

- Signale und Alerts sind Entscheidungshilfe, keine Order-Anweisung.
- `Triggered` bedeutet: manuell pruefen, nicht automatisch handeln.
- `No Setup` und `No Trade` bleiben konservative, vollwertige Ergebnisse.
- Scores bewerten Setup-Qualitaet, nicht Gewinnwahrscheinlichkeit.
- Trade Management Alerts dokumentieren Pruefpunkte und fuehren keine Broker-Aktion aus.

## Alert-System

Alerts bestehen aus Farbe, Status, Prioritaet und Aktion.

Farben:

- Grau: Info
- Gelb: Watch oder Armed
- Gruen: Triggered
- Blau: Management
- Rot: Warning, Exit oder Invalidated

Prioritaeten:

- P1: sofort pruefen
- P2: zeitnah pruefen
- P3: Information

## Alert-Typen

- Info Alert: Grau / P3, Analyse abgeschlossen, kein akuter Handlungsbedarf
- Watchlist Alert: Gelb / P2-P3, Asset wird interessant, noch kein Entry
- Armed Alert: Gelb / P2, Setup vorbereitet, Trigger-Level definiert
- Near Trigger Alert: Gelb / P2, Preis naehert sich Trigger
- Entry Trigger Alert: Gruen / P1, Trigger bestaetigt, Setup manuell pruefen
- Management Alert: Blau / P2, offener Trade benoetigt manuelle Pruefung
- Exit Warning: Rot / P1-P2, Trade-Struktur verschlechtert sich
- Exit Signal: Rot / P1, dokumentierte Ausstiegsregel erreicht
- Invalidation Alert: Rot oder Grau / P2, Setup vor Entry ungueltig

## Telegram-Alert-Format

```text
GRUEN / TRIGGERED / P1
AAPL Long Setup

Strategie:
Trend Pullback Long

Trigger:
4H Close ueber 184.50 bestaetigt

Pruefpunkte:
Entry Zone: 184.50 - 186.00
Stop: 179.80
Target 1: 192.00
Target 2: 198.50
R:R: 2.3

Score:
74/100, B-Setup

Aktion:
Manuell pruefen. Keine automatische Order und keine Kaufanweisung.
```

## Telegram-Routing-Policy Fuer v1.3

Automatische Telegram-Zustellung ist nur fuer ausgewaehlte Review-Ereignisse erlaubt.
Sie darf keine Orders erstellen, keine Trades anlegen und keine Kauf-/Verkaufsanweisung
formulieren. Wenn Policy, Konfiguration oder Datenlage unklar sind, wird nicht gesendet
und das Alert-Event bleibt zur manuellen Pruefung in der App.

### Automatisch Erlaubt

- Near Trigger Alert (`near_trigger`): P2, Preis naehert sich einem vorbereiteten Trigger; manuell pruefen, ob das Setup noch gueltig ist.
- Entry Trigger Alert (`entry_trigger` / `long_entry`): P1, Trigger-Bedingung wurde gemeldet; manuell pruefen, keine Entry-Anweisung.
- Invalidation Alert (`invalidation`): P2, Setup vor Entry moeglicherweise ungueltig; manuell pruefen und ggf. verwerfen.
- Exit Warning (`exit_warning`): P1-P2, offener Trade oder Setup verschlechtert sich; manuell pruefen, keine Exit-Anweisung.

### Manual-Only Oder Geblockt

- Info Alert (`info`): keine automatische Telegram-Zustellung, damit reine Statusmeldungen nicht rauschen.
- Watchlist Alert (`watchlist`): manual-only; noch kein konkreter Trigger.
- Armed Alert (`armed`): manual-only; vorbereitetes Setup, aber kein bestaetigtes Review-Ereignis.
- Management Alert (`management`): manual-only in v1.3, weil Positionsmanagement mehr Kontext braucht.
- Exit Signal (`exit_signal`): manual-only in v1.3, weil die Formulierung sonst zu leicht als Verkaufsanweisung verstanden wird.
- Unbekannte oder nicht gemappte Trigger: geblockt, nicht senden.

### Message-Wording-Regeln

Telegram-Nachrichten muessen review-orientiert formuliert sein:

- Immer enthalten: Symbol, Timeframe, Alert-Typ, Prioritaet, Trigger-Preis oder Referenzlevel falls vorhanden, Zeitstempel und naechster manueller Pruefschritt.
- Immer enthalten: Hinweis `Manual review required. Keine automatische Order. Keine Kauf- oder Verkaufsanweisung.`
- Erlaubte Verben: `pruefen`, `reviewen`, `validieren`, `dokumentieren`, `beobachten`.
- Nicht erlaubt: `kaufen`, `verkaufen`, `einsteigen`, `aussteigen`, `jetzt handeln`, `sicher`, `garantiert`, Gewinn- oder Trefferwahrscheinlichkeiten.
- Scores duerfen nur als Setup-Qualitaet beschrieben werden, nie als Gewinnwahrscheinlichkeit.
- `Triggered` bedeutet nur, dass ein Review-Ereignis eingegangen ist.

### Deduplication Und Rate Limit Erwartungen

v1.3 soll Telegram-Zustellung fail-safe und noise-arm halten:

- Dedup-Key: `symbol + alert_type + timeframe`.
- Innerhalb von 30 Minuten soll pro Dedup-Key hoechstens eine Telegram-Nachricht gesendet werden.
- Wiederholte Webhooks innerhalb des Dedup-Fensters bleiben als Alert-Events speicherbar, sollen aber nicht erneut Telegram senden.
- Burst-Limit: maximal 10 automatische Telegram-Zustellungen pro Nutzer innerhalb von 5 Minuten.
- Bei fehlender Telegram-Konfiguration wird nicht gesendet; das Alert-Event bleibt fuer manuelle Review sichtbar.
- Bei Telegram-Fehlern darf Webhook-Ingestion nicht fehlschlagen, sofern das Alert-Event gespeichert werden konnte.

### Smoke-Test-Evidence Fuer v1.3

Ein v1.3 Smoke Test braucht nicht geheime, bereinigte Evidenz fuer:

- Erlaubtes Event sendet Telegram automatisch, z.B. `near_trigger` oder `entry_trigger`.
- Manual-only Event sendet nicht, z.B. `watchlist`, `armed`, `management` oder `exit_signal`.
- Fehlende oder deaktivierte Telegram-Konfiguration sendet nicht und bleibt sicher.
- Wiederholtes gleiches Event innerhalb von 30 Minuten wird nicht mehrfach gesendet.
- Zustellfehler wird sichtbar dokumentiert, ohne Webhook-Persistenz oder manuelle Review zu blockieren.
- Keine Evidenz enthaelt Telegram Token, Chat IDs, Webhook Secrets oder private Trading-Daten.

## TradingView Webhook Payload

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

Das Backend prueft Secret, Payload, Setup, Symbol, Timeframe, Status, Risk/Reward und ob bereits ein offener Trade existiert.

## Trade Lifecycle

- Scanned: Asset wurde analysiert
- Watchlist: Asset ist interessant, aber noch nicht bereit
- Armed: Setup ist konkret vorbereitet
- Triggered: Trigger wurde bestaetigt, manuelle Pruefung erforderlich
- Entered: Nutzer hat einen extern ausgefuehrten Trade manuell geloggt
- Open: Trade ist aktiv
- Managed: Trade wurde aktiv angepasst
- Exit Warning: Trade verschlechtert sich
- Exit Signal: Ausstiegsregel erreicht
- Closed: Trade wurde beendet
- Reviewed: Trade wurde nachbereitet
- Invalidated: Setup wurde vor Entry ungueltig
- Missed: Trigger wurde ausgelöst, aber Entry verpasst
- Expired: Setup ist zeitlich nicht mehr relevant

## Exit- Und Management-Regeln

Target 1 erreicht:

- Blau / Management / P2
- Teilgewinn 30-50% manuell pruefen
- Stop auf Break-even manuell pruefen
- Restposition laufen lassen

Break-even Regel nach Target 1:

- Stop auf Entry
- oder Stop unter neues 4H Higher Low

Trailing Stop kann liegen:

- unter letztem 4H Higher Low
- unter EMA20/EMA50
- ATR-basiert unter aktuellem Preis
- unter neuer Daily Struktur

Exit Warning Bedingungen:

- 4H Higher Low gebrochen
- Close unter EMA20
- Momentum schwaecht deutlich ab
- Breakout-Level wird erneut getestet
- Volumen steigt beim Abverkauf

Exit Signal Bedingungen:

- Stop Loss erreicht
- Target 2 erreicht
- Daily Close unter letztem Higher Low
- Daily Close unter EMA50 nach Pullback
- Failed Breakout: Close zurueck in Base
- Time Stop: Trade laeuft nach X Kerzen nicht an

## Risk Management

Standardregeln:

- Mindest-R:R: 1:2
- Standard-Risiko pro Trade: 0.5% bis 1.0%
- Max. offene Trades: 3 bis 5 empfohlen

Positionsgroesse:

```text
Risk Amount = Account Size * Risk %
Risk Per Unit = Entry Price - Stop Loss
Position Size = Risk Amount / Risk Per Unit
```

Regel:

- Positionsgroesse folgt dem Stop.
- Stop folgt nicht der gewuenschten Positionsgroesse.

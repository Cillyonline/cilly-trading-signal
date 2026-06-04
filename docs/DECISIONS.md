# Decisions

## Zweck

Dieses Dokument haelt wichtige Produkt-, Trading- und Technikentscheidungen fest. Jede Entscheidung enthaelt Entscheidung, Begruendung, Konsequenz und Status.

## 1. Web-App Statt Lokaler Desktop-App

Status: entschieden

Entscheidung: Das Tool wird zuerst als Web-App gebaut.

Begruendung: Zugriff von ueberall, VPS und Domain sind vorhanden, TradingView Webhooks brauchen einen oeffentlich erreichbaren Endpunkt und PWA/Android-Nutzung wird spaeter einfacher.

Konsequenz: Deployment auf VPS, HTTPS, Login und Sicherheitskonzept sind noetig.

## 2. VPS Deployment

Status: entschieden

Entscheidung: Die App laeuft auf einem eigenen VPS.

Begruendung: VPS ist vorhanden, volle Kontrolle ueber Backend, Datenbank und Webhooks.

Konsequenz: Docker Compose, Reverse Proxy, Backups und Security werden geplant.

## 3. Single-User Zuerst

Status: entschieden

Entscheidung: Version 1 wird fuer einen Single-User gebaut.

Begruendung: weniger Komplexitaet, schnellerer MVP, keine Rollen oder Registrierung noetig.

Konsequenz: kein oeffentlicher Signup, ein Admin-Account, Multi-User spaeter nicht blockieren.

## 4. Deutsch Mit Englischen Fachbegriffen

Status: entschieden

Entscheidung: Dokumentation Deutsch mit englischen Fachbegriffen. Dateinamen, Code, API und Datenbank Englisch. UI startet Deutsch und bleibt i18n-faehig.

Begruendung: Planung bleibt verstaendlich, technische Umsetzung entwicklerfreundlich.

Konsequenz: Code-Objekte heissen z.B. Trade, Signal, Alert, WatchlistItem.

## 5. Long-Only Im Startumfang

Status: entschieden

Entscheidung: Version 1 unterstuetzt nur Long-Setups.

Begruendung: einfacher, stabiler, passend zu Swingtrading und Trade Republic.

Konsequenz: keine Short-Signale im MVP.

## 6. Swingtrading Als Hauptstil

Status: entschieden

Entscheidung: Das Tool wird primaer fuer Swingtrading gebaut.

Begruendung: passt zu 1W/1D/4H, weniger Rauschen, gut mit manueller Ausfuehrung vereinbar.

Konsequenz: kein Fokus auf 5m/15m Scalping.

## 7. Timeframe-Modell 1W / 1D / 4H

Status: entschieden

Entscheidung: 1W Kontext, 1D Setup, 4H Trigger und Management.

Begruendung: professioneller Top-down-Workflow, reduziert Fehlsignale.

Konsequenz: CSV Import und Signal Engine muessen mehrere Timeframes unterscheiden.

## 8. Zwei Kernstrategien Fuer Version 1

Status: entschieden

Entscheidung: Trend Pullback Long und Base Breakout Long.

Begruendung: professionell, erklaerbar, testbar, geeignet fuer Aktien und Krypto.

Konsequenz: Reclaim Long spaeter optional, keine RSI-/MACD-Blindsignale.

## 9. Keine Automatische Orderausfuehrung

Status: entschieden

Entscheidung: Das Tool fuehrt keine Trades automatisch aus.

Begruendung: Sicherheit, Fehlervermeidung, keine Broker API, manuelle Kontrolle bleibt beim Trader.

Konsequenz: Signale sind Entscheidungsunterstuetzung.

## 10. Manuelles Trade Logging

Status: entschieden

Entscheidung: Trades werden in Version 1 manuell erfasst.

Begruendung: Trade Republic wird genutzt, keine Broker-Anbindung geplant, sicherer und schneller.

Konsequenz: Nutzer traegt Entry, Stop, Positionsgroesse und Exit manuell ein.

## 11. TradingView CSV Als Erste Datenquelle

Status: entschieden

Entscheidung: TradingView CSV Upload ist die erste Datenquelle.

Begruendung: messbar, reproduzierbar, testbar, besser als Screenshot-Analyse.

Konsequenz: CSV Import ist MVP-Bestandteil.

## 12. TradingView Webhook Als Alert-Quelle

Status: entschieden fuer MVP+

Entscheidung: TradingView Webhooks werden fuer Trigger Alerts genutzt.

Begruendung: TradingView kann Preis-/Candle-Trigger ueberwachen, Webhooks passen zur VPS-Web-App.

Konsequenz: oeffentlicher HTTPS Webhook-Endpunkt, Secret und standardisierte Payload.

## 13. Telegram Als Erste Notification

Status: entschieden

Entscheidung: Telegram wird als erste Benachrichtigungsloesung genutzt.

Begruendung: einfache Einrichtung, schnelle mobile Push-Nachrichten, gute API.

Konsequenz: eigener Telegram Bot, Token sicher speichern.

## 14. Ampel Plus Status Und Prioritaet

Status: entschieden

Entscheidung: Alerts nutzen ein 5-Farben-System plus Status und Prioritaet.

Farben: Grau, Gelb, Gruen, Blau, Rot.

Prioritaeten: P1, P2, P3.

Begruendung: reine Ampel ist zu grob, Aktion muss klar sein.

Konsequenz: jeder Alert enthaelt Farbe, Status, Prioritaet und Aktion.

## 15. Keine Broker-Anbindung Im MVP

Status: entschieden

Entscheidung: Es gibt keine Broker- oder Exchange-Anbindung im MVP.

Begruendung: reduziert Sicherheitsrisiken, keine API Keys, manuelles Logging reicht.

Konsequenz: offene Trades muessen manuell gepflegt werden.

## 16. Performance In R-Multiples

Status: entschieden

Entscheidung: Performance wird primaer in R-Multiples gemessen.

Begruendung: professionelle Vergleichbarkeit, unabhaengig von Positionsgroesse und Asset.

Konsequenz: jeder Trade braucht Entry, Stop und Positionsgroesse.

## 17. Keine Blackbox-KI

Status: entschieden

Entscheidung: Signale werden regelbasiert und erklaerbar erzeugt.

Begruendung: Trading-Entscheidungen muessen nachvollziehbar, testbar und reviewbar sein.

Konsequenz: Signal Engine basiert auf Regeln, Score und No-Trade-Filtern.

## 18. PWA Vor Native Android

Status: entschieden fuer spaeter

Entscheidung: Mobile Nutzung zuerst ueber responsive Web-App/PWA.

Begruendung: schneller, weniger Aufwand, zentral wartbar.

Konsequenz: UI wird responsive geplant, Telegram bleibt erste Push-Loesung.

## 19. Webhook Sicherheit Mit Secret

Status: entschieden

Entscheidung: TradingView Webhooks werden nur mit Secret akzeptiert.

Begruendung: Endpunkt ist oeffentlich erreichbar und braucht Schutz.

Konsequenz: Payload enthaelt `secret`, Backend lehnt falsche Secrets ab.

## 20. Technische Startentscheidungen

Status: entschieden

Entscheidungen:

- Reverse Proxy: Caddy
- Auth: HttpOnly Cookie Auth
- Frontend: Next.js App Router
- Backend Dependencies: uv
- UI: Tailwind + eigene Komponenten
- Workflow: erst lokal entwickelbar, dann VPS Deployment

Begruendung: sicher, pragmatisch, modern und passend fuer VPS, Webhooks und spaetere PWA.

Konsequenz: Tech Architecture und Implementierung folgen diesen Vorgaben.

## 21. Manueller Provider-Sync Vor Automatischer Marktaktualisierung

Status: entschieden, v4.1 bestaetigt

Entscheidung: Provider-gestuetzte Marktdaten werden zuerst als manueller, disabled-by-default Sync umgesetzt. Der erste praktische Provider-Pfad bleibt Alpha Vantage Daily/EOD hinter einer provider-neutralen Boundary. Eine paid/production-like Provider-Auswahl fuer Twelve Data, Tiingo, Polygon oder EODHD wird vorerst vertagt.

Begruendung: Manuelle Syncs sind pruefbar, testbar und sicherer als Scheduler. Daily/EOD ist der kleinste sinnvolle Provider-Scope. Alpha Vantage ist bereits implementiert und reicht fuer Plumbing-, Freshness- und Fehlerpfad-Smoke. `4H`/Intraday, breitere Watchlists, Speicherung, Lizenz und Rate Limits bleiben provider- und planabhaengig.

Konsequenz: TradingView CSV bleibt Baseline und Fallback, insbesondere fuer `1W`/`1D`/`4H` Vollstaendigkeit. Provider-Daten werden mit Source/Freshness/Sync-Metadaten gespeichert und konservativ bewertet. Es gibt keinen Live-/Realtime-Claim, keine automatische Analyse nach Sync, keine Broker-Anbindung und keine automatische Orderausfuehrung. Secrets, Provider-Accounts und VPS-Konfiguration bleiben ausserhalb dieser Entscheidung.

## 22. Strategie-Kalibrierung Optimiert Signalqualitaet, Nicht Signalmenge

Status: entschieden

Entscheidung: Strategie-Regeln werden ueber einen dokumentierten Kalibrierungsworkflow geaendert: Playbook-Regel definieren, deterministische Golden Cases anlegen, erwartete Labels festlegen, Tests ausfuehren, Regeln konservativ anpassen und Restgaps als Folgeissues dokumentieren.

Begruendung: Ein professionelles Signal-Cockpit soll schwache Setups blockieren, No Trade als Risk-Control akzeptieren und Risiko-/Kontextgruende erklaeren. Mehr Signale sind nur dann wuenschenswert, wenn sie besser zur dokumentierten Strategiequalitaet passen.

Konsequenz: Rule-Loosening ohne Tests/Fixtures ist nicht akzeptiert. Bestandene Kalibrierungstests sind keine Profitabilitaets-, Produktions-, Broker- oder Live-Daten-Aussage und ersetzen keine separate historische oder Paper-Review.

## 23. Too-Strict Findings Rechtfertigen Keine Automatische Lockerung

Status: entschieden

Entscheidung: Wiederholte `too_strict` Findings werden zuerst gegen Golden Cases
und Playbook-Regeln geprueft. In v2.4 bleibt fehlende Trigger-Bestaetigung ein
`Watchlist`-Zustand, waehrend harte Blocker wie schlechte Datenqualitaet,
bearisher Kontext, fehlender Risikoplan, starke Widerstandsnaehe, unkontrollierter
Pullback, zu breite Base, unklarer Base High oder extended Breakout konservativ
blockiert bleiben.

Begruendung: Das System soll lieber weniger, bessere und erklaerbare Review-
Kandidaten liefern. Eine Lockerung nur fuer mehr Signale wuerde No Trade als
Risk-Control schwaechen.

Konsequenz: Loosening braucht einen konkreten Golden Case, coherent Stop/Target/
Invalidation/minimum R:R und darf keine Trading Advice, Profitabilitaets- oder
Ausfuehrungsimplikation erzeugen.

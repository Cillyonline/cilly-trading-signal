# Data Model

## Ziel

Dieses Dokument definiert die wichtigsten Datenobjekte fuer die Trading- und Signal-Web-App.

Das Datenmodell bildet ab:

- Single-User Account
- Watchlist
- Market Data aus TradingView CSV
- technische Indikatoren
- Signale / Setups
- Alerts
- manuell geloggte Trades
- Trade Management Events
- Journal Reviews
- Performance-Auswertung

## Grundprinzipien

- Code, API und Datenbank verwenden englische Namen.
- UI kann deutsche Labels anzeigen.
- Trades werden manuell geloggt.
- Keine Broker-Anbindung im MVP.
- Performance wird primaer in R-Multiples gemessen.
- Signale muessen erklaerbar und nachvollziehbar sein.
- Ein Signal ist nicht automatisch ein Trade.

## Core Entities

MVP:

- User
- Settings
- WatchlistItem
- MarketDataSeries
- MarketDataCandle
- IndicatorSnapshot
- Signal
- Alert
- NotificationLog
- Trade
- TradeEvent
- JournalEntry

MVP+:

- TradingViewWebhookDelivery

Spaeter:

- ScreenerImport
- ScreenerResult
- Attachment
- BrokerConnection
- PerformanceSnapshot

## User

Zweck: Single-User Login im MVP, spaeter Multi-User moeglich.

Felder:

- id
- email
- password_hash
- display_name
- role
- created_at
- updated_at
- last_login_at
- is_active

MVP-Regel: nur ein Admin-User, keine oeffentliche Registrierung.

## Settings

Zweck: Risiko-, Strategie- und Notification-Einstellungen.

Felder:

- id
- user_id
- account_size
- default_risk_percent
- max_risk_percent
- min_risk_reward
- max_open_trades
- base_currency
- telegram_enabled
- telegram_chat_id
- tradingview_webhook_secret
- created_at
- updated_at

Defaults:

- default_risk_percent: 0.5 bis 1.0
- min_risk_reward: 2.0
- max_open_trades: 3 bis 5
- base_currency: EUR

## WatchlistItem

Zweck: beobachtetes Symbol, z.B. `AAPL`, `NVDA`, `BTCUSDT`.

Felder:

- id
- user_id
- symbol
- name
- asset_class
- exchange
- currency
- is_active
- notes
- created_at
- updated_at
- last_analyzed_at

Werte:

- asset_class: stock, crypto

## MarketDataSeries

Zweck: importierter Datensatz fuer Symbol und Timeframe.

Felder:

- id
- watchlist_item_id
- source
- timeframe
- imported_at
- start_time
- end_time
- candle_count
- status
- validation_errors
- file_name
- created_at

Werte:

- source: tradingview_csv, manual, api_later
- timeframe: 1W, 1D, 4H
- status: imported, validated, failed, analyzed

## MarketDataCandle

Zweck: OHLCV-Kerzen.

Felder:

- id
- series_id
- timestamp
- open
- high
- low
- close
- volume
- created_at

Constraint: `series_id + timestamp` muss eindeutig sein.

## IndicatorSnapshot

Zweck: berechnete Indikatoren pro Analysepunkt.

Felder:

- id
- series_id
- timestamp
- ema20
- ema50
- ema200
- rsi14
- atr14
- volume_avg20
- relative_volume
- swing_high
- swing_low
- trend_state
- structure_state
- created_at

Werte:

- trend_state: bullish, neutral, bearish
- structure_state: higher_high_higher_low, range, lower_high_lower_low, unclear

## Signal

Zweck: erkanntes oder manuell gespeichertes Setup. Ein Signal ist kein echter Trade.

Felder:

- id
- user_id
- watchlist_item_id
- strategy_type
- status
- bias
- score
- score_class
- timeframe_context
- timeframe_setup
- timeframe_trigger
- entry_low
- entry_high
- trigger_level
- stop_loss
- target_1
- target_2
- risk_reward
- invalidated_at
- invalidation_reason
- reasoning
- risk_flags
- no_trade_reasons
- next_action
- review_note
- created_at
- updated_at
- triggered_at

Werte:

- strategy_type: trend_pullback_long, base_breakout_long, reclaim_long_later
- status: watchlist, armed, triggered, invalidated, no_setup, missed, expired
- bias: bullish, neutral, bearish
- score_class: a_setup, b_setup, watchlist, no_trade

`reasoning`, `risk_flags` und `no_trade_reasons` koennen als JSON gespeichert werden.
`next_action` speichert den naechsten manuellen Pruefhinweis und ist keine Order-Anweisung.
`review_note` speichert manuelle Review-Notizen des Users und veraendert Strategie-Score oder Setup-Auswertung nicht.

## Alert

Zweck: gespeichertes Benachrichtigungs- oder Review-Ereignis. Ein Alert ist keine Order und fuehrt keinen Trade aus.

Felder:

- id
- user_id
- signal_id
- trade_id
- watchlist_item_id
- alert_type
- status
- priority
- source
- trigger_level
- timeframe
- message
- source_payload
- delivery_status
- delivery_error
- last_triggered_at
- created_at
- updated_at

Werte:

- alert_type: info, watchlist, armed, near_trigger, entry_trigger, management, exit_warning, exit_signal, invalidation
- status: active, triggered, resolved, cancelled, expired
- priority: p1, p2, p3
- source: manual, tradingview_webhook, system
- delivery_status: pending, sent, failed, skipped

`source_payload` speichert validierte Metadaten des Ausloesers, z.B. einen spaeteren TradingView Webhook Payload. Es darf keine Broker-Orderdaten enthalten.

## Trade

Zweck: echter, manuell gestarteter Trade.

Felder:

- id
- user_id
- signal_id
- watchlist_item_id
- status
- strategy_type
- asset_class
- symbol
- entry_price
- stop_loss
- target_1
- target_2
- position_size
- fees
- opened_at
- closed_at
- exit_price
- exit_reason
- initial_risk_amount
- initial_risk_percent
- initial_risk_reward
- result_amount
- result_r
- notes
- created_at
- updated_at

Werte:

- status: open, partial_profit, break_even, exit_warning, exit_signal, closed, reviewed
- exit_reason: stop_loss, target_1, target_2, manual_exit, structure_break, time_stop, failed_breakout, other

## TradeEvent

Zweck: jede wichtige Aktion waehrend eines Trades dokumentieren.

Felder:

- id
- trade_id
- event_type
- event_time
- price
- quantity
- old_value
- new_value
- reason
- notes
- created_at

Werte:

- event_type: opened, stop_updated, target_updated, partial_exit, break_even, trailing_stop, management_alert, exit_warning, exit_signal, closed, note

## JournalEntry

Zweck: Review nach abgeschlossenem Trade.

Felder:

- id
- trade_id
- user_id
- setup_rule_followed
- entry_quality_score
- stop_quality_score
- exit_quality_score
- discipline_score
- market_context
- emotional_notes
- what_went_well
- what_went_wrong
- lesson_learned
- reviewed_at
- created_at
- updated_at

Scores: 1 bis 5.

## NotificationLog

MVP+ fuer Telegram, Discord oder E-Mail.

Felder:

- id
- user_id
- alert_id
- channel
- recipient
- message
- status
- sent_at
- error_message
- provider_payload
- created_at

Werte:

- channel: telegram
- status: pending, sent, failed, skipped

NotificationLog dokumentiert Zustellversuche. Es ist kein Ausfuehrungs- oder Broker-Log.

## Beziehungen

```text
User 1 -> many WatchlistItems
User 1 -> many Signals
User 1 -> many Trades
User 1 -> one Settings

WatchlistItem 1 -> many MarketDataSeries
MarketDataSeries 1 -> many MarketDataCandles
MarketDataSeries 1 -> many IndicatorSnapshots

WatchlistItem 1 -> many Signals
Signal 1 -> many Alerts
Signal 1 -> zero or one Trade

Trade 1 -> many TradeEvents
Trade 1 -> zero or one JournalEntry
Trade 1 -> many Alerts

Alert 1 -> many NotificationLogs
```

## Wichtige Berechnungen

```text
risk_per_unit = entry_price - stop_loss
risk_amount = risk_per_unit * position_size
risk_percent = risk_amount / account_size * 100
risk_reward = (target_price - entry_price) / (entry_price - stop_loss)
result_r = realized_profit_loss / initial_risk_amount
```

## Design-Entscheidungen

Signal und Trade werden getrennt, weil nicht jedes Signal gehandelt wird. TradeEvent wird genutzt, damit Stop-Aenderungen, Teilverkaeufe und Management-Entscheidungen nachvollziehbar bleiben. IndicatorSnapshot wird gespeichert, damit spaeter nachvollziehbar ist, warum ein Signal entstanden ist. R-Multiple ist die Kernmetrik fuer Strategiequalitaet.

## Empfehlungen Fuer Offene Punkte

- OHLCV-Daten dauerhaft speichern, aber pro Symbol/Timeframe ersetzbar machen.
- Fuer MVP IndicatorSnapshot pro Analyse-Endpunkt speichern.
- Signal kann 1W/1D/4H ueber Timeframe-Felder referenzieren.
- Teilverkaeufe ueber TradeEvent speichern.
- Performance live aus Trades berechnen, Snapshots spaeter ergaenzen.

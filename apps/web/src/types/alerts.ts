export type TelegramTestMessageResult = {
  status: string;
  message: string;
};

export type AlertStatus = "active" | "triggered" | "resolved" | "cancelled" | "expired";

export type AlertDeliveryStatus = "pending" | "sent" | "failed" | "skipped";

export type AlertSource = "manual" | "tradingview_webhook" | "system";

export type AlertType =
  | "info"
  | "watchlist"
  | "armed"
  | "near_trigger"
  | "entry_trigger"
  | "management"
  | "exit_warning"
  | "exit_signal"
  | "invalidation";

export type AlertEvent = {
  id: number;
  user_id: number;
  signal_id: number | null;
  trade_id: number | null;
  watchlist_item_id: number | null;
  alert_type: AlertType;
  status: AlertStatus;
  source: AlertSource;
  priority: string;
  trigger_level: string | null;
  timeframe: "1W" | "1D" | "4H" | null;
  message: string | null;
  source_payload: Record<string, unknown> | unknown[] | null;
  delivery_status: AlertDeliveryStatus;
  delivery_error: string | null;
  last_triggered_at: string | null;
  created_at: string;
  updated_at: string;
};

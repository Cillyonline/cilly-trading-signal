import type { AssetClass, StrategyType } from "@/types/signals";

export type TradeStatus = "open" | "partial_profit" | "break_even" | "exit_warning" | "exit_signal" | "closed" | "reviewed";

export type TradeEventType = "note" | "stop_updated" | "target_updated";

export type TradeEvent = {
  id: number;
  trade_id: number;
  event_type: TradeEventType;
  event_time: string;
  price: string | null;
  quantity: string | null;
  old_value: string | null;
  new_value: string | null;
  reason: string | null;
  notes: string | null;
  created_at: string;
};

export type Trade = {
  id: number;
  signal_id: number | null;
  watchlist_item_id: number;
  status: TradeStatus;
  strategy_type: StrategyType;
  asset_class: AssetClass;
  symbol: string;
  entry_price: string;
  stop_loss: string;
  target_1: string | null;
  target_2: string | null;
  position_size: string;
  fees: string | null;
  opened_at: string;
  closed_at: string | null;
  exit_price: string | null;
  risk_per_unit: string;
  initial_risk_amount: string | null;
  initial_risk_percent: string | null;
  initial_risk_reward: string | null;
  target_1_potential_r: string | null;
  target_2_potential_r: string | null;
  result_amount: string | null;
  result_r: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type TradeDetail = Trade & {
  events: TradeEvent[];
};

export type TradeCreatePayload = {
  watchlist_item_id?: number;
  signal_id?: number;
  strategy_type?: StrategyType;
  entry_price: string;
  stop_loss: string;
  target_1?: string | null;
  target_2?: string | null;
  position_size: string;
  fees?: string | null;
  opened_at: string;
  notes?: string | null;
};

export type TradeEventCreatePayload = {
  event_type: TradeEventType;
  event_time: string;
  price?: string | null;
  reason?: string | null;
  notes?: string | null;
};

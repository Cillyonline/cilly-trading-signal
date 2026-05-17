export type SignalStatus = "watchlist" | "armed" | "triggered" | "invalidated" | "no_setup" | "missed" | "expired";

export type ScoreClass = "a_setup" | "b_setup" | "watchlist" | "no_trade";

export type Bias = "bullish" | "neutral" | "bearish";

export type StrategyType = "trend_pullback_long" | "base_breakout_long";

export type Timeframe = "1W" | "1D" | "4H";

export type AssetClass = "stock" | "crypto";

export type Signal = {
  id: number;
  watchlist_item_id: number;
  symbol: string;
  asset_class: AssetClass;
  exchange: string | null;
  strategy_type: StrategyType;
  status: SignalStatus;
  bias: Bias;
  score: number | null;
  score_class: ScoreClass | null;
  timeframe_context: Timeframe | null;
  timeframe_setup: Timeframe | null;
  timeframe_trigger: Timeframe | null;
  entry_low: string | null;
  entry_high: string | null;
  trigger_level: string | null;
  stop_loss: string | null;
  target_1: string | null;
  target_2: string | null;
  risk_reward: string | null;
  invalidation_reason: string | null;
  reasoning: string[] | Record<string, unknown> | null;
  risk_flags: string[] | Record<string, unknown> | null;
  no_trade_reasons: string[] | Record<string, unknown> | null;
  next_action: string | null;
  review_note: string | null;
  created_at: string;
  updated_at: string;
  triggered_at: string | null;
};

export type SignalStatusUpdatePayload = {
  status: SignalStatus;
};

export type SignalReviewNoteUpdatePayload = {
  review_note: string | null;
};

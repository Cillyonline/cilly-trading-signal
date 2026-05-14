export type Timeframe = "1W" | "1D" | "4H";

export type MarketDataStatus = "imported" | "validated" | "failed" | "analyzed";

export type SignalStatus = "watchlist" | "armed" | "triggered" | "invalidated" | "no_setup" | "missed" | "expired";

export type ScoreClass = "a_setup" | "b_setup" | "watchlist" | "no_trade";

export type Bias = "bullish" | "neutral" | "bearish";

export type StrategyType = "trend_pullback_long" | "base_breakout_long";

export type CsvImportError = {
  row: number | null;
  field: string | null;
  message: string;
};

export type CsvImportResult = {
  series_id: number | null;
  watchlist_item_id: number;
  timeframe: Timeframe;
  status: MarketDataStatus;
  candle_count: number;
  start_time: string | null;
  end_time: string | null;
  errors: CsvImportError[];
};

export type SignalAnalysisResult = {
  strategy_type: StrategyType;
  status: SignalStatus;
  bias: Bias;
  score: number;
  score_class: ScoreClass;
  timeframe_context: Timeframe;
  timeframe_setup: Timeframe;
  timeframe_trigger: Timeframe;
  entry_low: string | null;
  entry_high: string | null;
  trigger_level: string | null;
  stop_loss: string | null;
  target_1: string | null;
  target_2: string | null;
  risk_reward: string | null;
  invalidation_reason: string | null;
  reasoning: string[];
  risk_flags: string[];
  next_action: string;
  no_trade_reasons: string[];
};

export type MarketDataAnalysisResult = {
  series_id: number;
  status: MarketDataStatus;
  candle_count: number;
  indicator_snapshot_count: number;
  signal: SignalAnalysisResult;
};

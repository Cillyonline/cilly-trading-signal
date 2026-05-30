export type Timeframe = "1W" | "1D" | "4H";

export type MarketDataStatus = "imported" | "validated" | "failed" | "analyzed";

export type MarketDataSource = "tradingview_csv" | "manual" | "api_later" | "provider" | "unknown";

export type MarketDataFreshnessStatus = "fresh" | "stale" | "unknown" | "failed" | "partial";

export type MarketDataSyncStatus = "not_applicable" | "success" | "skipped" | "failed" | "partial";

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
  source: MarketDataSource;
  freshness_status: MarketDataFreshnessStatus;
  sync_status: MarketDataSyncStatus;
  last_synced_at: string | null;
  errors: CsvImportError[];
};

export type ImportHistoryItem = {
  series_id: number;
  watchlist_item_id: number;
  symbol: string;
  timeframe: Timeframe;
  status: MarketDataStatus;
  candle_count: number;
  start_time: string | null;
  end_time: string | null;
  imported_at: string;
  source: MarketDataSource;
  freshness_status: MarketDataFreshnessStatus;
  sync_status: MarketDataSyncStatus;
  last_synced_at: string | null;
  provider_name: string | null;
  file_name: string | null;
};

export type MarketDataSyncRequest = {
  watchlist_item_id: number;
  timeframe: Timeframe;
};

export type MarketDataSyncResult = {
  watchlist_item_id: number;
  series_id: number;
  source: MarketDataSource;
  timeframe: Timeframe;
  provider_name: string | null;
  provider_symbol: string | null;
  provider_exchange: string | null;
  provider_timeframe: string | null;
  sync_status: MarketDataSyncStatus;
  freshness_status: MarketDataFreshnessStatus;
  last_synced_at: string | null;
  end_time: string | null;
  sync_error_code: string | null;
  sync_error_message: string | null;
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
  quality_report: AnalysisQualityCheck[];
};

export type AnalysisQualityCheck = {
  key: string;
  label: string;
  status: "passed" | "warning" | "blocked" | "missing" | string;
  detail: string;
};

export type MarketDataAnalysisResult = {
  series_id: number;
  status: MarketDataStatus;
  candle_count: number;
  indicator_snapshot_count: number;
  signal: SignalAnalysisResult;
};

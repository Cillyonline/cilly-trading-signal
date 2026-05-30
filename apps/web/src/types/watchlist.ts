export type AssetClass = "stock" | "crypto";

export type Timeframe = "1W" | "1D" | "4H";

export type MarketDataSource = "tradingview_csv" | "manual" | "api_later" | "provider" | "unknown";

export type MarketDataFreshnessStatus = "fresh" | "stale" | "unknown" | "failed" | "partial";

export type MarketDataSyncStatus = "not_applicable" | "success" | "skipped" | "failed" | "partial";

export type WatchlistMarketDataSummary = {
  series_id: number;
  source: MarketDataSource;
  freshness_status: MarketDataFreshnessStatus;
  sync_status: MarketDataSyncStatus;
  timeframe: Timeframe;
  end_time: string | null;
  imported_at: string;
  last_synced_at: string | null;
  provider_name: string | null;
};

export type WatchlistItem = {
  id: number;
  symbol: string;
  name: string | null;
  asset_class: AssetClass;
  exchange: string | null;
  currency: string | null;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
  last_analyzed_at: string | null;
  latest_market_data: WatchlistMarketDataSummary | null;
};

export type BenchmarkRequirementStatus = {
  key: string;
  accepted_symbols: string[];
  status: string;
  present_symbol: string | null;
  latest_daily_freshness: MarketDataFreshnessStatus | null;
  message: string;
};

export type BenchmarkContextStatus = {
  asset_class: AssetClass;
  requirements: BenchmarkRequirementStatus[];
  guidance: string;
};

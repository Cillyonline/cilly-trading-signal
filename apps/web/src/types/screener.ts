import type { AssetClass } from "@/types/signals";

export type ScreenerImportSource = "tradingview_screener_csv";

export type ScreenerImportStatus = "pending" | "validated" | "failed" | "imported" | "partial";

export type ScreenerResultStatus = "candidate" | "watchlist_added" | "duplicate" | "rejected" | "ignored";

export type ScreenerResultSortBy =
  | "created_at"
  | "symbol"
  | "status"
  | "volume"
  | "relative_volume"
  | "rsi14"
  | "price"
  | "rank";

export type ScreenerResultSortDirection = "asc" | "desc";

export type ScreenerResultFilters = {
  asset_class?: AssetClass | "";
  status?: ScreenerResultStatus | "";
  exchange?: string;
  screener_import_id?: number | "";
  min_volume?: string;
  min_relative_volume?: string;
  min_rsi14?: string;
  max_rsi14?: string;
  sort_by?: ScreenerResultSortBy;
  sort_direction?: ScreenerResultSortDirection;
  page?: number;
  page_size?: number;
};

export type ScreenerResultPage = {
  items: ScreenerResult[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

export type ScreenerResultBulkStatusPayload = {
  result_ids: number[];
  status: "candidate" | "ignored" | "rejected";
};

export type ScreenerResultBulkStatusResult = {
  requested_count: number;
  updated_count: number;
  skipped_count: number;
  skipped_result_ids: number[];
  results: ScreenerResult[];
};

export type ScreenerImportError = {
  row: number | null;
  field: string | null;
  message: string;
};

export type ScreenerImport = {
  id: number;
  user_id: number;
  source: ScreenerImportSource;
  file_name: string | null;
  asset_class: AssetClass;
  screener_preset: string | null;
  snapshot_at: string | null;
  row_count: number;
  accepted_count: number;
  rejected_count: number;
  duplicate_count: number;
  status: ScreenerImportStatus;
  validation_errors: ScreenerImportError[] | Record<string, unknown> | null;
  created_at: string;
};

export type ScreenerResult = {
  id: number;
  screener_import_id: number;
  user_id: number;
  watchlist_item_id: number | null;
  symbol: string;
  name: string | null;
  asset_class: AssetClass;
  exchange: string | null;
  currency: string | null;
  sector: string | null;
  industry: string | null;
  price: string | null;
  change_percent: string | null;
  volume: string | null;
  relative_volume: string | null;
  market_cap: string | null;
  rsi14: string | null;
  ema20: string | null;
  ema50: string | null;
  ema200: string | null;
  rank: number | null;
  status: ScreenerResultStatus;
  duplicate_of_result_id: number | null;
  validation_errors: ScreenerImportError[] | Record<string, unknown> | null;
  raw_metadata: Record<string, unknown> | unknown[] | null;
  created_at: string;
  updated_at: string;
};

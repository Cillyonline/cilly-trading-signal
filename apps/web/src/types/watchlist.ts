export type AssetClass = "stock" | "crypto";

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
};

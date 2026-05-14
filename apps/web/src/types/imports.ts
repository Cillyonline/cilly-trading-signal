export type Timeframe = "1W" | "1D" | "4H";

export type MarketDataStatus = "imported" | "validated" | "failed" | "analyzed";

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

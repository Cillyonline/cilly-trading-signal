export type PerformanceByStrategy = {
  strategy_type: string;
  closed_trade_count: number;
  total_r: string;
  average_r: string | null;
  win_rate: string | null;
};

export type PerformanceSummary = {
  closed_trade_count: number;
  total_r: string;
  average_r: string | null;
  win_rate: string | null;
  best_r: string | null;
  worst_r: string | null;
  by_strategy: PerformanceByStrategy[];
};

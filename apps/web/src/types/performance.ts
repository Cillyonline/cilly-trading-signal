export type PerformanceByStrategy = {
  strategy_type: string;
  closed_trade_count: number;
  total_r: string;
  average_r: string | null;
  win_rate: string | null;
};

export type PerformanceByAssetClass = {
  asset_class: string;
  closed_trade_count: number;
  total_r: string;
  average_r: string | null;
  win_rate: string | null;
};

export type OpenRiskGroup = {
  group: string;
  open_trade_count: number;
  documented_initial_risk_amount: string;
  documented_initial_risk_percent: string;
  incomplete_risk_count: number;
};

export type OpenPortfolioRisk = {
  open_trade_count: number;
  complete_risk_count: number;
  incomplete_risk_count: number;
  documented_initial_risk_amount: string;
  documented_initial_risk_percent: string;
  by_strategy: OpenRiskGroup[];
  by_asset_class: OpenRiskGroup[];
  review_only_notice: string;
};

export type PerformanceSummary = {
  closed_trade_count: number;
  total_r: string;
  average_r: string | null;
  win_rate: string | null;
  best_r: string | null;
  worst_r: string | null;
  by_strategy: PerformanceByStrategy[];
  by_asset_class: PerformanceByAssetClass[];
  open_portfolio_risk: OpenPortfolioRisk;
};

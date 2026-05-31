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

export type ConcentrationGroup = {
  group: string;
  open_trade_count: number;
  open_trade_percent: string;
  warning: boolean;
};

export type AssetConcentration = {
  warning_status: "ok" | "warning";
  warning_threshold_percent: string;
  warnings: string[];
  by_asset_class: ConcentrationGroup[];
  by_symbol: ConcentrationGroup[];
  by_sector: ConcentrationGroup[];
  by_industry: ConcentrationGroup[];
  review_only_notice: string;
};

export type CorrelationProxy = {
  key: string;
  label: string;
  status: "ok" | "unknown" | "warning";
  open_trade_count: number;
  symbols: string[];
  message: string;
};

export type CorrelationProxySummary = {
  warning_status: "ok" | "unknown" | "warning";
  warnings: CorrelationProxy[];
  review_only_notice: string;
};

export type JournalScoreSummary = {
  average_entry_quality_score: string | null;
  average_stop_quality_score: string | null;
  average_exit_quality_score: string | null;
  average_discipline_score: string | null;
};

export type JournalStrategySummary = JournalScoreSummary & {
  strategy_type: string;
  reviewed_trade_count: number;
  setup_rule_followed_count: number;
  setup_rule_broken_count: number;
  setup_rule_unknown_count: number;
};

export type JournalAnalytics = JournalScoreSummary & {
  closed_trade_count: number;
  reviewed_trade_count: number;
  missing_review_count: number;
  setup_rule_followed_count: number;
  setup_rule_broken_count: number;
  setup_rule_unknown_count: number;
  min_strategy_sample_size: number;
  by_strategy: JournalStrategySummary[];
  small_sample_notice: string;
};

export type OpenPortfolioRisk = {
  open_trade_count: number;
  complete_risk_count: number;
  incomplete_risk_count: number;
  documented_initial_risk_amount: string;
  documented_initial_risk_percent: string;
  max_risk_percent: string;
  warning_status: "ok" | "unknown" | "warning";
  warnings: string[];
  asset_concentration: AssetConcentration;
  correlation_proxies: CorrelationProxySummary;
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
  journal_analytics: JournalAnalytics;
};

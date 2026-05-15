export type RiskSettings = {
  account_size: string | null;
  default_risk_percent: string;
  max_risk_percent: string;
  min_risk_reward: string;
  max_open_trades: number;
  base_currency: string;
};

export type RiskSettingsUpdatePayload = {
  account_size?: string | null;
  default_risk_percent?: string | null;
  max_risk_percent?: string | null;
  min_risk_reward?: string | null;
  max_open_trades?: number | null;
  base_currency?: string | null;
};

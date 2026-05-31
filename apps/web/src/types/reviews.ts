import type { AssetClass, ScoreClass, SignalStatus, StrategyType } from "@/types/signals";

export type ReviewBatchType = "historical" | "paper";

export type ManualReviewLabel = "useful" | "too_permissive" | "too_strict" | "unclear";

export type ReviewBatch = {
  id: number;
  name: string;
  review_type: ReviewBatchType;
  description: string | null;
  asset_class: AssetClass | null;
  strategy_type: StrategyType | null;
  review_window_start: string | null;
  review_window_end: string | null;
  data_source: string | null;
  context_notes: string | null;
  created_at: string;
  updated_at: string;
  entries: ReviewEntry[];
  summary: ReviewBatchSummary;
};

export type ReviewEntry = {
  id: number;
  batch_id: number;
  signal_id: number | null;
  symbol: string;
  asset_class: AssetClass;
  strategy_type: StrategyType;
  stored_data_start: string | null;
  stored_data_end: string | null;
  benchmark_context: string | null;
  signal_status: SignalStatus;
  score_class: ScoreClass | null;
  no_trade_reasons: unknown[] | Record<string, unknown> | null;
  risk_flags: unknown[] | Record<string, unknown> | null;
  quality_blockers: unknown[] | Record<string, unknown> | null;
  entry_price: string | null;
  stop_loss: string | null;
  target_price: string | null;
  planned_risk_reward: string | null;
  manual_review_label: ManualReviewLabel;
  outcome_r: string | null;
  outcome_measurement_rule: string | null;
  follow_up_needed: boolean;
  follow_up_issue_url: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type ReviewBatchSummary = {
  reviewed_count: number;
  label_counts: Record<string, number>;
  follow_up_needed_count: number;
  repeated_attention_labels: string[];
  repeated_blocker_patterns: string[];
  finding_category_counts: Record<string, number>;
  repeated_finding_categories: string[];
  evidence_only_notice: string;
};

export type ReviewBatchCreatePayload = {
  name: string;
  review_type: ReviewBatchType;
  description?: string | null;
  asset_class?: AssetClass | null;
  strategy_type?: StrategyType | null;
  review_window_start?: string | null;
  review_window_end?: string | null;
  data_source?: string | null;
  context_notes?: string | null;
};

export type ReviewEntryCreatePayload = {
  signal_id?: number | null;
  symbol: string;
  asset_class: AssetClass;
  strategy_type: StrategyType;
  stored_data_start?: string | null;
  stored_data_end?: string | null;
  benchmark_context?: string | null;
  signal_status: SignalStatus;
  score_class?: ScoreClass | null;
  quality_blockers?: string[];
  manual_review_label: ManualReviewLabel;
  outcome_r?: string | null;
  outcome_measurement_rule?: string | null;
  follow_up_needed?: boolean;
  follow_up_issue_url?: string | null;
  notes?: string | null;
};

export type ReviewEntryUpdatePayload = ReviewEntryCreatePayload;

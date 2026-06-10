import type { AnalysisQualityCheck, ScoreClass, SignalStatus } from "@/types/signals";

export type SignalDecisionKind = "paper_candidate" | "observe" | "no_trade" | "data_problem";
export type SignalDecisionTone = "green" | "yellow" | "red" | "gray";

export type SignalDecisionInput = {
  status: SignalStatus;
  score: number | null;
  score_class: ScoreClass | null;
  risk_reward: string | number | null;
  risk_flags: string[] | Record<string, unknown> | null;
  no_trade_reasons: string[] | Record<string, unknown> | null;
  quality_report: AnalysisQualityCheck[];
  is_stale?: boolean;
};

export type SignalDecisionLike = {
  status: string;
  score: number | null;
  score_class: string | null;
  risk_reward: string | number | null;
  risk_flags: string[] | Record<string, unknown> | null;
  no_trade_reasons: string[] | Record<string, unknown> | null;
  quality_report: AnalysisQualityCheck[];
  is_stale?: boolean;
};

export type SignalDecision = {
  kind: SignalDecisionKind;
  tone: SignalDecisionTone;
  label: string;
  quality: "Stark" | "Mittel" | "Schwach" | "Nicht bewertbar";
  headline: string;
  action: string;
  reasons: string[];
  priority: number;
};

const DATA_QUALITY_REASONS = new Set([
  "poor_data_quality",
  "required_timeframe_data_missing",
  "required_market_data_not_fresh",
  "insufficient_candle_history",
  "required_indicator_missing",
  "missing_stop_loss",
  "missing_reward_target",
]);

const TECHNICAL_TEXT: Record<string, string> = {
  stock_market_regime_bearish: "Das Marktumfeld blockiert Long-Setups.",
  crypto_regime_bearish: "Das Krypto-Marktumfeld blockiert Long-Setups.",
  weekly_context_bearish: "Der uebergeordnete Wochen-Trend ist zu schwach.",
  daily_context_bearish: "Der Tages-Trend ist zu schwach.",
  pullback_not_controlled: "Der Ruecksetzer ist nicht kontrolliert genug.",
  pullback_volume_aggressive: "Das Volumen im Ruecksetzer ist zu aggressiv.",
  base_too_wide: "Die Basis ist zu breit und damit unsauber.",
  breakout_too_extended: "Der Ausbruch ist bereits zu weit gelaufen.",
  base_high_not_clear: "Die Ausbruchsmarke ist nicht klar genug.",
  strong_resistance_nearby: "Nahe Widerstaende schwaechen das Setup.",
  setup_already_invalidated: "Das Setup ist bereits ungueltig.",
  relative_strength_underperforming: "Relative Staerke reicht nicht aus.",
  stock_market_regime_mixed: "Das Marktumfeld ist gemischt.",
  stock_benchmark_context_missing: "Benchmark-Kontext fehlt.",
  stock_benchmark_context_stale: "Benchmark-Kontext ist veraltet.",
  stock_benchmark_context_unknown: "Benchmark-Kontext ist unklar.",
  relative_strength_unavailable: "Relative Staerke muss manuell geprueft werden.",
  relative_strength_lagging: "Relative Staerke ist nur schwach.",
  liquidity_unconfirmed: "Liquiditaet ist nicht ausreichend bestaetigt.",
  price_touch_without_close_confirmation: "Es fehlt eine saubere Schlusskurs-Bestaetigung.",
  wick_without_close_confirmation: "Nur ein Docht, noch keine Schlusskurs-Bestaetigung.",
  aggressive_pullback_volume: "Volumen schwaecht die Pullback-Qualitaet.",
  base_volume_not_drying_up: "Volumen trocknet in der Basis nicht sauber aus.",
  required_timeframe_data_missing: "Mindestens ein benoetigter Timeframe fehlt.",
  required_market_data_not_fresh: "Marktdaten sind nicht aktuell genug.",
  required_indicator_missing: "Ein benoetigter Indikator fehlt.",
  insufficient_candle_history: "Die Historie reicht fuer eine saubere Analyse nicht aus.",
  missing_stop_loss: "Der Risikoplan ist unvollstaendig: Stop fehlt.",
  missing_reward_target: "Der Risikoplan ist unvollstaendig: Ziel fehlt.",
  poor_data_quality: "Die Datenqualitaet reicht nicht aus.",
};

export function buildSignalDecision(input: SignalDecisionLike): SignalDecision {
  const riskFlags = normalizeTextList(input.risk_flags);
  const noTradeReasons = normalizeTextList(input.no_trade_reasons);
  const hasDataProblem = hasBlockingDataProblem(input, riskFlags, noTradeReasons);
  const hasNoTrade =
    noTradeReasons.length > 0 ||
    input.score_class === "no_trade" ||
    input.status === "no_setup" ||
    input.status === "invalidated" ||
    input.status === "missed" ||
    input.status === "expired";

  if (hasDataProblem) {
    return {
      kind: "data_problem",
      tone: "gray",
      label: "Datenproblem",
      quality: "Nicht bewertbar",
      headline: "Analyse nicht sauber genug.",
      action: "Daten aktualisieren oder fehlende Timeframes importieren. Kein Trade.",
      reasons: decisionReasons(input, riskFlags, noTradeReasons, ["Datenbasis ist unvollstaendig oder veraltet."]),
      priority: 3,
    };
  }

  if (hasNoTrade) {
    return {
      kind: "no_trade",
      tone: "red",
      label: "Kein Trade",
      quality: "Schwach",
      headline: "Setup aussortieren.",
      action: "Nicht handeln und nicht als Paper-Trade erfassen. Spaeter neu pruefen.",
      reasons: decisionReasons(input, riskFlags, noTradeReasons, ["Mindestens ein Pflichtfilter blockiert das Setup."]),
      priority: 2,
    };
  }

  if (input.status === "triggered" || (input.status === "armed" && input.score_class === "a_setup")) {
    return {
      kind: "paper_candidate",
      tone: "green",
      label: "Paper-Kandidat",
      quality: "Stark",
      headline: "Setup ist fuer manuelle Paper-Pruefung bereit.",
      action: "Nur manuell pruefen. Keine automatische Order und keine echte Ausfuehrung.",
      reasons: decisionReasons(input, riskFlags, noTradeReasons, ["Trend, Setup und Risikoplan sind grundsaetzlich stimmig."]),
      priority: 0,
    };
  }

  return {
    kind: "observe",
    tone: "yellow",
    label: "Beobachten",
    quality: input.score_class === "b_setup" ? "Mittel" : "Schwach",
    headline: "Interessant, aber noch nicht stark genug.",
    action: "Weiter beobachten und erst bei klarerer Bestaetigung manuell pruefen.",
    reasons: decisionReasons(input, riskFlags, noTradeReasons, ["Setup ist noch nicht eindeutig genug."]),
    priority: 1,
  };
}

export function signalDecisionToneClass(tone: SignalDecisionTone): string {
  if (tone === "green") {
    return "border-emerald-300/40 bg-emerald-300/10 text-emerald-100";
  }
  if (tone === "yellow") {
    return "border-yellow-300/40 bg-yellow-300/10 text-yellow-100";
  }
  if (tone === "red") {
    return "border-red-300/40 bg-red-300/10 text-red-100";
  }
  return "border-slate-400/40 bg-slate-400/10 text-slate-100";
}

export function signalDecisionDotClass(tone: SignalDecisionTone): string {
  if (tone === "green") {
    return "bg-emerald-300";
  }
  if (tone === "yellow") {
    return "bg-yellow-300";
  }
  if (tone === "red") {
    return "bg-red-300";
  }
  return "bg-slate-300";
}

function hasBlockingDataProblem(
  input: SignalDecisionLike,
  riskFlags: string[],
  noTradeReasons: string[],
): boolean {
  if (input.is_stale) {
    return true;
  }
  if (noTradeReasons.some((reason) => DATA_QUALITY_REASONS.has(reason))) {
    return true;
  }
  return input.quality_report.some(
    (check) =>
      check.key === "data_quality" &&
      check.status === "blocked",
  );
}

function decisionReasons(
  input: SignalDecisionLike,
  riskFlags: string[],
  noTradeReasons: string[],
  fallback: string[],
): string[] {
  const translated = [...noTradeReasons, ...riskFlags]
    .map((item) => TECHNICAL_TEXT[item] ?? null)
    .filter((item): item is string => Boolean(item));
  const qualityReasons = input.quality_report
    .filter((check) => check.status === "blocked" || check.status === "warning" || check.status === "missing")
    .map((check) => translateQualityCheck(check));
  const reasons = uniqueText([...translated, ...qualityReasons]);
  return (reasons.length > 0 ? reasons : fallback).slice(0, 3);
}

function translateQualityCheck(check: AnalysisQualityCheck): string {
  const key = `${check.key}:${check.status}`;
  const translations: Record<string, string> = {
    "market_regime:blocked": "Das Marktumfeld blockiert Long-Setups.",
    "market_regime:warning": "Das Marktumfeld ist unklar oder gemischt.",
    "asset_overlay:blocked": "Asset-spezifische Filter blockieren das Setup.",
    "asset_overlay:warning": "Asset-spezifische Filter brauchen manuelle Pruefung.",
    "trend:blocked": "Der Trend ist nicht stark genug.",
    "structure:blocked": "Die Struktur ist nicht sauber genug.",
    "trigger:blocked": "Der Trigger ist qualitativ blockiert.",
    "trigger:warning": "Der Trigger braucht noch eine saubere Bestaetigung.",
    "trigger:missing": "Trigger-Bestaetigung fehlt noch.",
    "volume:warning": "Volumen schwaecht die Setup-Qualitaet.",
    "risk_plan:blocked": "Der Risikoplan ist nicht vollstaendig oder zu schwach.",
    "risk_plan:missing": "Der Risikoplan ist noch nicht vollstaendig.",
    "data_quality:blocked": "Die Datenbasis blockiert eine saubere Analyse.",
    "data_quality:warning": "Ein Teil der Datenbasis braucht manuelle Pruefung.",
  };
  return translations[key] ?? check.detail;
}

function normalizeTextList(value: string[] | Record<string, unknown> | null): string[] {
  return Array.isArray(value) ? value.map(String) : [];
}

function uniqueText(values: string[]): string[] {
  return values.filter((value, index) => values.indexOf(value) === index);
}

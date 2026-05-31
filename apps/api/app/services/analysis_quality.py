from dataclasses import dataclass
from decimal import Decimal

from app.models.enums import SignalStatus


@dataclass(frozen=True)
class AnalysisQualityCheck:
    key: str
    label: str
    status: str
    detail: str


BLOCKED_REASONS = {
    "stock_market_regime_bearish",
    "crypto_regime_bearish",
    "weekly_context_bearish",
    "daily_context_bearish",
}
MISSING_DATA_REASONS = {
    "poor_data_quality",
    "missing_stop_loss",
    "missing_reward_target",
}
STRUCTURE_BLOCKERS = {
    "pullback_not_controlled",
    "base_too_wide",
    "base_high_not_clear",
    "strong_resistance_nearby",
    "setup_already_invalidated",
}
TRIGGER_BLOCKERS = {
    "breakout_too_extended",
}
REGIME_FLAGS = {
    "stock_benchmark_context_missing",
    "stock_benchmark_context_stale",
    "stock_benchmark_context_unknown",
    "stock_benchmark_context_failed",
    "stock_benchmark_context_partial",
    "stock_market_regime_mixed",
    "crypto_regime_context_missing",
    "crypto_regime_context_stale",
    "crypto_regime_context_unknown",
    "crypto_regime_context_failed",
    "crypto_regime_context_partial",
    "crypto_regime_mixed",
}
ASSET_FLAGS = {
    "relative_strength_unavailable",
    "relative_strength_lagging",
    "relative_strength_underperforming",
    "liquidity_unconfirmed",
}
TRIGGER_FLAGS = {
    "price_touch_without_close_confirmation",
    "wick_without_close_confirmation",
}
VOLUME_FLAGS = {
    "aggressive_pullback_volume",
    "base_volume_not_drying_up",
}


def build_analysis_quality_report(signal: object) -> list[dict[str, str]]:
    risk_flags = normalize_list(getattr(signal, "risk_flags", None))
    no_trade_reasons = normalize_list(getattr(signal, "no_trade_reasons", None))
    checks = [
        market_regime_check(risk_flags, no_trade_reasons),
        asset_overlay_check(risk_flags, no_trade_reasons),
        trend_check(no_trade_reasons),
        structure_check(no_trade_reasons),
        trigger_check(signal, risk_flags, no_trade_reasons),
        volume_check(risk_flags),
        risk_plan_check(signal, no_trade_reasons),
        data_quality_check(risk_flags, no_trade_reasons),
    ]
    return [check.__dict__ for check in checks]


def market_regime_check(
    risk_flags: list[str], no_trade_reasons: list[str]
) -> AnalysisQualityCheck:
    if any(reason in BLOCKED_REASONS for reason in no_trade_reasons):
        return check("market_regime", "Market regime", "blocked", "Regime blocks long-only review.")
    if any(flag in REGIME_FLAGS for flag in risk_flags):
        return check(
            "market_regime", "Market regime", "warning", "Regime context is missing or mixed."
        )
    return check("market_regime", "Market regime", "passed", "No regime blocker is active.")


def asset_overlay_check(
    risk_flags: list[str], no_trade_reasons: list[str]
) -> AnalysisQualityCheck:
    if "relative_strength_underperforming" in no_trade_reasons:
        return check(
            "asset_overlay", "Asset overlay", "blocked", "Relative strength blocks review."
        )
    if any(flag in ASSET_FLAGS for flag in risk_flags):
        return check(
            "asset_overlay", "Asset overlay", "warning", "Asset overlay needs manual scrutiny."
        )
    return check("asset_overlay", "Asset overlay", "passed", "No asset-specific blocker is active.")


def trend_check(no_trade_reasons: list[str]) -> AnalysisQualityCheck:
    if "weekly_context_bearish" in no_trade_reasons or "daily_context_bearish" in no_trade_reasons:
        return check("trend", "Trend", "blocked", "Trend context is bearish.")
    return check("trend", "Trend", "passed", "Trend context is not blocking the setup.")


def structure_check(no_trade_reasons: list[str]) -> AnalysisQualityCheck:
    if any(reason in STRUCTURE_BLOCKERS for reason in no_trade_reasons):
        return check("structure", "Structure", "blocked", "Structure is not clean enough.")
    return check("structure", "Structure", "passed", "No structure blocker is active.")


def trigger_check(
    signal: object, risk_flags: list[str], no_trade_reasons: list[str]
) -> AnalysisQualityCheck:
    if any(reason in TRIGGER_BLOCKERS for reason in no_trade_reasons):
        return check("trigger", "Trigger", "blocked", "Trigger quality is blocked.")
    if any(flag in TRIGGER_FLAGS for flag in risk_flags):
        return check("trigger", "Trigger", "warning", "Trigger lacks clean close confirmation.")
    if getattr(signal, "status", None) == SignalStatus.ARMED:
        return check("trigger", "Trigger", "passed", "Trigger plan is reviewable.")
    return check("trigger", "Trigger", "missing", "Trigger confirmation is not complete yet.")


def volume_check(risk_flags: list[str]) -> AnalysisQualityCheck:
    if any(flag in VOLUME_FLAGS for flag in risk_flags):
        return check("volume", "Volume", "warning", "Volume weakens setup quality.")
    return check("volume", "Volume", "passed", "No volume warning is active.")


def risk_plan_check(signal: object, no_trade_reasons: list[str]) -> AnalysisQualityCheck:
    if any(reason in MISSING_DATA_REASONS for reason in no_trade_reasons):
        return check("risk_plan", "Risk plan", "blocked", "Risk plan is incomplete.")
    risk_reward = getattr(signal, "risk_reward", None)
    if risk_reward is None:
        return check("risk_plan", "Risk plan", "missing", "R:R is not available yet.")
    if Decimal(str(risk_reward)) < Decimal("2"):
        return check("risk_plan", "Risk plan", "blocked", "R:R is below 2R.")
    return check("risk_plan", "Risk plan", "passed", "Risk plan meets minimum R:R.")


def data_quality_check(risk_flags: list[str], no_trade_reasons: list[str]) -> AnalysisQualityCheck:
    if "poor_data_quality" in no_trade_reasons:
        return check(
            "data_quality", "Data quality", "blocked", "Required data is missing or stale."
        )
    missing_flags = [flag for flag in risk_flags if "missing" in flag or "stale" in flag]
    if missing_flags:
        return check(
            "data_quality", "Data quality", "warning", "Some context data is missing or stale."
        )
    return check("data_quality", "Data quality", "passed", "No data-quality blocker is active.")


def check(key: str, label: str, status: str, detail: str) -> AnalysisQualityCheck:
    return AnalysisQualityCheck(key=key, label=label, status=status, detail=detail)


def normalize_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []

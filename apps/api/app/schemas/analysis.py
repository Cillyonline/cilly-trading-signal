from decimal import Decimal

from pydantic import BaseModel

from app.models.enums import (
    Bias,
    MarketDataStatus,
    ScoreClass,
    SignalStatus,
    StrategyType,
    Timeframe,
)


class SignalAnalysisResult(BaseModel):
    strategy_type: StrategyType
    status: SignalStatus
    bias: Bias
    score: int
    score_class: ScoreClass
    timeframe_context: Timeframe
    timeframe_setup: Timeframe
    timeframe_trigger: Timeframe
    entry_low: Decimal | None
    entry_high: Decimal | None
    trigger_level: Decimal | None
    stop_loss: Decimal | None
    target_1: Decimal | None
    target_2: Decimal | None
    risk_reward: Decimal | None
    invalidation_reason: str | None
    reasoning: list[str]
    risk_flags: list[str]
    next_action: str
    no_trade_reasons: list[str]
    quality_report: list[dict[str, str]] = []


class MarketDataAnalysisResult(BaseModel):
    series_id: int
    status: MarketDataStatus
    candle_count: int
    indicator_snapshot_count: int
    signal: SignalAnalysisResult

from decimal import Decimal

from pydantic import BaseModel


class PerformanceByStrategyRead(BaseModel):
    strategy_type: str
    closed_trade_count: int
    total_r: Decimal
    average_r: Decimal | None
    win_rate: Decimal | None


class PerformanceByAssetClassRead(BaseModel):
    asset_class: str
    closed_trade_count: int
    total_r: Decimal
    average_r: Decimal | None
    win_rate: Decimal | None


class PerformanceSummaryRead(BaseModel):
    closed_trade_count: int
    total_r: Decimal
    average_r: Decimal | None
    win_rate: Decimal | None
    best_r: Decimal | None
    worst_r: Decimal | None
    by_strategy: list[PerformanceByStrategyRead]
    by_asset_class: list[PerformanceByAssetClassRead]

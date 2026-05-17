from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import AssetClass, StrategyType, TradeStatus
from app.models.trade import Trade
from app.schemas.performance import (
    PerformanceByAssetClassRead,
    PerformanceByStrategyRead,
    PerformanceSummaryRead,
)

FOUR_PLACES = Decimal("0.0001")
TWO_PLACES = Decimal("0.01")


def get_performance_summary(db: Session, user_id: int) -> PerformanceSummaryRead:
    trade_results = list(
        db.execute(
            select(Trade.strategy_type, Trade.asset_class, Trade.result_r).where(
                Trade.user_id == user_id,
                Trade.status == TradeStatus.CLOSED,
                Trade.result_r.is_not(None),
            )
        )
    )
    result_values = [result_r for _, _, result_r in trade_results]

    closed_trade_count = len(result_values)
    if closed_trade_count == 0:
        return PerformanceSummaryRead(
            closed_trade_count=0,
            total_r=Decimal("0.0000"),
            average_r=None,
            win_rate=None,
            best_r=None,
            worst_r=None,
            by_strategy=[],
            by_asset_class=[],
        )

    total_r = sum(result_values, Decimal("0"))
    winning_trades = sum(1 for result_r in result_values if result_r > 0)

    return PerformanceSummaryRead(
        closed_trade_count=closed_trade_count,
        total_r=_quantize(total_r, FOUR_PLACES),
        average_r=_quantize(total_r / closed_trade_count, FOUR_PLACES),
        win_rate=_quantize(Decimal(winning_trades) / closed_trade_count * 100, TWO_PLACES),
        best_r=_quantize(max(result_values), FOUR_PLACES),
        worst_r=_quantize(min(result_values), FOUR_PLACES),
        by_strategy=_build_strategy_breakdown(trade_results),
        by_asset_class=_build_asset_class_breakdown(trade_results),
    )


def _build_strategy_breakdown(
    trade_results: list[tuple[StrategyType, AssetClass, Decimal]]
) -> list[PerformanceByStrategyRead]:
    grouped_results: dict[StrategyType, list[Decimal]] = {}
    for strategy_type, _, result_r in trade_results:
        grouped_results.setdefault(strategy_type, []).append(result_r)

    return [
        PerformanceByStrategyRead(strategy_type=group_key.value, **metrics)
        for group_key, metrics in _build_group_metrics(grouped_results)
    ]


def _build_asset_class_breakdown(
    trade_results: list[tuple[StrategyType, AssetClass, Decimal]]
) -> list[PerformanceByAssetClassRead]:
    grouped_results: dict[AssetClass, list[Decimal]] = {}
    for _, asset_class, result_r in trade_results:
        grouped_results.setdefault(asset_class, []).append(result_r)

    return [
        PerformanceByAssetClassRead(asset_class=group_key.value, **metrics)
        for group_key, metrics in _build_group_metrics(grouped_results)
    ]


def _build_group_metrics(
    grouped_results: dict[StrategyType | AssetClass, list[Decimal]]
) -> list[tuple[StrategyType | AssetClass, dict[str, Decimal | int]]]:
    breakdown: list[tuple[StrategyType | AssetClass, dict[str, Decimal | int]]] = []
    sorted_groups = sorted(grouped_results.items(), key=lambda item: item[0].value)
    for strategy_type, result_values in sorted_groups:
        closed_trade_count = len(result_values)
        total_r = sum(result_values, Decimal("0"))
        winning_trades = sum(1 for result_r in result_values if result_r > 0)
        breakdown.append(
            (
                strategy_type,
                {
                    "closed_trade_count": closed_trade_count,
                    "total_r": _quantize(total_r, FOUR_PLACES),
                    "average_r": _quantize(total_r / closed_trade_count, FOUR_PLACES),
                    "win_rate": _quantize(
                        Decimal(winning_trades) / closed_trade_count * 100,
                        TWO_PLACES,
                    ),
                },
            )
        )

    return breakdown


def _quantize(value: Decimal, exponent: Decimal) -> Decimal:
    return value.quantize(exponent, rounding=ROUND_HALF_UP)

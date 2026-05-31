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
from app.services.settings import get_or_create_settings

FOUR_PLACES = Decimal("0.0001")
TWO_PLACES = Decimal("0.01")
RISK_REVIEW_ONLY_NOTICE = (
    "Open portfolio risk is based only on manually documented trades. It is review-only, "
    "not broker/account sync, automatic position sizing, an order recommendation, or "
    "trading advice."
)


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


def get_open_portfolio_risk(db: Session, user_id: int) -> dict:
    settings = get_or_create_settings(db, user_id)
    open_trades = list(
        db.scalars(
            select(Trade).where(
                Trade.user_id == user_id,
                Trade.status == TradeStatus.OPEN,
            )
        )
    )
    complete_trades = [trade for trade in open_trades if _has_complete_risk(trade)]
    incomplete_count = len(open_trades) - len(complete_trades)
    documented_risk_amount = _quantize(
        sum((trade.initial_risk_amount for trade in complete_trades), Decimal("0")),
        TWO_PLACES,
    )
    documented_risk_percent = _quantize(
        sum((trade.initial_risk_percent for trade in complete_trades), Decimal("0")),
        FOUR_PLACES,
    )
    warning_status, warnings = _build_open_risk_warnings(
        documented_risk_percent,
        settings.max_risk_percent,
        incomplete_count,
    )
    return {
        "open_trade_count": len(open_trades),
        "complete_risk_count": len(complete_trades),
        "incomplete_risk_count": incomplete_count,
        "documented_initial_risk_amount": documented_risk_amount,
        "documented_initial_risk_percent": documented_risk_percent,
        "max_risk_percent": settings.max_risk_percent,
        "warning_status": warning_status,
        "warnings": warnings,
        "by_strategy": _build_open_risk_groups(open_trades, "strategy_type"),
        "by_asset_class": _build_open_risk_groups(open_trades, "asset_class"),
        "review_only_notice": RISK_REVIEW_ONLY_NOTICE,
    }


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


def _build_open_risk_groups(open_trades: list[Trade], field_name: str) -> list[dict]:
    groups: dict[str, list[Trade]] = {}
    for trade in open_trades:
        value = getattr(trade, field_name)
        group = value.value if hasattr(value, "value") else str(value)
        groups.setdefault(group, []).append(trade)

    results: list[dict] = []
    for group, trades in sorted(groups.items()):
        complete_trades = [trade for trade in trades if _has_complete_risk(trade)]
        results.append(
            {
                "group": group,
                "open_trade_count": len(trades),
                "documented_initial_risk_amount": _quantize(
                    sum((trade.initial_risk_amount for trade in complete_trades), Decimal("0")),
                    TWO_PLACES,
                ),
                "documented_initial_risk_percent": _quantize(
                    sum((trade.initial_risk_percent for trade in complete_trades), Decimal("0")),
                    FOUR_PLACES,
                ),
                "incomplete_risk_count": len(trades) - len(complete_trades),
            }
        )
    return results


def _build_open_risk_warnings(
    documented_risk_percent: Decimal,
    max_risk_percent: Decimal,
    incomplete_count: int,
) -> tuple[str, list[str]]:
    warnings: list[str] = []
    if documented_risk_percent > max_risk_percent:
        warnings.append("Documented open risk percent exceeds the configured max risk percent.")
    if incomplete_count > 0:
        warnings.append("Some open trades are missing complete documented risk data.")

    if documented_risk_percent > max_risk_percent:
        return "warning", warnings
    if incomplete_count > 0:
        return "unknown", warnings
    return "ok", warnings


def _has_complete_risk(trade: Trade) -> bool:
    return trade.initial_risk_amount is not None and trade.initial_risk_percent is not None


def _quantize(value: Decimal, exponent: Decimal) -> Decimal:
    return value.quantize(exponent, rounding=ROUND_HALF_UP)

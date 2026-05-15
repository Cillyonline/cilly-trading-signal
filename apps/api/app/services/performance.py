from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import TradeStatus
from app.models.trade import Trade
from app.schemas.performance import PerformanceSummaryRead

FOUR_PLACES = Decimal("0.0001")
TWO_PLACES = Decimal("0.01")


def get_performance_summary(db: Session, user_id: int) -> PerformanceSummaryRead:
    result_values = list(
        db.scalars(
            select(Trade.result_r).where(
                Trade.user_id == user_id,
                Trade.status == TradeStatus.CLOSED,
                Trade.result_r.is_not(None),
            )
        )
    )

    closed_trade_count = len(result_values)
    if closed_trade_count == 0:
        return PerformanceSummaryRead(
            closed_trade_count=0,
            total_r=Decimal("0.0000"),
            average_r=None,
            win_rate=None,
            best_r=None,
            worst_r=None,
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
    )


def _quantize(value: Decimal, exponent: Decimal) -> Decimal:
    return value.quantize(exponent, rounding=ROUND_HALF_UP)

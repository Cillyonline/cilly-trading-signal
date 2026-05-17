import csv
import io
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.trade import Trade
from app.services.performance import get_performance_summary

TRADES_CSV_HEADERS = [
    "id",
    "symbol",
    "strategy_type",
    "asset_class",
    "status",
    "entry_price",
    "stop_loss",
    "target_1",
    "target_2",
    "position_size",
    "fees",
    "opened_at",
    "closed_at",
    "exit_price",
    "exit_reason",
    "initial_risk_amount",
    "initial_risk_percent",
    "initial_risk_reward",
    "result_amount",
    "result_r",
    "notes",
    "review_complete",
]

PERFORMANCE_CSV_HEADERS = [
    "section",
    "group",
    "closed_trade_count",
    "total_r",
    "average_r",
    "win_rate",
    "best_r",
    "worst_r",
]


def export_trades_csv(db: Session, user_id: int) -> str:
    trades = list(
        db.scalars(
            select(Trade)
            .where(Trade.user_id == user_id)
            .options(selectinload(Trade.journal_entry))
            .order_by(Trade.opened_at.desc(), Trade.id.desc())
        )
    )

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=TRADES_CSV_HEADERS, lineterminator="\r\n")
    writer.writeheader()
    for trade in trades:
        writer.writerow(
            {
                "id": trade.id,
                "symbol": trade.symbol,
                "strategy_type": trade.strategy_type.value if trade.strategy_type else "",
                "asset_class": trade.asset_class.value if trade.asset_class else "",
                "status": trade.status.value if trade.status else "",
                "entry_price": _fmt(trade.entry_price),
                "stop_loss": _fmt(trade.stop_loss),
                "target_1": _fmt(trade.target_1),
                "target_2": _fmt(trade.target_2),
                "position_size": _fmt(trade.position_size),
                "fees": _fmt(trade.fees),
                "opened_at": _fmt_dt(trade.opened_at),
                "closed_at": _fmt_dt(trade.closed_at),
                "exit_price": _fmt(trade.exit_price),
                "exit_reason": trade.exit_reason.value if trade.exit_reason else "",
                "initial_risk_amount": _fmt(trade.initial_risk_amount),
                "initial_risk_percent": _fmt(trade.initial_risk_percent),
                "initial_risk_reward": _fmt(trade.initial_risk_reward),
                "result_amount": _fmt(trade.result_amount),
                "result_r": _fmt(trade.result_r),
                "notes": trade.notes or "",
                "review_complete": "yes" if trade.journal_entry is not None else "no",
            }
        )

    return output.getvalue()


def export_performance_csv(db: Session, user_id: int) -> str:
    summary = get_performance_summary(db, user_id)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=PERFORMANCE_CSV_HEADERS, lineterminator="\r\n")
    writer.writeheader()

    writer.writerow(
        {
            "section": "overall",
            "group": "",
            "closed_trade_count": summary.closed_trade_count,
            "total_r": _fmt(summary.total_r),
            "average_r": _fmt(summary.average_r),
            "win_rate": _fmt(summary.win_rate),
            "best_r": _fmt(summary.best_r),
            "worst_r": _fmt(summary.worst_r),
        }
    )

    for item in summary.by_strategy:
        writer.writerow(
            {
                "section": "by_strategy",
                "group": item.strategy_type,
                "closed_trade_count": item.closed_trade_count,
                "total_r": _fmt(item.total_r),
                "average_r": _fmt(item.average_r),
                "win_rate": _fmt(item.win_rate),
                "best_r": "",
                "worst_r": "",
            }
        )

    for item in summary.by_asset_class:
        writer.writerow(
            {
                "section": "by_asset_class",
                "group": item.asset_class,
                "closed_trade_count": item.closed_trade_count,
                "total_r": _fmt(item.total_r),
                "average_r": _fmt(item.average_r),
                "win_rate": _fmt(item.win_rate),
                "best_r": "",
                "worst_r": "",
            }
        )

    return output.getvalue()


def _fmt(value: Decimal | None) -> str:
    if value is None:
        return ""
    return str(value)


def _fmt_dt(value: object) -> str:
    if value is None:
        return ""
    return str(value)

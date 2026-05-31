from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.performance import PerformanceSummaryRead
from app.services.performance import (
    get_journal_analytics,
    get_open_portfolio_risk,
    get_performance_summary,
)

router = APIRouter(prefix="/performance", tags=["performance"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


class OpenRiskGroupRead(BaseModel):
    group: str
    open_trade_count: int
    documented_initial_risk_amount: Decimal
    documented_initial_risk_percent: Decimal
    incomplete_risk_count: int


class ConcentrationGroupRead(BaseModel):
    group: str
    open_trade_count: int
    open_trade_percent: Decimal
    warning: bool


class AssetConcentrationRead(BaseModel):
    warning_status: str
    warning_threshold_percent: Decimal
    warnings: list[str]
    by_asset_class: list[ConcentrationGroupRead]
    by_symbol: list[ConcentrationGroupRead]
    by_sector: list[ConcentrationGroupRead]
    by_industry: list[ConcentrationGroupRead]
    review_only_notice: str


class CorrelationProxyRead(BaseModel):
    key: str
    label: str
    status: str
    open_trade_count: int
    symbols: list[str]
    message: str


class CorrelationProxySummaryRead(BaseModel):
    warning_status: str
    warnings: list[CorrelationProxyRead]
    review_only_notice: str


class JournalScoreSummaryRead(BaseModel):
    average_entry_quality_score: Decimal | None
    average_stop_quality_score: Decimal | None
    average_exit_quality_score: Decimal | None
    average_discipline_score: Decimal | None


class JournalStrategySummaryRead(JournalScoreSummaryRead):
    strategy_type: str
    reviewed_trade_count: int
    setup_rule_followed_count: int
    setup_rule_broken_count: int
    setup_rule_unknown_count: int


class JournalAnalyticsRead(JournalScoreSummaryRead):
    closed_trade_count: int
    reviewed_trade_count: int
    missing_review_count: int
    setup_rule_followed_count: int
    setup_rule_broken_count: int
    setup_rule_unknown_count: int
    min_strategy_sample_size: int
    by_strategy: list[JournalStrategySummaryRead]
    small_sample_notice: str


class OpenPortfolioRiskRead(BaseModel):
    open_trade_count: int
    complete_risk_count: int
    incomplete_risk_count: int
    documented_initial_risk_amount: Decimal
    documented_initial_risk_percent: Decimal
    max_risk_percent: Decimal
    warning_status: str
    warnings: list[str]
    asset_concentration: AssetConcentrationRead
    correlation_proxies: CorrelationProxySummaryRead
    by_strategy: list[OpenRiskGroupRead]
    by_asset_class: list[OpenRiskGroupRead]
    review_only_notice: str


class PerformanceSummaryWithOpenRiskRead(PerformanceSummaryRead):
    open_portfolio_risk: OpenPortfolioRiskRead
    journal_analytics: JournalAnalyticsRead


@router.get("/summary", response_model=PerformanceSummaryWithOpenRiskRead)
def get_summary(db: DbSession, user: CurrentUser) -> PerformanceSummaryWithOpenRiskRead:
    summary = get_performance_summary(db, user.id).model_dump()
    summary["open_portfolio_risk"] = get_open_portfolio_risk(db, user.id)
    summary["journal_analytics"] = get_journal_analytics(db, user.id)
    return PerformanceSummaryWithOpenRiskRead.model_validate(summary)

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.performance import PerformanceSummaryRead
from app.services.performance import get_open_portfolio_risk, get_performance_summary

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


@router.get("/summary", response_model=PerformanceSummaryWithOpenRiskRead)
def get_summary(db: DbSession, user: CurrentUser) -> PerformanceSummaryWithOpenRiskRead:
    summary = get_performance_summary(db, user.id).model_dump()
    summary["open_portfolio_risk"] = get_open_portfolio_risk(db, user.id)
    return PerformanceSummaryWithOpenRiskRead.model_validate(summary)

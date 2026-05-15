from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.performance import PerformanceSummaryRead
from app.services.performance import get_performance_summary
from app.services.watchlist import get_or_create_default_user

router = APIRouter(prefix="/performance", tags=["performance"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/summary", response_model=PerformanceSummaryRead)
def get_summary(db: DbSession) -> PerformanceSummaryRead:
    user = get_or_create_default_user(db)
    return get_performance_summary(db, user.id)

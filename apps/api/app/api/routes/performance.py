from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.performance import PerformanceSummaryRead
from app.services.performance import get_performance_summary

router = APIRouter(prefix="/performance", tags=["performance"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/summary", response_model=PerformanceSummaryRead)
def get_summary(db: DbSession, user: CurrentUser) -> PerformanceSummaryRead:
    return get_performance_summary(db, user.id)

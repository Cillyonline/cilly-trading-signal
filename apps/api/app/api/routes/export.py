from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.export import export_performance_csv, export_trades_csv

router = APIRouter(prefix="/export", tags=["export"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/trades")
def get_trades_export(db: DbSession, user: CurrentUser) -> StreamingResponse:
    csv_content = export_trades_csv(db, user.id)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=trades.csv"},
    )


@router.get("/performance")
def get_performance_export(db: DbSession, user: CurrentUser) -> StreamingResponse:
    csv_content = export_performance_csv(db, user.id)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=performance.csv"},
    )

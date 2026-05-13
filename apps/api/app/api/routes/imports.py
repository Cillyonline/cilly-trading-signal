from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.enums import Timeframe
from app.schemas.imports import CsvImportResult
from app.services.csv_import import import_tradingview_csv
from app.services.watchlist import get_or_create_default_user, get_watchlist_item

router = APIRouter(prefix="/imports", tags=["imports"])
DbSession = Annotated[Session, Depends(get_db)]


@router.post("/csv", response_model=CsvImportResult)
async def import_csv(
    db: DbSession,
    watchlist_item_id: Annotated[int, Form()],
    timeframe: Annotated[Timeframe, Form()],
    file: Annotated[UploadFile, File()],
) -> CsvImportResult:
    user = get_or_create_default_user(db)
    watchlist_item = get_watchlist_item(db, user.id, watchlist_item_id)
    if watchlist_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist item not found.")

    content_bytes = await file.read()
    try:
        content = content_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file must be UTF-8 encoded.",
        ) from error

    result = import_tradingview_csv(
        db=db,
        watchlist_item=watchlist_item,
        timeframe=timeframe,
        file_name=file.filename,
        content=content,
    )
    if result.errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[error.model_dump() for error in result.errors],
        )
    return result

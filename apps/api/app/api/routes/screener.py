from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import AssetClass
from app.models.user import User
from app.schemas.screener import ScreenerImportDetail, ScreenerImportRead, ScreenerResultRead
from app.services.screener_import import (
    MAX_SCREENER_UPLOAD_BYTES,
    get_screener_import,
    import_screener_csv,
    list_screener_imports,
    list_screener_results,
)

router = APIRouter(prefix="/screener", tags=["screener"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/imports", response_model=ScreenerImportRead, status_code=status.HTTP_201_CREATED)
async def import_screener(
    db: DbSession,
    user: CurrentUser,
    asset_class: Annotated[AssetClass, Form()],
    file: Annotated[UploadFile, File()],
    screener_preset: Annotated[str | None, Form()] = None,
) -> ScreenerImportRead:
    content_bytes = await file.read()
    if len(content_bytes) > MAX_SCREENER_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=[
                {
                    "row": None,
                    "field": "file",
                    "message": f"CSV file must be at most {MAX_SCREENER_UPLOAD_BYTES} bytes.",
                }
            ],
        )

    try:
        content = content_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file must be UTF-8 encoded.",
        ) from error

    import_record, errors = import_screener_csv(
        db=db,
        user_id=user.id,
        asset_class=asset_class,
        file_name=file.filename,
        content=content,
        screener_preset=screener_preset,
    )
    if import_record is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[error.to_dict() for error in errors],
        )
    return import_record


@router.get("/imports", response_model=list[ScreenerImportRead])
def list_imports(db: DbSession, user: CurrentUser) -> list[ScreenerImportRead]:
    return list_screener_imports(db, user.id)


@router.get("/imports/{import_id}", response_model=ScreenerImportDetail)
def get_import(import_id: int, db: DbSession, user: CurrentUser) -> ScreenerImportDetail:
    import_record = get_screener_import(db, user.id, import_id)
    if import_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screener import not found.",
        )
    return ScreenerImportDetail.model_validate(import_record)


@router.get("/results", response_model=list[ScreenerResultRead])
def list_results(db: DbSession, user: CurrentUser) -> list[ScreenerResultRead]:
    return list_screener_results(db, user.id)

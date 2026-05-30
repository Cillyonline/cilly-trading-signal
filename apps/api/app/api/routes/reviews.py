from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.review import ReviewBatch
from app.models.user import User
from app.schemas.reviews import (
    ReviewBatchCreate,
    ReviewBatchRead,
    ReviewEntryCreate,
    ReviewEntryRead,
)
from app.services.reviews import (
    ReviewEntryError,
    build_review_batch_summary,
    create_review_batch,
    create_review_entry,
    get_review_batch,
    list_review_batches,
)

router = APIRouter(prefix="/reviews", tags=["reviews"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/batches", response_model=list[ReviewBatchRead])
def list_batches(db: DbSession, user: CurrentUser) -> list[ReviewBatchRead]:
    return [to_batch_read(batch) for batch in list_review_batches(db, user.id)]


@router.post("/batches", response_model=ReviewBatchRead, status_code=status.HTTP_201_CREATED)
def create_batch(payload: ReviewBatchCreate, db: DbSession, user: CurrentUser) -> ReviewBatchRead:
    return to_batch_read(create_review_batch(db, user.id, payload))


@router.get("/batches/{batch_id}", response_model=ReviewBatchRead)
def get_batch(batch_id: int, db: DbSession, user: CurrentUser) -> ReviewBatchRead:
    batch = get_review_batch(db, user.id, batch_id)
    if batch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review batch not found.")
    return to_batch_read(batch)


@router.post(
    "/batches/{batch_id}/entries",
    response_model=ReviewEntryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_entry(
    batch_id: int, payload: ReviewEntryCreate, db: DbSession, user: CurrentUser
) -> ReviewEntryRead:
    try:
        return create_review_entry(db, user.id, batch_id, payload)
    except ReviewEntryError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message) from error


def to_batch_read(batch: ReviewBatch) -> ReviewBatchRead:
    return ReviewBatchRead.model_validate(
        {**batch.__dict__, "summary": build_review_batch_summary(batch)}
    )

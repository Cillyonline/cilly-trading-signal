from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_session_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthUserRead, LoginRequest
from app.services.auth import LoginRateLimitExceededError, authenticate_admin

router = APIRouter(prefix="/auth", tags=["auth"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/login", response_model=AuthUserRead)
def login(payload: LoginRequest, response: Response, db: DbSession) -> AuthUserRead:
    try:
        user = authenticate_admin(db, payload.email, payload.password)
    except LoginRateLimitExceededError as error:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
        ) from error
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    response.set_cookie(
        key=settings.auth_cookie_name,
        value=create_session_token(user.id),
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
        max_age=settings.auth_session_ttl_seconds,
        path="/",
    )
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout() -> Response:
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(key=settings.auth_cookie_name, path="/")
    return response


@router.get("/me", response_model=AuthUserRead)
def me(user: CurrentUser) -> AuthUserRead:
    return user

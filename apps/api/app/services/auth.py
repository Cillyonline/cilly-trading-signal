from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.models.enums import UserRole
from app.models.user import User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_or_create_admin_user(db: Session) -> User:
    user = get_user_by_email(db, settings.admin_email)
    if user is not None:
        return user

    user = User(
        email=settings.admin_email,
        password_hash=hash_password(settings.admin_initial_password),
        display_name="Admin",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_admin(db: Session, email: str, password: str) -> User | None:
    if email != settings.admin_email:
        return None
    user = get_or_create_admin_user(db)
    if not user.is_active or not verify_password(password, user.password_hash):
        return None
    user.last_login_at = datetime.now(UTC)
    db.commit()
    db.refresh(user)
    return user

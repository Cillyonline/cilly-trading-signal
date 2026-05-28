from datetime import UTC, datetime
import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.models.enums import UserRole
from app.models.user import User


class LoginRateLimitExceededError(Exception):
    pass


_failed_login_attempts: dict[str, int] = {}
_login_locked_until: dict[str, float] = {}


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
    _raise_if_login_rate_limited(email)

    if email != settings.admin_email:
        _record_failed_login(email)
        return None
    user = get_or_create_admin_user(db)
    if not user.is_active or not verify_password(password, user.password_hash):
        _record_failed_login(email)
        return None
    _clear_failed_login(email)
    user.last_login_at = datetime.now(UTC)
    db.commit()
    db.refresh(user)
    return user


def reset_login_rate_limit() -> None:
    _failed_login_attempts.clear()
    _login_locked_until.clear()


def _raise_if_login_rate_limited(email: str) -> None:
    key = _rate_limit_key(email)
    locked_until = _login_locked_until.get(key)
    if locked_until is None:
        return
    now = time.monotonic()
    if locked_until > now:
        raise LoginRateLimitExceededError
    _login_locked_until.pop(key, None)
    _failed_login_attempts.pop(key, None)


def _record_failed_login(email: str) -> None:
    key = _rate_limit_key(email)
    failed_attempts = _failed_login_attempts.get(key, 0) + 1
    _failed_login_attempts[key] = failed_attempts
    if failed_attempts >= settings.auth_login_max_failed_attempts:
        _login_locked_until[key] = time.monotonic() + settings.auth_login_lockout_seconds


def _clear_failed_login(email: str) -> None:
    key = _rate_limit_key(email)
    _failed_login_attempts.pop(key, None)
    _login_locked_until.pop(key, None)


def _rate_limit_key(email: str) -> str:
    return email.strip().lower()

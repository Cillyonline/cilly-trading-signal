from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time

from app.core.config import settings

HASH_ITERATIONS = 210_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, HASH_ITERATIONS)
    encoded_salt = _b64encode(salt)
    encoded_digest = _b64encode(digest)
    return f"pbkdf2_sha256${HASH_ITERATIONS}${encoded_salt}${encoded_digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected = password_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        _b64decode(salt),
        int(iterations),
    )
    return hmac.compare_digest(_b64encode(digest), expected)


def create_session_token(user_id: int, now: int | None = None) -> str:
    issued_at = now or int(time.time())
    expires_at = issued_at + settings.auth_session_ttl_seconds
    nonce = secrets.token_urlsafe(16)
    payload = f"{user_id}:{expires_at}:{nonce}"
    signature = _sign(payload)
    return f"{payload}:{signature}"


def parse_session_token(token: str) -> int | None:
    parts = token.split(":")
    if len(parts) != 4:
        return None
    user_id, expires_at, nonce, signature = parts
    payload = f"{user_id}:{expires_at}:{nonce}"
    if not hmac.compare_digest(_sign(payload), signature):
        return None
    try:
        parsed_user_id = int(user_id)
        parsed_expires_at = int(expires_at)
    except ValueError:
        return None
    if parsed_expires_at < int(time.time()):
        return None
    return parsed_user_id


def _sign(payload: str) -> str:
    digest = hmac.new(settings.secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256)
    return digest.hexdigest()


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value.encode("ascii"))

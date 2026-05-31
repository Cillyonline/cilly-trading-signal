from pathlib import Path

from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import SessionLocal

router = APIRouter(tags=["health"])
EXPECTED_MIGRATION_PREFIX = "20260530_0008"


@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/health/details")
def detailed_health_check() -> dict:
    database = _check_database()
    migrations = _check_migrations()
    checks = {
        "database": database,
        "migrations": migrations,
        "configuration": _check_configuration(),
    }
    status = "ok" if all(check["status"] == "ok" for check in checks.values()) else "degraded"
    return {
        "status": status,
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "checks": checks,
    }


def _check_database() -> dict[str, bool | str]:
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return {"status": "degraded", "reachable": False}
    return {"status": "ok", "reachable": True}


def _check_migrations() -> dict[str, bool | str]:
    versions_dir = Path(__file__).resolve().parents[3] / "alembic" / "versions"
    expected_present = any(versions_dir.glob(f"{EXPECTED_MIGRATION_PREFIX}_*.py"))
    return {
        "status": "ok" if expected_present else "degraded",
        "expected_latest_revision": EXPECTED_MIGRATION_PREFIX,
        "expected_latest_revision_present": expected_present,
    }


def _check_configuration() -> dict[str, bool | str]:
    return {
        "status": "ok",
        "safe_config_summary_only": True,
        "auth_cookie_secure": settings.auth_cookie_secure,
        "market_data_provider_sync_enabled": settings.market_data_provider_sync_enabled,
        "telegram_alert_routing_enabled": settings.telegram_alert_routing_enabled,
    }

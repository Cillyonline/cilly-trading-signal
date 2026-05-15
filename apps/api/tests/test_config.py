import pytest

from app.core.config import Settings


SAFE_PRODUCTION_SETTINGS = {
    "environment": "production",
    "database_url": "postgresql+psycopg://app_user:strong-db-password@postgres:5432/app_db",
    "secret_key": "strong-session-secret",
    "tradingview_webhook_secret": "strong-webhook-secret",
    "admin_email": "admin@trading.example.com",
    "admin_initial_password": "strong-admin-password",
    "auth_cookie_secure": True,
    "cors_origins": ["https://trading.example.com"],
}


def test_development_allows_local_defaults() -> None:
    settings = Settings(_env_file=None, environment="development")

    assert settings.secret_key == "change-me"
    assert settings.tradingview_webhook_secret == "change-me"


def test_production_allows_safe_values() -> None:
    settings = Settings(_env_file=None, **SAFE_PRODUCTION_SETTINGS)

    assert settings.environment == "production"


@pytest.mark.parametrize(
    ("field", "value", "expected_message"),
    [
        ("secret_key", "change-me", "SECRET_KEY"),
        ("secret_key", "", "SECRET_KEY"),
        ("tradingview_webhook_secret", "change-me", "TRADINGVIEW_WEBHOOK_SECRET"),
        ("admin_email", "admin@example.com", "ADMIN_EMAIL"),
        ("admin_initial_password", "change-this-password", "ADMIN_INITIAL_PASSWORD"),
        ("auth_cookie_secure", False, "AUTH_COOKIE_SECURE"),
        ("database_url", "", "DATABASE_URL"),
        (
            "database_url",
            "postgresql+psycopg://postgres:postgres@postgres:5432/cilly_trading_signal",
            "DATABASE_URL",
        ),
        ("cors_origins", ["*"], "CORS_ORIGINS"),
    ],
)
def test_production_rejects_unsafe_settings(
    field: str,
    value: object,
    expected_message: str,
) -> None:
    payload = SAFE_PRODUCTION_SETTINGS | {field: value}

    with pytest.raises(ValueError, match=expected_message):
        Settings(_env_file=None, **payload)


def test_staging_rejects_unsafe_settings() -> None:
    payload = SAFE_PRODUCTION_SETTINGS | {"environment": "staging", "secret_key": "change-me"}

    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(_env_file=None, **payload)

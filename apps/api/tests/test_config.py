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
    assert settings.telegram_alert_routing_enabled is False


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


def test_telegram_alert_routing_defaults_to_disabled() -> None:
    settings = Settings(_env_file=None, environment="development")

    assert settings.telegram_alert_routing_enabled is False
    assert settings.telegram_bot_token is None
    assert settings.telegram_chat_id is None


def test_telegram_alert_routing_allows_safe_configuration() -> None:
    settings = Settings(
        _env_file=None,
        **SAFE_PRODUCTION_SETTINGS,
        telegram_alert_routing_enabled=True,
        telegram_bot_token="1234567890:valid-test-token",
        telegram_chat_id="123456789",
    )

    assert settings.telegram_alert_routing_enabled is True


@pytest.mark.parametrize(
    ("field", "value", "expected_message"),
    [
        ("telegram_bot_token", None, "TELEGRAM_BOT_TOKEN"),
        ("telegram_bot_token", "", "TELEGRAM_BOT_TOKEN"),
        ("telegram_bot_token", "change-this-telegram-bot-token", "TELEGRAM_BOT_TOKEN"),
        ("telegram_chat_id", None, "TELEGRAM_CHAT_ID"),
        ("telegram_chat_id", "", "TELEGRAM_CHAT_ID"),
        ("telegram_chat_id", "change-this-telegram-chat-id", "TELEGRAM_CHAT_ID"),
    ],
)
def test_telegram_alert_routing_rejects_missing_or_placeholder_config(
    field: str,
    value: object,
    expected_message: str,
) -> None:
    payload = SAFE_PRODUCTION_SETTINGS | {
        "telegram_alert_routing_enabled": True,
        "telegram_bot_token": "1234567890:valid-test-token",
        "telegram_chat_id": "123456789",
        field: value,
    }

    with pytest.raises(ValueError, match=expected_message):
        Settings(_env_file=None, **payload)


def test_market_data_provider_sync_defaults_to_disabled() -> None:
    settings = Settings(_env_file=None, environment="development")

    assert settings.market_data_provider_sync_enabled is False
    assert settings.market_data_provider is None
    assert settings.market_data_api_key is None


def test_market_data_provider_sync_allows_safe_configuration() -> None:
    settings = Settings(
        _env_file=None,
        **SAFE_PRODUCTION_SETTINGS,
        market_data_provider_sync_enabled=True,
        market_data_provider="alpha_vantage",
        market_data_api_key="strong-provider-api-key",
    )

    assert settings.market_data_provider_sync_enabled is True
    assert settings.market_data_provider == "alpha_vantage"


@pytest.mark.parametrize(
    ("field", "value", "expected_message"),
    [
        ("market_data_provider", None, "MARKET_DATA_PROVIDER"),
        ("market_data_provider", "", "MARKET_DATA_PROVIDER"),
        ("market_data_provider", "unknown_provider", "MARKET_DATA_PROVIDER"),
        ("market_data_api_key", None, "MARKET_DATA_API_KEY"),
        ("market_data_api_key", "", "MARKET_DATA_API_KEY"),
        (
            "market_data_api_key",
            "change-this-market-data-api-key",
            "MARKET_DATA_API_KEY",
        ),
    ],
)
def test_market_data_provider_sync_rejects_missing_or_placeholder_config(
    field: str,
    value: object,
    expected_message: str,
) -> None:
    payload = SAFE_PRODUCTION_SETTINGS | {
        "market_data_provider_sync_enabled": True,
        "market_data_provider": "alpha_vantage",
        "market_data_api_key": "strong-provider-api-key",
        field: value,
    }

    with pytest.raises(ValueError, match=expected_message):
        Settings(_env_file=None, **payload)

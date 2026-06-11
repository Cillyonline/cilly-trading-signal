from urllib.parse import urlsplit

from pydantic_settings import BaseSettings, SettingsConfigDict


SAFE_LOCAL_ENVIRONMENTS = {"development", "test"}
UNSAFE_SECRET_VALUES = {"", "change-me", "change-this-secret-key", "change-this-webhook-secret"}
UNSAFE_PASSWORD_VALUES = {"", "postgres", "password", "change-me", "change-this-password"}
UNSAFE_ADMIN_EMAILS = {"", "admin@example.com"}
UNSAFE_TELEGRAM_VALUES = {
    "",
    "change-me",
    "change-this-telegram-bot-token",
    "change-this-telegram-chat-id",
    "telegram-bot-token",
    "telegram-chat-id",
}
UNSAFE_MARKET_DATA_VALUES = {
    "",
    "change-me",
    "change-this-market-data-api-key",
    "market-data-api-key",
    "provider-api-key",
}
SUPPORTED_MARKET_DATA_PROVIDERS = {
    "alpha_vantage",
    "twelve_data",
}


def _has_unsafe_database_credentials(database_url: str) -> bool:
    parsed = urlsplit(database_url)
    if parsed.scheme not in {"postgres", "postgresql", "postgresql+psycopg"}:
        return False

    username = parsed.username or ""
    password = parsed.password or ""
    return username == "postgres" or password in UNSAFE_PASSWORD_VALUES


def _has_unsafe_cors_origin(cors_origins: list[str]) -> bool:
    return any("*" in origin for origin in cors_origins)


def _is_unsafe_optional_secret(value: str | None, unsafe_values: set[str]) -> bool:
    return value is None or value.strip() in unsafe_values


class Settings(BaseSettings):
    app_name: str = "Cilly Trading Signal API"
    app_version: str = "0.1.0"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@postgres:5432/cilly_trading_signal"
    secret_key: str = "change-me"
    cors_origins: list[str] = ["http://localhost:3000"]
    admin_email: str = "admin@example.com"
    admin_initial_password: str = "change-this-password"
    auth_cookie_name: str = "cilly_session"
    auth_cookie_secure: bool = False
    auth_session_ttl_seconds: int = 60 * 60 * 12
    auth_login_max_failed_attempts: int = 5
    auth_login_lockout_seconds: int = 60
    tradingview_webhook_secret: str = "change-me"
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    telegram_alert_routing_enabled: bool = False
    market_data_provider_sync_enabled: bool = False
    market_data_provider: str | None = None
    market_data_api_key: str | None = None

    def __init__(self, **values: object) -> None:
        super().__init__(**values)
        self._validate_deployment_safety()
        self._validate_telegram_alert_routing()
        self._validate_market_data_provider_sync()

    def _validate_deployment_safety(self) -> None:
        if self.environment.strip().lower() in SAFE_LOCAL_ENVIRONMENTS:
            return

        errors: list[str] = []
        if self.secret_key.strip() in UNSAFE_SECRET_VALUES:
            errors.append("SECRET_KEY must be set to a non-default value")
        if self.tradingview_webhook_secret.strip() in UNSAFE_SECRET_VALUES:
            errors.append("TRADINGVIEW_WEBHOOK_SECRET must be set to a non-default value")
        if self.admin_email.strip().lower() in UNSAFE_ADMIN_EMAILS:
            errors.append("ADMIN_EMAIL must be set to a non-default value")
        if self.admin_initial_password.strip() in UNSAFE_PASSWORD_VALUES:
            errors.append("ADMIN_INITIAL_PASSWORD must be set to a non-default value")
        if not self.auth_cookie_secure:
            errors.append("AUTH_COOKIE_SECURE must be true")
        if not self.database_url.strip():
            errors.append("DATABASE_URL must be set")
        if _has_unsafe_database_credentials(self.database_url):
            errors.append("DATABASE_URL must not use empty or default database credentials")
        if _has_unsafe_cors_origin(self.cors_origins):
            errors.append("CORS_ORIGINS must not allow wildcard origins")

        if errors:
            raise ValueError("Unsafe production configuration: " + "; ".join(errors))

    def _validate_telegram_alert_routing(self) -> None:
        if not self.telegram_alert_routing_enabled:
            return

        errors: list[str] = []
        if _is_unsafe_optional_secret(self.telegram_bot_token, UNSAFE_TELEGRAM_VALUES):
            errors.append(
                "TELEGRAM_BOT_TOKEN must be set before TELEGRAM_ALERT_ROUTING_ENABLED can be true"
            )
        if _is_unsafe_optional_secret(self.telegram_chat_id, UNSAFE_TELEGRAM_VALUES):
            errors.append(
                "TELEGRAM_CHAT_ID must be set before TELEGRAM_ALERT_ROUTING_ENABLED can be true"
            )

        if errors:
            raise ValueError(
                "Unsafe Telegram alert routing configuration: " + "; ".join(errors)
            )

    def _validate_market_data_provider_sync(self) -> None:
        if not self.market_data_provider_sync_enabled:
            return

        errors: list[str] = []
        provider = (self.market_data_provider or "").strip().lower()
        if provider not in SUPPORTED_MARKET_DATA_PROVIDERS:
            errors.append(
                "MARKET_DATA_PROVIDER must be one of "
                + ", ".join(sorted(SUPPORTED_MARKET_DATA_PROVIDERS))
                + " before MARKET_DATA_PROVIDER_SYNC_ENABLED can be true"
            )
        if _is_unsafe_optional_secret(self.market_data_api_key, UNSAFE_MARKET_DATA_VALUES):
            errors.append(
                "MARKET_DATA_API_KEY must be set before "
                "MARKET_DATA_PROVIDER_SYNC_ENABLED can be true"
            )

        if errors:
            raise ValueError(
                "Unsafe market data provider configuration: " + "; ".join(errors)
            )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

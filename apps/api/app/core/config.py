from pydantic_settings import BaseSettings, SettingsConfigDict


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
    tradingview_webhook_secret: str = "change-me"
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

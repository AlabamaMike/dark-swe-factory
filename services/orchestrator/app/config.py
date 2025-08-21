from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "dsf-orchestrator"
    ENV: str = "dev"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    REDIS_URL: str = "redis://localhost:6379/0"
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/dsf"

    GITHUB_WEBHOOK_SECRET: str = "change-me"
    GITHUB_APP_ID: str | None = None
    GITHUB_PRIVATE_KEY_PATH: str | None = None


settings = Settings()
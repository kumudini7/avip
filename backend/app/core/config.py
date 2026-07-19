from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AVIP API"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 480
    database_url: str = "mysql+pymysql://root:password@localhost:3306/avip"
    upload_dir: str = "storage/uploads"
    report_dir: str = "storage/reports"
    analysis_provider: str = "auto"
    openai_model: str = "gpt-4.1-mini"
    openai_api_key: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_model: str = "gpt-4.1-mini"
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_api_version: str = "2024-10-21"
    gemini_model: str = "gemini-2.0-flash"
    gemini_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-5"
    anthropic_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    groq_api_key: str | None = None
    analysis_temperature: float = 0.2
    demo_user_email: str = "demo@avip.test"
    demo_user_password: str = "Demo@12345"
    usd_inr_rate: float = 83.0
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

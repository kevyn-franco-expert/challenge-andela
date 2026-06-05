from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    database_url: str = Field(default="sqlite+aiosqlite:///./watchdog.db")
    webhook_timeout_seconds: int = Field(default=10)
    webhook_max_retries: int = Field(default=3)
    anomaly_threshold_zscore: float = Field(default=2.5)
    anomaly_window_minutes: int = Field(default=5)
    log_level: str = Field(default="INFO")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application Mode / Environment
    ENV: str = "development"
    
    # Security & Protection Keys
    CRON_KEY: str = "dev_cron_key"

    # Database Configuration
    DATABASE_URL: Optional[str] = None
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # Redis/Cache Configuration
    REDIS_URL: Optional[str] = None

    # Settings configuration: loads env vars and reads .env files (in order) if present
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Create a singleton settings object
settings = Settings()

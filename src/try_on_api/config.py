from pathlib import Path

from pydantic import DirectoryPath
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_KEY: str

    LOG_DIR: str = "logs"
    LOG_LEVEL: str = "INFO"
    DB_LOG_LEVEL: str = "ERROR"
    ENABLE_LOG_FILE: bool = False
    LOG_FILE_SIZE_IN_MB: int = 5

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", case_sensitive=True
    )


Config = Settings()

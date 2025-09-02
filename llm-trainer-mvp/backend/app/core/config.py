# Config and settings for backend
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Use sqlite file in project data dir by default
    DATABASE_URL: str = "sqlite:///../data/database.db"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()
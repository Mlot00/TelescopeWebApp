from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TWAPP_", env_file=".env", extra="ignore")

    env: str = "dev"
    datasets_file: Path = Field(default=Path("data/datasets.yml"))
    data_dir: Path = Field(default=Path("data"))
    cache_dir: Path = Field(default=Path(".cache"))
    output_dir: Path = Field(default=Path("output"))
    log_level: str = "INFO"


@lru_cache

def get_settings() -> Settings:
    return Settings()

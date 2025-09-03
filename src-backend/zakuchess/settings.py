from __future__ import annotations

from typing import Literal

from pydantic_core import Url  # noqa: TC002 # Pydantic needs to read this
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnvironment = Literal["production", "development"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.local", env_prefix="APP_")
    environment: AppEnvironment = "production"
    astro_dev_url: Url = "http://localhost:4321"


def get_settings() -> Settings:
    return Settings()

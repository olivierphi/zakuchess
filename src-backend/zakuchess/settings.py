from __future__ import annotations

import functools
from pathlib import Path
from typing import Literal

from pydantic_core import Url
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnvironment = Literal["production", "development"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,  # we leave the loading of an env file to uvicorn
        env_prefix="APP_",
    )
    environment: AppEnvironment = "production"
    project_folder: Path = (Path(__file__).parent / ".." / "..").resolve()
    astro_dev_url: Url = Url("http://localhost:4321")
    astro_build_folder: Path = (Path(__file__).parent / ".." / ".." / "dist").resolve()


@functools.cache  # we'll have to clear that cache when we run our tests
def get_settings() -> Settings:
    return Settings()

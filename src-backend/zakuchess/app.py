from __future__ import annotations

import logging

from fastapi import FastAPI

from .http.response import AstroPageProxyResponse
from .logging import setup_logging
from .settings import get_settings

_logger = logging.getLogger(__name__)

app = FastAPI()

settings = get_settings()
setup_logging(settings.environment)

_logger.info("Starting server with environment: %s", settings.environment)

match settings.environment:
    case "production":
        from starlette.staticfiles import StaticFiles

        astro_static_path = settings.astro_build_folder / "_astro"
        app.mount(
            "/_astro", StaticFiles(directory=astro_static_path), name="astro-static"
        )
    case "development":
        from starlette.staticfiles import StaticFiles

        astro_assets_path = settings.project_folder / "public" / "assets"
        app.mount(
            "/assets", StaticFiles(directory=astro_assets_path), name="astro-assets"
        )


@app.get("/")
def read_root():
    return AstroPageProxyResponse("/")

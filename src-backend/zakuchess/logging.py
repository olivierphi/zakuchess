from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .settings import AppEnvironment


def setup_logging(environment: "AppEnvironment") -> None:
    try:
        from uvicorn.logging import ColourizedFormatter

        formatter = ColourizedFormatter(fmt="%(levelprefix)s [%(name)s] %(message)s")
    except ImportError:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    logging_level = logging.DEBUG if environment == "development" else logging.INFO

    # Create and configure stdout handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(logging_level)

    # Configure the root logger for zakuchess.*
    app_logger = logging.getLogger("zakuchess")
    app_logger.setLevel(logging_level)
    app_logger.addHandler(stdout_handler)

    # Prevent propagation to root logger to avoid duplicate logs
    app_logger.propagate = False

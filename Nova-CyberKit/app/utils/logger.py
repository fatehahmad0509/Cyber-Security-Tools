"""Central logging configuration."""
from __future__ import annotations

import logging
import sys

from app.config import settings


def setup_logging() -> None:
    """Set up a consistent log format across the application."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    # Reduce the log level of noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

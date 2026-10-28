"""Holehe integration: finds the sites where an email address is registered.

Holehe is a library that runs on `trio`, while this project runs on asyncio
(aiogram). Therefore holehe's trio loop is run synchronously in a separate
thread (`asyncio.to_thread`); this is the same approach holehe's own CLI
(`maincore`) takes.
"""
from __future__ import annotations

import asyncio

import httpx
import trio
from holehe.core import get_functions, import_submodules, is_email, launch_module

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class HoleheError(Exception):
    pass


class _Args:
    """Minimal args object expected by holehe.core.get_functions."""

    nopasswordrecovery = False


async def _run_holehe_trio(email: str, timeout: float) -> list[dict]:
    modules = import_submodules("holehe.modules")
    websites = get_functions(modules, _Args())

    out: list[dict] = []
    async with httpx.AsyncClient(timeout=timeout) as client:
        async with trio.open_nursery() as nursery:
            for website in websites:
                nursery.start_soon(launch_module, website, email, client, out)

    return sorted(out, key=lambda i: i["name"])


def _run_holehe_sync(email: str, timeout: float) -> list[dict]:
    return trio.run(_run_holehe_trio, email, timeout)


async def check_email(email: str) -> list[dict]:
    """Return the sites where the given email address was detected as registered.

    Each result dict contains: name, domain, exists, rateLimit, emailrecovery,
    phoneNumber, others (see holehe.core).
    """
    email = email.strip()

    if not is_email(email):
        raise HoleheError("Enter a valid email address.")

    try:
        return await asyncio.to_thread(_run_holehe_sync, email, settings.holehe_timeout)
    except HoleheError:
        raise
    except Exception as exc:
        logger.exception("Unexpected error in Holehe query")
        raise HoleheError("Could not run the Holehe query.") from exc

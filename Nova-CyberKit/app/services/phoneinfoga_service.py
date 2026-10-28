"""PhoneInfoga service: OSINT scan for a phone number.

Runs the `phoneinfoga` (Go) CLI installed on the system as a subprocess.
See the "PhoneInfoga Setup" section of the README for installation.
"""
from __future__ import annotations

import re

from app.config import settings
from app.utils.logger import get_logger
from app.utils.subprocess_tools import SubprocessError, run_subprocess

logger = get_logger(__name__)

# Restricted to the characters that can appear in international/E.164
# phone numbers; an allowlist approach is used so that no other CLI flag
# can be injected, even through whitespace.
_ALLOWED_NUMBER_RE = re.compile(r"^[0-9+()\-\s]{3,32}$")


class PhoneInfogaError(Exception):
    pass


async def scan_number(number: str) -> str:
    """Run `phoneinfoga scan -n <number>` for the given phone number."""
    number = number.strip()

    if not number or not _ALLOWED_NUMBER_RE.match(number):
        raise PhoneInfogaError(
            "Invalid phone number format. Enter it in international format "
            "(e.g. +905551234567)."
        )

    cmd = [settings.phoneinfoga_binary, "scan", "-n", number]

    try:
        return await run_subprocess(cmd, timeout=settings.phoneinfoga_timeout)
    except SubprocessError as exc:
        logger.error("PhoneInfoga execution error: %s", exc)
        raise PhoneInfogaError(str(exc)) from exc

"""Pwned Passwords service (Have I Been Pwned k-anonymity API).

No API key required. Thanks to the k-anonymity model, only the first 5
characters of the password's SHA-1 hash are sent to the server; neither the
plain-text password nor the full hash is sent out or logged.
"""
from __future__ import annotations

import hashlib

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PwnedPasswordError(Exception):
    pass


async def check_password(password: str) -> int:
    """Return how many times the given password appears in known data breaches.

    A return value of 0 means the password was not found in the HIBP dataset.
    """
    if not password:
        raise PwnedPasswordError("An empty password cannot be queried.")

    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]

    url = f"{settings.pwnedpasswords_base_url}/{prefix}"
    headers = {
        # Fake padding lines recommended by HIBP, to make it harder for the
        # server to distinguish the real match through traffic analysis.
        "Add-Padding": "true",
        "User-Agent": "Nova-CyberKit-OSINT-Bot",
    }

    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        try:
            r = await client.get(url, headers=headers)
            r.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("Pwned Passwords query error: %s", exc)
            raise PwnedPasswordError("Could not reach the Pwned Passwords service.") from exc

    for line in r.text.splitlines():
        if ":" not in line:
            continue
        line_suffix, _, count_str = line.partition(":")
        if line_suffix.strip() == suffix:
            try:
                return int(count_str.strip())
            except ValueError:
                return 0

    return 0

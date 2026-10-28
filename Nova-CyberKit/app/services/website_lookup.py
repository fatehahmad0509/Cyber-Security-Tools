"""Combined website analysis using a BuiltWith lookup and Nova Web Secure."""
from __future__ import annotations

import asyncio

import httpx

from app.config import settings
from app.services.nova_web_secure import NovaWebSecureError, analyze_website
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def get_builtwith_info(domain: str) -> dict | None:
    """Fetch the technologies in use via the BuiltWith Domain API.

    Returns None if no API key is set (the feature is skipped).
    """
    if not settings.builtwith_api_key:
        return None

    params = {"KEY": settings.builtwith_api_key, "LOOKUP": domain}

    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        try:
            response = await client.get(settings.builtwith_base_url, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("BuiltWith request failed: %s", exc)
            return None

    data = response.json()

    technologies: list[str] = []
    try:
        for result in data.get("Results", []):
            for path in result.get("Result", {}).get("Paths", []):
                for tech in path.get("Technologies", []):
                    name = tech.get("Name")
                    if name and name not in technologies:
                        technologies.append(name)
    except Exception:  # pragma: no cover - defensive code
        logger.exception("Could not parse BuiltWith response")
        return None

    return {"technologies": technologies[:25]}


async def analyze_full(url: str, domain: str) -> dict:
    """Gather Nova Web Secure + BuiltWith results in parallel."""
    nova_task = analyze_website(url)
    builtwith_task = get_builtwith_info(domain)

    nova_result: dict | None = None
    nova_error: str | None = None
    builtwith_result: dict | None = None

    results = await asyncio.gather(nova_task, builtwith_task, return_exceptions=True)

    nova_raw, builtwith_raw = results

    if isinstance(nova_raw, NovaWebSecureError):
        nova_error = str(nova_raw)
    elif isinstance(nova_raw, Exception):
        logger.exception("Nova Web Secure unexpected error", exc_info=nova_raw)
        nova_error = "An unexpected error occurred."
    else:
        nova_result = nova_raw

    if isinstance(builtwith_raw, Exception):
        logger.exception("BuiltWith unexpected error", exc_info=builtwith_raw)
        builtwith_result = None
    else:
        builtwith_result = builtwith_raw

    return {
        "nova_web_secure": nova_result,
        "nova_web_secure_error": nova_error,
        "builtwith": builtwith_result,
    }

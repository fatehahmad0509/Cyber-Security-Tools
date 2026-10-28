"""Nova Web Secure integration.

Nova Web Secure is a FastAPI service developed by the user
(see nova_web_secure_service/Nova_Web_Secure.py). This module calls that
service's analysis logic directly from the same process, without requiring
a separate deployment; this way `python main.py` alone is enough.

Backward compatibility: those who want to run the service separately can
still start it with `uvicorn Nova_Web_Secure:app` and make HTTP calls via
NOVA_WEB_SECURE_URL; however, this is no longer required.
"""
from __future__ import annotations

import asyncio
import json
import os
from urllib.parse import urlparse

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NovaWebSecureError(Exception):
    pass


# --- Direct (in-process) call path ---------------------------------------

_nws_module = None


def _get_nws_module():
    """Lazily load the nova_web_secure_service.Nova_Web_Secure module.

    The module runs `load_dotenv()` and the `genai.Client` setup at import
    time; therefore it is only loaded when needed.
    """
    global _nws_module
    if _nws_module is None:
        try:
            import nova_web_secure_service.Nova_Web_Secure as nws  # noqa: F401
        except Exception as exc:
            raise RuntimeError(
                "Could not load the nova_web_secure_service.Nova_Web_Secure module: "
                f"{exc}"
            ) from exc
        _nws_module = nws
    return _nws_module


async def _analyze_in_process(url: str) -> dict:
    """Run the Nova Web Secure analysis in the same process.

    Since `Nova_Web_Secure.analyze_url` performs synchronous I/O (requests)
    and blocking socket operations, we run it on a separate worker thread
    to avoid blocking the event loop.
    """
    nws = _get_nws_module()
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(None, nws.analyze_url, url)
    except RuntimeError as exc:
        raise NovaWebSecureError(str(exc)) from exc
    except Exception as exc:
        logger.exception("Nova Web Secure unexpected error: %s", exc)
        raise NovaWebSecureError("Nova Web Secure returned an unexpected error.") from exc


# --- HTTP (remote service) call path ------------------------------------------

async def _analyze_via_http(url: str) -> dict:
    """Call the service over HTTP if NOVA_WEB_SECURE_URL is set.

    If the setting is not at its default value (the user explicitly entered
    an address), the HTTP path is preferred; this way, those who run the
    service on a separate machine keep the existing behavior.
    """
    payload = {"url": url}

    async with httpx.AsyncClient(timeout=settings.nova_web_secure_timeout) as client:
        try:
            response = await client.post(settings.nova_web_secure_url, json=payload)
            response.raise_for_status()
        except httpx.ConnectError as exc:
            logger.error("Could not connect to the Nova Web Secure service: %s", exc)
            raise NovaWebSecureError(
                "Could not reach the Nova Web Secure service. Make sure the service "
                "is running (NOVA_WEB_SECURE_URL) or remove the setting to enable "
                "in-process use."
            ) from exc
        except httpx.HTTPStatusError as exc:
            logger.error("Nova Web Secure returned an error: %s", exc)
            detail = ""
            try:
                detail = exc.response.json().get("detail", "")
            except Exception:
                pass
            raise NovaWebSecureError(detail or "Nova Web Secure returned an error.") from exc
        except httpx.HTTPError as exc:
            logger.error("Nova Web Secure request failed: %s", exc)
            raise NovaWebSecureError("Nova Web Secure request failed.") from exc

    return response.json()


# --- Common API --------------------------------------------------------------

async def analyze_website(url: str) -> dict:
    """Return a security analysis for a URL.

    The returned dict (per the service's own output) contains these fields:
    score, risk, summary, strengths, weaknesses, recommendations, reasoning

    If the user has explicitly set NOVA_WEB_SECURE_URL to a non-default
    value, the HTTP path is used; otherwise the analysis runs in the same
    process, with no separate deployment required.
    """
    default = "http://localhost:8000/analyze"
    if settings.nova_web_secure_url and settings.nova_web_secure_url != default:
        return await _analyze_via_http(url)
    return await _analyze_in_process(url)

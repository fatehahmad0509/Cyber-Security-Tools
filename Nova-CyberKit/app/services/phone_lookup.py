"""Phone number lookup service (veriphone.io).
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PhoneLookupError(Exception):
    pass


async def get_phone_info(number: str) -> dict:
    if not settings.phone_lookup_api_key:
        raise PhoneLookupError(
            "PHONE_LOOKUP_API_KEY is not set. Please add a veriphone.io "
            "key to your .env file."
        )

    url = settings.phone_lookup_base_url
    params = {"key": settings.phone_lookup_api_key, "phone": number}

    async with httpx.AsyncClient(timeout=settings.request_timeout, follow_redirects=True) as client:
        try:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
        except httpx.HTTPError as exc:
            logger.error("veriphone query error: %s", exc)
            raise PhoneLookupError("Could not reach the phone lookup service.") from exc

    if data.get("phone") is None:
        return {
            "number": number,
            "valid": "No",
            "country": "Unknown",
            "operator": "Unknown",
            "region": "Unknown",
        }

    return {
        "number": data.get("phone", number),
        "valid": "Yes",
        "country": data.get("country", "Unknown"),
        "operator": data.get("carrier", "Unknown"),
        "region": data.get("location", "Unknown"),
    }




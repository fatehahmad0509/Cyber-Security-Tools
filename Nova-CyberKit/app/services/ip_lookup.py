"""IP / hostname geolocation lookup service via ip-api.com."""
from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_FIELDS = "status,message,country,regionName,city,isp,org,as,lat,lon,timezone,query"


@dataclass
class IpLookupError(Exception):
    message: str

    def __str__(self) -> str:  # pragma: no cover
        return self.message


async def get_ip_info(query: str) -> dict:
    """Return location/ISP info for an IP address or hostname.

    Raises IpLookupError on failure.
    """
    url = f"{settings.ipapi_base_url}/{query}"

    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        try:
            response = await client.get(url, params={"fields": _FIELDS})
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("ip-api request failed: %s", exc)
            raise IpLookupError("Could not reach the IP service.") from exc

    data = response.json()

    if data.get("status") != "success":
        raise IpLookupError(data.get("message") or "Query failed.")

    return {
        "target": data.get("query"),
        "country": data.get("country") or "Unknown",
        "region": data.get("regionName") or "Unknown",
        "city": data.get("city") or "Unknown",
        "isp": data.get("isp") or "Unknown",
        "organization": data.get("org") or "Unknown",
        "asn": data.get("as") or "Unknown",
        "latitude": data.get("lat"),
        "longitude": data.get("lon"),
        "timezone": data.get("timezone") or "Unknown",
    }

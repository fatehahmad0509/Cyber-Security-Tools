"""Username lookup service: Sherlock + WhatsMyName.

Sherlock: the `sherlock` command-line tool installed as a pip package is run
as a subprocess and the found accounts are parsed.

WhatsMyName: a direct HTTP request is made for each site using the
WebBreacher/WhatsMyName dataset. The existence (e_code/e_string) and
non-existence (m_code/m_string) conditions are evaluated together.
"""
from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_WMN_DATA_PATH = Path(__file__).parent / "data" / "wmn-data.json"
_FOUND_LINE_RE = re.compile(r"^\[\+\]\s*([^:]+):\s*(\S+)\s*$")

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


class UsernameLookupError(Exception):
    pass


# ---------------------------------------------------------------------------
# Sherlock
# ---------------------------------------------------------------------------

async def _run_sherlock(username: str) -> list[dict]:
    """Run the Sherlock CLI as a subprocess and return the accounts found."""
    cmd = [
        "sherlock",
        username,
        "--print-found",
        "--no-color",
        "--no-txt",
        "--timeout",
        str(settings.username_lookup_timeout),
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(
            proc.communicate(), timeout=settings.sherlock_timeout
        )
    except FileNotFoundError:
        logger.error("sherlock command not found. Was requirements.txt installed?")
        return []
    except asyncio.TimeoutError:
        logger.warning("Sherlock timed out (username=%s)", username)
        try:
            proc.kill()
        except Exception:
            pass
        return []

    found: list[dict] = []
    for raw_line in stdout.decode(errors="ignore").splitlines():
        match = _FOUND_LINE_RE.match(raw_line.strip())
        if match:
            found.append({"platform": match.group(1).strip(), "url": match.group(2).strip()})

    return found


# ---------------------------------------------------------------------------
# WhatsMyName
# ---------------------------------------------------------------------------

def _load_wmn_sites() -> list[dict]:
    with _WMN_DATA_PATH.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("sites", [])


_WMN_SITES_CACHE: list[dict] | None = None


def _get_wmn_sites() -> list[dict]:
    global _WMN_SITES_CACHE
    if _WMN_SITES_CACHE is None:
        _WMN_SITES_CACHE = _load_wmn_sites()
    return _WMN_SITES_CACHE


async def _run_whatsmyname(username: str) -> list[dict]:
    """Run concurrent checks for the sites in the WhatsMyName dataset.

    For each site, the non-existence condition (m_code/m_string) is checked
    first; if it does not match, the existence condition (e_code/e_string)
    is checked.
    """
    sites = _get_wmn_sites()
    semaphore = asyncio.Semaphore(settings.username_lookup_concurrency)

    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        tasks = [_check_one_site(client, site, username, semaphore) for site in sites]
        results = await asyncio.gather(*tasks, return_exceptions=False)

    return [r for r in results if r is not None]


async def _check_one_site(
    client: httpx.AsyncClient, site: dict, username: str, semaphore: asyncio.Semaphore
) -> dict | None:
    uri = site.get("uri_check", "")
    if "{account}" not in uri:
        return None

    check_url = uri.replace("{account}", username)

    async with semaphore:
        try:
            response = await client.get(
                check_url,
                headers={"User-Agent": _USER_AGENT},
            )
        except Exception:
            return None

    # If there is a non-existence condition (m_code / m_string), check it first
    m_code = site.get("m_code")
    m_string = site.get("m_string") or ""
    if m_code is not None and m_string:
        if response.status_code == m_code and m_string in response.text:
            return None

    # Existence condition (e_code / e_string)
    e_code = site.get("e_code")
    e_string = site.get("e_string") or ""
    if e_code is not None and response.status_code == e_code:
        if not e_string or e_string in response.text:
            return {"platform": site.get("name", "?"), "url": check_url}

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def lookup_username(username: str) -> dict:
    """Combine the Sherlock and WhatsMyName results.

    Returned dict: {"sherlock": [...], "whatsmyname": [...], "sherlock_total": int, "whatsmyname_total": int}
    """
    sherlock_results, wmn_results = await asyncio.gather(
        _run_sherlock(username),
        _run_whatsmyname(username),
        return_exceptions=True,
    )

    if isinstance(sherlock_results, Exception):
        logger.exception("Sherlock unexpected error", exc_info=sherlock_results)
        sherlock_results = []

    if isinstance(wmn_results, Exception):
        logger.exception("WhatsMyName unexpected error", exc_info=wmn_results)
        wmn_results = []

    max_results = settings.username_lookup_max_results

    return {
        "sherlock": sherlock_results[:max_results],
        "sherlock_total": len(sherlock_results),
        "whatsmyname": wmn_results[:max_results],
        "whatsmyname_total": len(wmn_results),
    }

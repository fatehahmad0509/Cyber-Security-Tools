"""DuckDuckGo web search service (duckduckgo-search / ddgs library)."""
from __future__ import annotations

import asyncio

from ddgs import DDGS

from app.utils.logger import get_logger

logger = get_logger(__name__)


class SearchError(Exception):
    pass


def _search_sync(query: str, max_results: int) -> list[dict]:
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))


async def search(query: str, max_results: int = 5) -> list[dict]:
    """Search DuckDuckGo and return the top results.

    Each raw result: {"title": ..., "href": ..., "body": ...}
    """
    try:
        raw_results = await asyncio.to_thread(_search_sync, query, max_results)
    except Exception as exc:
        logger.error("DuckDuckGo search failed: %s", exc)
        raise SearchError("An error occurred during the search.") from exc

    return [
        {
            "title": item.get("title", ""),
            "link": item.get("href", ""),
            "summary": item.get("body", ""),
        }
        for item in raw_results
    ]

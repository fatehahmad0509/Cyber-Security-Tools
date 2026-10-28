"""/search command."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.services.duckduckgo import SearchError, search
from app.utils.logger import get_logger

router = Router(name="search")
logger = get_logger(__name__)


@router.message(Command("search"))
async def cmd_search(message: Message, command: CommandObject) -> None:
    query = (command.args or "").strip()

    if not query:
        await message.answer("Usage: <code>/search search phrase</code>")
        return

    status_msg = await message.answer("🔎 Searching DuckDuckGo...")

    try:
        results = await search(query, max_results=5)
    except SearchError as exc:
        await status_msg.edit_text(f"❌ Error: {exc}")
        return
    except Exception:
        logger.exception("Unexpected error during search")
        await status_msg.edit_text("❌ An unexpected error occurred.")
        return

    if not results:
        await status_msg.edit_text("No results found.")
        return

    lines = [f"🔎 <b>Search Results</b> — <i>{query}</i>\n"]
    for item in results:
        lines.append(f"<b>{item['title']}</b>\n{item['link']}\n{item['summary']}\n")

    await status_msg.edit_text("\n".join(lines), disable_web_page_preview=True)

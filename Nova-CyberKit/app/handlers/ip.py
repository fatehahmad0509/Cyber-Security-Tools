"""/ip command."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.services.ip_lookup import IpLookupError, get_ip_info
from app.utils.logger import get_logger

router = Router(name="ip")
logger = get_logger(__name__)


@router.message(Command("ip"))
async def cmd_ip(message: Message, command: CommandObject) -> None:
    query = (command.args or "").strip()

    if not query:
        await message.answer(
            "Usage: <code>/ip 8.8.8.8</code> or <code>/ip example.com</code>"
        )
        return

    status_msg = await message.answer("🔎 Querying...")

    try:
        info = await get_ip_info(query)
    except IpLookupError as exc:
        await status_msg.edit_text(f"❌ Error: {exc}")
        return
    except Exception:
        logger.exception("Unexpected error in IP query")
        await status_msg.edit_text("❌ An unexpected error occurred.")
        return

    text = (
        f"🌐 <b>IP / Host Info</b> — <code>{info['target']}</code>\n\n"
        f"🌍 <b>Country:</b> {info['country']}\n"
        f"📍 <b>Region:</b> {info['region']}\n"
        f"🏙️ <b>City:</b> {info['city']}\n"
        f"📡 <b>ISP:</b> {info['isp']}\n"
        f"🏢 <b>Organization:</b> {info['organization']}\n"
        f"🔢 <b>ASN:</b> {info['asn']}\n"
        f"↕️ <b>Latitude:</b> {info['latitude']}\n"
        f"↔️ <b>Longitude:</b> {info['longitude']}\n"
        f"🕒 <b>Timezone:</b> {info['timezone']}"
    )

    await status_msg.edit_text(text)

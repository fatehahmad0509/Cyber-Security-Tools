"""/phone command."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.services.phone_lookup import PhoneLookupError, get_phone_info
from app.utils.logger import get_logger

router = Router(name="phone")
logger = get_logger(__name__)


@router.message(Command("phone"))
async def cmd_phone(message: Message, command: CommandObject) -> None:
    number = (command.args or "").strip()

    if not number:
        await message.answer(
            "Usage: <code>/phone +905551234567</code> (enter in international format)"
        )
        return

    status_msg = await message.answer("🔎 Querying...")

    try:
        info = await get_phone_info(number)
    except PhoneLookupError as exc:
        await status_msg.edit_text(f"❌ Error: {exc}")
        return
    except Exception:
        logger.exception("Unexpected error in phone query")
        await status_msg.edit_text("❌ An unexpected error occurred.")
        return

    text = (
        f"📞 <b>Phone Info</b> — <code>{info['number']}</code>\n\n"
        f"✅ <b>Valid:</b> {info['valid']}\n"
        f"🌍 <b>Country:</b> {info['country']}\n"
        f"📡 <b>Carrier:</b> {info['operator']}\n"
        f"📍 <b>Region:</b> {info['region']}"
    )

    await status_msg.edit_text(text)

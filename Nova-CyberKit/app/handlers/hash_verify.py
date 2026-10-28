"""/verify command - compares a hash with plain text."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.services.hash_generator import verify_hash
from app.utils.logger import get_logger

router = Router(name="hash_verify")
logger = get_logger(__name__)


@router.message(Command("verify"))
async def cmd_verify(message: Message, command: CommandObject) -> None:
    args = (command.args or "").strip()

    if not args or " " not in args:
        await message.answer(
            "Usage: <code>/verify &lt;hash&gt; &lt;plain_text&gt;</code>\n"
            "Example: <code>/verify 5d41402abc4b2a76b9719d911017c592 hello</code>"
        )
        return

    parts = args.split(maxsplit=1)
    target_hash = parts[0].strip()
    plain_text = parts[1].strip()

    if len(plain_text) > 2048:
        await message.answer("❌ Text is too long (maximum 2048 characters).")
        return

    status_msg = await message.answer("🔎 Verifying hash...")

    try:
        result = verify_hash(plain_text, target_hash)
    except Exception:
        logger.exception("Hash verification error")
        await status_msg.edit_text("❌ An error occurred while verifying the hash.")
        return

    detected = f" (<code>{result.algorithm}</code>)" if result.algorithm else ""

    if result.is_match:
        await status_msg.edit_text(
            f"✅ <b>MATCH FOUND</b>\n\n"
            f"<b>Algorithm:</b> <code>{result.algorithm}</code>\n"
            f"<b>Hash:</b> <code>{target_hash}</code>\n"
            f"<b>Text:</b> <code>{plain_text[:128]}</code>"
        )
    else:
        await status_msg.edit_text(
            f"❌ <b>NO MATCH</b>\n\n"
            f"The given hash does not match the text's hash under any algorithm.\n\n"
            f"<b>Hash:</b> <code>{target_hash}</code>{detected}\n"
            f"<b>Text:</b> <code>{plain_text[:128]}</code>"
        )

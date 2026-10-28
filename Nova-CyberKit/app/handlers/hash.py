"""/hash command."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.services.hash_generator import (
    generate_argon2,
    generate_bcrypt,
    generate_hashes,
    generate_md5,
    generate_sha1,
    generate_sha256,
    generate_sha512,
)
from app.utils.logger import get_logger

router = Router(name="hash")
logger = get_logger(__name__)

_ALGO_MAP = {
    "md5": ("MD5", generate_md5),
    "sha1": ("SHA-1", generate_sha1),
    "sha256": ("SHA-256", generate_sha256),
    "sha512": ("SHA-512", generate_sha512),
    "bcrypt": ("Bcrypt", generate_bcrypt),
    "argon2": ("Argon2", generate_argon2),
}


@router.message(Command("hash"))
async def cmd_hash(message: Message, command: CommandObject) -> None:
    args = (command.args or "").strip()

    if not args:
        lines = [
            "Usage:",
            "<code>/hash hello</code> (MD5, SHA-1, SHA-256, SHA-512)",
        ]
        for name in _ALGO_MAP:
            lines.append(f"<code>/hash {name} hello</code>")
        await message.answer("\n".join(lines))
        return

    parts = args.split(maxsplit=1)
    algo_key = parts[0].lower()
    text: str

    if algo_key in _ALGO_MAP:
        if len(parts) < 2:
            await message.answer(f"Usage: <code>/hash {algo_key} &lt;text&gt;</code>")
            return
        text = parts[1]
    else:
        algo_key = "all"
        text = args

    if len(text) > 2048:
        await message.answer("❌ Text is too long (maximum 2048 characters).")
        return

    status_msg = await message.answer("🔎 Calculating hash...")

    try:
        if algo_key == "all":
            result = generate_hashes(text)
            payload = result.format_message(text)
        else:
            label, fn = _ALGO_MAP[algo_key]
            h = fn(text)
            payload = f"<b>🔐 {label} Hash</b>\n\n<code>{h}</code>"
    except Exception:
        logger.exception("Hash calculation error")
        await status_msg.edit_text("❌ An error occurred while calculating the hash.")
        return

    await status_msg.edit_text(payload)

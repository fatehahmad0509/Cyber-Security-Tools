"""/password command."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.services.password_generator import (
    MAX_LENGTH,
    MIN_LENGTH,
    generate_password,
    format_password_message,
)
from app.utils.logger import get_logger

router = Router(name="password")
logger = get_logger(__name__)


@router.message(Command("password"))
async def cmd_password(message: Message, command: CommandObject) -> None:
    arg = (command.args or "").strip()

    length = 16
    if arg:
        try:
            parsed = int(arg)
            if parsed < MIN_LENGTH or parsed > MAX_LENGTH:
                await message.answer(
                    f"❌ Length must be between {MIN_LENGTH} and {MAX_LENGTH}."
                )
                return
            length = parsed
        except ValueError:
            await message.answer(
                "Usage: <code>/password</code> (default 16)\n"
                "or: <code>/password 24</code> (custom length)"
            )
            return

    try:
        password = generate_password(length=length)
    except Exception:
        logger.exception("Password generation error")
        await message.answer("❌ An error occurred while generating the password.")
        return

    await message.answer(format_password_message(password, length))

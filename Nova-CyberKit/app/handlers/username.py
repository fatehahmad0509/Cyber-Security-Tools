"""/username command - redirects to whatsmyname.me."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

router = Router(name="username")


@router.message(Command("username"))
async def cmd_username(message: Message, command: CommandObject) -> None:
    username = (command.args or "").strip()

    if not username or " " in username:
        await message.answer("Usage: <code>/username someusername</code>")
        return

    url = f"https://whatsmyname.me?q={username}"
    await message.answer(
        f"🔗 <b>WhatsMyName</b>\n"
        f"Search for the username at this address: <code>{username}</code>\n\n"
        f"{url}",
        disable_web_page_preview=False,
    )

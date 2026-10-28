"""/pwnedpassword command."""
from __future__ import annotations

from html import escape as _html_escape

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.services.pwned_service import PwnedPasswordError, check_password
from app.utils.logger import get_logger

router = Router(name="pwnedpassword")
logger = get_logger(__name__)


def _mask(password: str) -> str:
    """Mask the password so it is not shown repeatedly in plain text in messages.

    Keeps only the first and last character; being distinguishable is
    enough, there is no need to carry the password itself.
    """
    if len(password) <= 2:
        return "*" * len(password)
    return password[0] + "*" * (len(password) - 2) + password[-1]


@router.message(Command("pwnedpassword"))
async def cmd_pwnedpassword(message: Message, command: CommandObject) -> None:
    password = (command.args or "").strip()

    if not password:
        await message.answer(
            "Usage: <code>/pwnedpassword yourpassword</code>\n"
            "The password is checked against the Have I Been Pwned k-anonymity API by sending only its hash's "
            "first 5 characters; the plain text never leaves the bot."
        )
        return

    # Masked display: if different passwords are queried back to back, it is
    # clear which result belongs to which password, but the plain-text
    # password is not shown over and over in messages.
    masked = _html_escape(_mask(password))
    status_msg = await message.answer(f"🔎 Querying <code>{masked}</code>...")

    try:
        count = await check_password(password)
    except PwnedPasswordError as exc:
        await status_msg.edit_text(f"❌ Error: {exc}")
        return
    except Exception:
        logger.exception("Unexpected error in Pwned password query")
        await status_msg.edit_text("❌ An unexpected error occurred.")
        return

    if count > 0:
        formatted = f"{count:,}"
        text = (
            f"☠️ <b>Password found</b> — <code>{masked}</code>\n\n"
            f"Seen <b>{formatted}</b> times in known breaches.\n"
            "We recommend never using this password anywhere again."
        )
    else:
        text = (
            f"✅ <b>Password not found</b> — <code>{masked}</code>\n\n"
            "Not seen in known breaches. Still, it is recommended to use a different "
            "and strong password for every account."
        )

    text += "\n\n🔐 Note: We recommend manually deleting this message from the chat."

    await status_msg.edit_text(text)

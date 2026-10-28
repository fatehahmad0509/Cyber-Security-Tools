"""/phoneinfo command."""
from __future__ import annotations

from html import escape as _html_escape

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.services.phoneinfoga_service import PhoneInfogaError, scan_number
from app.utils.logger import get_logger
from app.utils.long_output import send_cli_output
import re
import time

router = Router(name="phoneinfo")
logger = get_logger(__name__)


@router.message(Command("phoneinfo"))
async def cmd_phoneinfo(message: Message, command: CommandObject) -> None:
    number = (command.args or "").strip()

    if not number:
        await message.answer(
            "Usage: <code>/phoneinfo +905551234567</code> (enter in international format)"
        )
        return

    # The target is written into the status message: if different numbers are
    # queried back to back (one running slowly while another is sent), the
    # message text makes it clear which result belongs to which number, so
    # results do not get mixed up.
    status_msg = await message.answer(
        f"🔎 Querying <code>{_html_escape(number)}</code> with PhoneInfoga..."
    )

    try:
        output = await scan_number(number)
    except PhoneInfogaError as exc:
        await status_msg.edit_text(f"❌ Error: {exc}")
        return
    except Exception:
        logger.exception("Unexpected error in PhoneInfoga query")
        await status_msg.edit_text("❌ An unexpected error occurred.")
        return

    suffix = re.sub(r"\D", "", number)[-4:] or "x"
    await send_cli_output(
        status_msg,
        output,
        filename=f"phoneinfoga_{suffix}_{int(time.time())}.txt",
        empty_message="PhoneInfoga produced no output.",
    )

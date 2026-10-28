"""/nmap command."""
from __future__ import annotations
import re
import time

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from html import escape as _html_escape

from app.config import settings
from app.services.nmap_service import NmapError, scan_target
from app.utils.logger import get_logger
from app.utils.long_output import send_cli_output

router = Router(name="nmap")
logger = get_logger(__name__)


@router.message(Command("nmap"))
async def cmd_nmap(message: Message, command: CommandObject) -> None:
    target = (command.args or "").strip()

    if not target:
        flags = "-Pn -sT -sV -O" if settings.nmap_os_detection else "-Pn -sT -sV"
        await message.answer(
            "Usage: <code>/nmap 8.8.8.8</code> or <code>/nmap example.com</code>\n"
            f"Runs <code>nmap {flags} &lt;target&gt;</code> in the background "
            "(no raw socket required, also works in containerized environments).\n"
            "⚠️ Only use on systems you are authorized to scan."
        )
        return

    # The target is written into the status message: if different targets are
    # scanned back to back (one running slowly while another is sent), the
    # message text makes it clear which result belongs to which target, so
    # results do not get mixed up.
    status_msg = await message.answer(
        f"🔎 nmap scan started for <code>{_html_escape(target)}</code> "
        "(port + service detection)...\nThis may take a few minutes."
    )

    try:
        output = await scan_target(target)
    except NmapError as exc:
        await status_msg.edit_text(f"❌ Error: {exc}")
        return
    except Exception:
        logger.exception("Unexpected error in Nmap scan")
        await status_msg.edit_text("❌ An unexpected error occurred.")
        return

    safe_target = re.sub(r"[^A-Za-z0-9.-]", "_", target)[:40]
    await send_cli_output(
        status_msg,
        output,
        filename=f"nmap_{safe_target}_{int(time.time())}.txt",
        empty_message="Nmap produced no output.",
    )

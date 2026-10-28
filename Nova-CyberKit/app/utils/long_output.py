"""Helper for sending long CLI output (nmap, phoneinfoga, ...) to Telegram.

Telegram message text is limited to ~4096 characters. For output that
approaches this limit, we send the result as a .txt file so that
readability is not compromised.
"""
from __future__ import annotations

from html import escape as _html_escape

from aiogram.types import BufferedInputFile, Message

_TELEGRAM_TEXT_LIMIT = 3500


async def send_cli_output(
    status_message: Message,
    text: str,
    *,
    filename: str,
    empty_message: str = "No output received (empty response).",
) -> None:
    """Send the raw text output of a CLI tool via `status_message`.

    Short output is shown inside a <pre> block; long output is attached
    as a .txt file.
    """
    cleaned = text.strip()

    if not cleaned:
        await status_message.edit_text(empty_message)
        return

    if len(cleaned) <= _TELEGRAM_TEXT_LIMIT:
        await status_message.edit_text(f"<pre>{_html_escape(cleaned)}</pre>")
        return

    document = BufferedInputFile(cleaned.encode("utf-8"), filename=filename)
    await status_message.edit_text(
        "📄 Output is long, sending it as a file..."
    )
    await status_message.answer_document(document)

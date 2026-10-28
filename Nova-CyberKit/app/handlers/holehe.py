"""/holehe command."""
from __future__ import annotations

from html import escape as _html_escape

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.services.holehe_service import HoleheError, check_email
from app.utils.logger import get_logger

router = Router(name="holehe")
logger = get_logger(__name__)

_MAX_LISTED = 40


@router.message(Command("holehe"))
async def cmd_holehe(message: Message, command: CommandObject) -> None:
    email = (command.args or "").strip()

    if not email:
        await message.answer("Usage: <code>/holehe email@example.com</code>")
        return

    # The target is written into the status message: if different emails are
    # queried back to back (one running slowly while another is sent), the
    # message text makes it clear which result belongs to which email, so
    # results do not get mixed up.
    status_msg = await message.answer(
        f"🔎 <code>{_html_escape(email)}</code> is being queried... (this may take a while)"
    )

    try:
        results = await check_email(email)
    except HoleheError as exc:
        await status_msg.edit_text(f"❌ Error: {exc}")
        return
    except Exception:
        logger.exception("Unexpected error in Holehe query")
        await status_msg.edit_text("❌ An unexpected error occurred.")
        return

    used = [r for r in results if r.get("exists")]
    rate_limited = [r for r in results if r.get("rateLimit")]

    lines = [f"📧 <b>Holehe Results</b> — <code>{_html_escape(email)}</code>\n"]

    if used:
        lines.append(f"✅ <b>Registered sites found ({len(used)}):</b>")
        for r in used[:_MAX_LISTED]:
            extra = ""
            if r.get("emailrecovery"):
                extra += f" — recovery: {_html_escape(str(r['emailrecovery']))}"
            if r.get("phoneNumber"):
                extra += f" — phone: {_html_escape(str(r['phoneNumber']))}"
            lines.append(f"• {_html_escape(str(r['domain']))}{extra}")
        if len(used) > _MAX_LISTED:
            lines.append(f"… and {len(used) - _MAX_LISTED} more sites.")
    else:
        lines.append("No sites were found where the email is registered.")

    lines.append(f"\n🔍 {len(results)} sites checked in total.")
    if rate_limited:
        lines.append(
            f"⚠️ {len(rate_limited)} sites could not be checked "
            "due to rate limiting."
        )

    await status_msg.edit_text("\n".join(lines))

"""/website command."""
from __future__ import annotations

from urllib.parse import urlparse

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.services.website_lookup import analyze_full
from app.utils.logger import get_logger

router = Router(name="website")
logger = get_logger(__name__)


def _normalize_url(raw: str) -> str:
    raw = raw.strip()
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    return raw


@router.message(Command("website"))
async def cmd_website(message: Message, command: CommandObject) -> None:
    arg = (command.args or "").strip()

    if not arg:
        await message.answer("Usage: <code>/website example.com</code>")
        return

    url = _normalize_url(arg)
    domain = urlparse(url).hostname or arg

    status_msg = await message.answer("🔎 Analyzing site, this may take a while...")

    try:
        result = await analyze_full(url, domain)
    except Exception:
        logger.exception("Unexpected error in website analysis")
        await status_msg.edit_text("❌ An unexpected error occurred.")
        return

    lines = [f"🔒 <b>Website Analysis</b> — <code>{domain}</code>\n"]

    nova = result.get("nova_web_secure")
    nova_error = result.get("nova_web_secure_error")

    if nova:
        lines.append("<b>🛡️ Nova Web Secure</b>")
        lines.append(f"Score: <b>{nova.get('score', '—')}</b>  |  Risk: <b>{nova.get('risk', '—')}</b>")
        if nova.get("summary"):
            lines.append(f"Summary: {nova['summary']}")

        strengths = nova.get("strengths") or []
        weaknesses = nova.get("weaknesses") or []
        recommendations = nova.get("recommendations") or []

        if strengths:
            lines.append("\n✅ <b>Strengths:</b>")
            lines.extend(f"• {s}" for s in strengths[:6])

        if weaknesses:
            lines.append("\n⚠️ <b>Weaknesses:</b>")
            lines.extend(f"• {w}" for w in weaknesses[:6])

        if recommendations:
            lines.append("\n💡 <b>Recommendations:</b>")
            lines.extend(f"• {r}" for r in recommendations[:6])
    elif nova_error:
        lines.append(f"<b>🛡️ Nova Web Secure:</b> ❌ {nova_error}")

    builtwith = result.get("builtwith")
    if builtwith:
        techs = builtwith.get("technologies") or []
        lines.append("\n<b>🧩 BuiltWith Technologies</b>")
        if techs:
            lines.append(", ".join(techs))
        else:
            lines.append("No technology information found.")
    else:
        lines.append(
            "\n<b>🧩 BuiltWith:</b> Skipped (BUILTWITH_API_KEY is not set or no result was returned)."
        )

    await status_msg.edit_text("\n".join(lines))

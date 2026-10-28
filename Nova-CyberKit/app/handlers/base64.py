"""/b64encode and /b64decode commands (image/file)."""
from __future__ import annotations

import io

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import BufferedInputFile, Message

from app.services.base64_service import decode_bytes, encode_bytes
from app.utils.logger import get_logger

router = Router(name="base64")
logger = get_logger(__name__)


@router.message(Command("b64encode"))
async def cmd_b64encode(message: Message) -> None:
    reply = message.reply_to_message
    if not reply:
        await message.answer(
            "Send <code>/b64encode</code> as a reply to a message/file."
        )
        return

    status = await message.answer("⏳ Processing...")

    try:
        bot = message.bot

        if reply.text:
            data = reply.text.encode("utf-8")
        else:
            file_id = None
            # Support all file types
            if reply.photo:
                file_id = reply.photo[-1].file_id
            elif reply.document:
                file_id = reply.document.file_id
            elif reply.audio:
                file_id = reply.audio.file_id
            elif reply.voice:
                file_id = reply.voice.file_id
            elif reply.video:
                file_id = reply.video.file_id
            elif reply.video_note:
                file_id = reply.video_note.file_id
            elif reply.animation:
                file_id = reply.animation.file_id
            elif reply.sticker:
                file_id = reply.sticker.file_id

            if not file_id:
                await status.edit_text("❌ Unsupported message type.")
                return

            file = await bot.get_file(file_id)
            buf = io.BytesIO()
            await bot.download_file(file.file_path, destination=buf)
            data = buf.getvalue()
    except Exception:
        logger.exception("File download error")
        await status.edit_text("❌ An error occurred while downloading the file.")
        return

    b64_str = encode_bytes(data)

    if len(b64_str) > 4000:
        buf = io.BytesIO(b64_str.encode("utf-8"))
        buf.name = "base64.txt"
        await message.reply_document(BufferedInputFile(file=buf.read(), filename=buf.name))
    else:
        await message.reply(f"<b>Base64:</b>\n<code>{b64_str}</code>")

    await status.delete()


@router.message(Command("b64decode"))
async def cmd_b64decode(message: Message, command: CommandObject) -> None:
    b64_str = (command.args or "").strip()

    if not b64_str:
        reply = message.reply_to_message
        if reply and reply.text:
            b64_str = reply.text.strip()
        elif reply and reply.document:
            status = await message.answer("⏳ Reading file...")
            try:
                bot = message.bot
                file = await bot.get_file(reply.document.file_id)
                buf = io.BytesIO()
                await bot.download_file(file.file_path, destination=buf)
                b64_str = buf.getvalue().decode("utf-8").strip()
            except Exception:
                logger.exception("File read error")
                await status.edit_text("❌ An error occurred while reading the file.")
                return
            await status.delete()
        else:
            await message.answer(
                "Usage: <code>/b64decode &lt;base64&gt;</code>\n"
                "or reply to a base64 text with <code>/b64decode</code>"
            )
            return

    try:
        data = decode_bytes(b64_str)
    except Exception:
        logger.exception("Base64 decode error")
        await message.answer("❌ Invalid base64 input.")
        return

    ext = _guess_ext(data)
    buf = io.BytesIO(data)
    buf.name = f"decoded{ext}"
    await message.reply_document(BufferedInputFile(file=buf.read(), filename=buf.name))


def _guess_ext(data: bytes) -> str:
    if data.startswith(b"\x89PNG"):
        return ".png"
    if data.startswith(b"\xff\xd8"):
        return ".jpg"
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return ".gif"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return ".webp"
    if data.startswith(b"PK"):
        return ".zip"
    if data.startswith(b"%"):
        return ".pdf"
    return ".bin"

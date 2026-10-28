"""Simple link commands that only send the official website."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="links")

_LINKS: dict[str, tuple[str, str, str]] = {
    "facecheck": ("FaceCheck.ID", "https://facecheck.id", "Search for people using face recognition"),
    "pimeyes": ("PimEyes", "https://pimeyes.com", "Reverse face search engine"),
    "geospy": ("GeoSpy", "https://geospy.ai", "Location estimation from a photo"),
    "hive": ("Hive Moderation", "https://hivemoderation.com", "AI image/content analysis"),
    "aiornot": ("AI or Not", "https://www.aiornot.com", "Detects whether an image was AI-generated"),
    "whatsmyname": ("WhatsMyName", "https://whatsmyname.me", "Username search (Instagram, LinkedIn, etc.)"),
    "imginn": ("ImgInn", "https://imginn.com", "View Instagram profiles"),
}


def _make_handler(command_name: str):
    display_name, url, desc = _LINKS[command_name]

    async def handler(message: Message) -> None:
        await message.answer(f"🔗 <b>{display_name}</b> — {desc}\n{url}")

    return handler


for _cmd, (_name, _url, _desc) in _LINKS.items():
    router.message(Command(_cmd))(_make_handler(_cmd))

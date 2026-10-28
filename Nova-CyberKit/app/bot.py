"""Bot / Dispatcher setup."""
from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.handlers import (
    base64,
    hash,
    hash_verify,
    holehe,
    ip,
    links,
    nmap,
    password,
    phone,
    phoneinfo,
    pwnedpassword,
    search,
    start,
    username,
    website,
)
from app.middlewares.auth import WhitelistMiddleware


def create_bot() -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    # The whitelist check runs before all updates; requests from
    # unauthorized users never reach the handlers.
    dp.update.outer_middleware(WhitelistMiddleware())

    dp.include_router(base64.router)
    dp.include_router(start.router)
    dp.include_router(ip.router)
    dp.include_router(website.router)
    dp.include_router(username.router)
    dp.include_router(phone.router)
    dp.include_router(search.router)
    dp.include_router(hash.router)
    dp.include_router(hash_verify.router)
    dp.include_router(password.router)
    dp.include_router(links.router)
    dp.include_router(pwnedpassword.router)
    dp.include_router(holehe.router)
    dp.include_router(phoneinfo.router)
    dp.include_router(nmap.router)

    return dp

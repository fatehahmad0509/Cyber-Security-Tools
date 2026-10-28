"""Authorization middleware.

This bot is entirely private. No reply is ever sent to a user who is
not on the whitelist; incoming messages are silently ignored.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from app.database.crud import is_whitelisted
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WhitelistMiddleware(BaseMiddleware):
    """Check, for every incoming update, whether the sender is on the whitelist."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = self._extract_user(event)

        if user is None:
            # Updates from which no user info can be extracted (e.g. some
            # service messages) are ignored, erring on the safe side.
            return None

        allowed = await is_whitelisted(user.id)

        if not allowed:
            logger.warning(
                "Unauthorized access attempt: id=%s username=%s -> ignored",
                user.id,
                user.username,
            )
            # Per the rule: no reply is sent, the message is fully ignored.
            return None

        return await handler(event, data)

    @staticmethod
    def _extract_user(event: TelegramObject):
        if isinstance(event, Update):
            inner = event.event
            return getattr(inner, "from_user", None)
        return getattr(event, "from_user", None)

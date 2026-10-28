"""CRUD helper functions for the whitelist table."""
from __future__ import annotations

from sqlalchemy import delete, select

from app.database.engine import get_session
from app.models.whitelist import Whitelist


async def is_whitelisted(telegram_id: int) -> bool:
    """Check whether the given Telegram ID is on the whitelist."""
    async with get_session() as session:
        result = await session.execute(
            select(Whitelist.id).where(Whitelist.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none() is not None


async def add_to_whitelist(telegram_id: int, name: str | None = None) -> Whitelist:
    """Add a new user to the whitelist."""
    async with get_session() as session:
        entry = Whitelist(telegram_id=telegram_id, name=name)
        session.add(entry)
        await session.commit()
        await session.refresh(entry)
        return entry


async def remove_from_whitelist(telegram_id: int) -> bool:
    """Remove a user from the whitelist. Returns True on success."""
    async with get_session() as session:
        result = await session.execute(
            delete(Whitelist).where(Whitelist.telegram_id == telegram_id)
        )
        await session.commit()
        return result.rowcount > 0


async def list_whitelist() -> list[Whitelist]:
    """Return all entries on the whitelist."""
    async with get_session() as session:
        result = await session.execute(select(Whitelist).order_by(Whitelist.created_at))
        return list(result.scalars().all())

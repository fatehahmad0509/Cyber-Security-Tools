"""Async SQLAlchemy engine and session management."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.models.whitelist import Base

engine = create_async_engine(settings.database_url, pool_pre_ping=True, future=True)

async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def init_db() -> None:
    """Create the tables (if they do not exist). Called once at application startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Context manager that provides an async session for a single operation."""
    async with async_session_factory() as session:
        yield session

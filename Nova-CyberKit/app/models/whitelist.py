"""Whitelist table - Telegram users who are allowed to access the bot."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Whitelist(Base):
    __tablename__ = "whitelist"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Whitelist id={self.id} telegram_id={self.telegram_id} name={self.name!r}>"

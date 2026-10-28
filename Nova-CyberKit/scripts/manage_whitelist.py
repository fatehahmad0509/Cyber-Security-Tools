"""Command-line tool for managing the whitelist.

Since the bot does not reply to any user who is not on the whitelist, the
first entry (your own Telegram ID) must be added with this script.

Usage:
    python -m scripts.manage_whitelist add 123456789 "Your Name"
    python -m scripts.manage_whitelist remove 123456789
    python -m scripts.manage_whitelist list
"""
from __future__ import annotations

import asyncio
import sys

from app.database.crud import add_to_whitelist, list_whitelist, remove_from_whitelist
from app.database.engine import init_db


async def _add(telegram_id: int, name: str | None) -> None:
    await init_db()
    entry = await add_to_whitelist(telegram_id, name)
    print(f"Added: id={entry.id} telegram_id={entry.telegram_id} name={entry.name}")


async def _remove(telegram_id: int) -> None:
    await init_db()
    ok = await remove_from_whitelist(telegram_id)
    print("Removed." if ok else "Entry not found.")


async def _list() -> None:
    await init_db()
    entries = await list_whitelist()
    if not entries:
        print("Whitelist is empty.")
        return
    for entry in entries:
        print(f"{entry.telegram_id}\t{entry.name or '-'}\t{entry.created_at}")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    action = sys.argv[1]

    if action == "add":
        if len(sys.argv) < 3:
            print("Usage: manage_whitelist add <telegram_id> [name]")
            sys.exit(1)
        telegram_id = int(sys.argv[2])
        name = " ".join(sys.argv[3:]) or None
        asyncio.run(_add(telegram_id, name))

    elif action == "remove":
        if len(sys.argv) < 3:
            print("Usage: manage_whitelist remove <telegram_id>")
            sys.exit(1)
        asyncio.run(_remove(int(sys.argv[2])))

    elif action == "list":
        asyncio.run(_list())

    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()

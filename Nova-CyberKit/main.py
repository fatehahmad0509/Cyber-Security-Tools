"""Nova CyberKit entry point."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.bot import create_bot, create_dispatcher
from app.database.engine import init_db
from app.utils.logger import get_logger, setup_logging

logger = get_logger("nova_cyberkit")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Preparing database...")
    await init_db()

    bot = create_bot()
    dp = create_dispatcher()

    logger.info("Starting Nova CyberKit (polling)...")
    await bot.delete_webhook(drop_pending_updates=True)
    task = asyncio.create_task(dp.start_polling(bot))

    yield

    task.cancel()
    await bot.session.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
@app.head("/")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")

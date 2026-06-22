import asyncio

from aiogram.client.session.aiohttp import AiohttpSession

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.config.config import Config
from app.database.init_db import init_db

from app.bot.handlers.start import router as start_router
from app.bot.handlers.deposit import routers
from app.bot.handlers.logger import router as logger_router
from app.bot.handlers.feedback import router as feedback_router

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.scheduler.reminder import check_deposits


session = AiohttpSession(
    proxy=Config.PROXY_URL
)

bot = Bot(
    token=Config.BOT_TOKEN,
    session=session,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()

dp.include_router(start_router)

for r in routers:
    dp.include_router(r)

dp.include_router(feedback_router)
dp.include_router(logger_router)


async def main():
    await init_db()

    print("Bot started...")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_deposits,
        "interval",
        minutes=1,
        args=(bot,)
    )
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
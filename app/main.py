import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.strategy import FSMStrategy
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from bot.middlewares.db import DataBaseSession

from database.engine import create_db, drop_db, session_maker

from bot.handlers.user_private import user_private_router
from bot.handlers.admin_group import admin_group_router
from bot.handlers.admin_private import admin_private_router
from bot.handlers.bot_group import bot_group_router

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.processing import clean_database

from bot.spam_detection.spam_detector import SpamDetector


bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)

dp.include_router(user_private_router)
dp.include_router(admin_group_router)
dp.include_router(admin_private_router)
dp.include_router(bot_group_router)


async def on_startup(bot):
    # binding spam_detector instance to bot on startup
    bot.spam_detector = SpamDetector()

    run_param = False
    if run_param:
        await drop_db()

    await create_db()

    db_scheduler = AsyncIOScheduler()
    db_scheduler.add_job(
        clean_database, "interval", days=1, name="Cleaning db",kwargs={"bot": bot}
    )  # Запускать каждый день
    db_scheduler.start()


async def on_shutdown(bot):
    print("бот лег")


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())

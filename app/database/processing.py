from datetime import datetime, timedelta
import pytz

from aiogram import Bot

from database.models import Base, ChatAdmin, AntiSpamChat, BannedUser, MutedUser

from sqlalchemy import select, update, delete, exists, not_, and_

from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import session_maker


async def clean_database(bot: Bot):
    async with session_maker() as session:  # Используем асинхронный сеанс
        await clean_chats_and_admins(session, bot)
        await clean_banned_users(session)


async def clean_chats_and_admins(session: AsyncSession, bot: Bot):
    chat_ids = await session.execute(select(AntiSpamChat))  # Получаем все чаты
    chat_ids = chat_ids.scalars().all()  # Извлекаем результаты

    for chat in chat_ids:
        try:
            await bot.get_chat(chat.chat_id)  # Проверяем, существует ли чат
        except Exception:
            # Удаляем запись
            await session.execute(
                delete(ChatAdmin).where(ChatAdmin.chat_id == chat.chat_id)
            )
            await session.execute(
                delete(AntiSpamChat).where(AntiSpamChat.chat_id == chat.chat_id)
            )
    await session.commit()  # Коммитим изменения


async def clean_banned_users(session: AsyncSession):
    # Получаем текущее время
    current_time = datetime.now(pytz.utc)

    # Запрашиваем пользователей, у которых срок бана истек
    result = await session.execute(
        select(BannedUser).where(BannedUser.banned_till <= current_time)
    )
    banned_users = result.scalars().all()  # Извлекаем результаты

    # Удаляем пользователей из таблицы
    for user in banned_users:
        await session.execute(
            delete(BannedUser).where(BannedUser.user_id == user.user_id)
        )

    await session.commit()  # Коммитим изменения

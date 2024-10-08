from aiogram import Bot
from aiogram.types.chat_member_administrator import ChatMemberAdministrator
from aiogram.types.chat_member_owner import ChatMemberOwner
from aiogram.exceptions import TelegramForbiddenError

from sqlalchemy import select, update, delete, exists, not_, and_

from sqlalchemy import (
    DateTime,
    Integer,
    Float,
    String,
    Text,
    text,
    BigInteger,
    Boolean,
    Enum as SqlaEnum,
    func,
)

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.exc import SQLAlchemyError

from database.models import (
    Punishment,
    ChatAdmin,
    AntiSpamChat,
    BannedUser,
    MutedUser,
)

from datetime import datetime, timedelta
import pytz

from database.engine import region

from dogpile.cache.api import NoValue


def get_server_time():
    return datetime.now(pytz.utc)


# calculates till time from nom
def get_till_time(duration: int):
    return get_server_time() + timedelta(hours=duration)


async def orm_add_chat_admin(session: AsyncSession, data: dict):
    chat_id = data["chat_id"]
    user_id = data["user_id"]

    cache_key = f"admin_user_status_{user_id}"
    region.set(cache_key, True)

    # checks whether the instance presents
    stmt = select(ChatAdmin).filter_by(chat_id=chat_id, user_id=user_id)
    result = await session.execute(stmt)
    existing_record = result.scalar()

    if existing_record:
        # if yes - prevents from saving again
        return

    # adds new row
    obj = ChatAdmin(chat_id=chat_id, user_id=user_id)

    session.add(obj)

    await session.commit()


async def orm_delete_admin_chat(session: AsyncSession, admin_id: int):
    query = delete(ChatAdmin).where(ChatAdmin.id == admin_id)
    await session.execute(query)

    # invalidates cache if data has changed
    cache_key = f"admin_user_status_{admin_id}"
    region.delete(cache_key)


# gets list of all chats that an admin rules
async def orm_get_admin_chats(session: AsyncSession, admin_id: int):
    query = select(ChatAdmin).where(ChatAdmin.user_id == admin_id)
    result = await session.execute(query)
    return result.scalars()


# checks whether a bot user is an admin in any antispam chat
async def orm_is_user_admin(session: AsyncSession, user_id: int, bot: Bot) -> bool:
    cache_key = f"admin_user_status_{user_id}"
    obj = region.get(cache_key)

    if obj is None or isinstance(obj, NoValue):
        # Проверяем базу данных на наличие информации о пользователе
        stmt = select(ChatAdmin).where(ChatAdmin.user_id == user_id)
        result = await session.execute(stmt)
        chat_admins = result.scalars().all()

        # Проверяем доступность чатов и актуальность информации
        admin_status = False
        for chat_admin in chat_admins:
            try:
                chat_member = await bot.get_chat_member(chat_admin.chat_id, user_id)
                if isinstance(chat_member, (ChatMemberOwner, ChatMemberAdministrator)):
                    admin_status = True
                    break
            except TelegramForbiddenError:
                # Логируем исключение, если необходимо, для отладки
                continue

        # Обновляем кэш
        region.set(cache_key, admin_status)
    else:
        admin_status = obj

    return admin_status


async def orm_add_anti_spam_chat(session: AsyncSession, data: dict):
    chat_id = data["chat_id"]

    # checks whether the instance presents
    stmt = select(AntiSpamChat).filter_by(chat_id=chat_id)
    result = await session.execute(stmt)
    existing_record = result.scalar()

    if existing_record:
        # if yes - prevents from saving againF
        return

    # adds new row
    obj = AntiSpamChat(
        chat_id=chat_id,
    )

    session.add(obj)
    try:
        await session.commit()
    except SQLAlchemyError as ex:
        print(ex)
        await session.rollback()


async def orm_delete_anti_spam_chat(session: AsyncSession, chat_id: int):
    query = delete(AntiSpamChat).where(AntiSpamChat.chat_id == chat_id)
    await session.execute(query)


async def orm_get_anti_spam_chat(session: AsyncSession, chat_id: int):
    cache_key = f"anti_spam_chat_{chat_id}"
    obj = region.get(cache_key)

    if obj is None or isinstance(obj, NoValue):
        query = select(AntiSpamChat).where(AntiSpamChat.chat_id == chat_id)
        result = await session.execute(query)
        obj = result.scalar_one_or_none()
        if obj is not None:
            region.set(cache_key, obj)

    return obj


async def orm_update_anti_spam_chat(session: AsyncSession, chat_id: int, data: dict):
    query = update(AntiSpamChat).where(AntiSpamChat.chat_id == chat_id).values(**data)
    await session.execute(query)
    await session.commit()

    # invalidates cache if data has changed
    cache_key = f"anti_spam_chat_{chat_id}"
    region.delete(cache_key)


# a functional for changing activation status in an antispam chat by toggling
async def orm_toggle_anti_spam_chat_is_enabled(session: AsyncSession, chat_id: int):
    query = (
        update(AntiSpamChat)
        .where(AntiSpamChat.chat_id == chat_id)
        .values(is_enabled=not_(AntiSpamChat.is_enabled))
    )
    await session.execute(query)
    await session.commit()

    # invalidates cache if data has changed
    cache_key = f"anti_spam_chat_{chat_id}"
    region.delete(cache_key)


# a functional for changing punishment way in an antispam chat by toggling
async def orm_toggle_anti_spam_chat_punishment(session: AsyncSession, chat_id: int):
    query = select(AntiSpamChat).where(AntiSpamChat.chat_id == chat_id)
    result = await session.execute(query)
    chat = result.scalar_one_or_none()

    if chat:
        if chat.punishment == Punishment.MUTE:
            chat.punishment = Punishment.BAN
        else:
            chat.punishment = Punishment.MUTE

        await session.commit()

        # invalidates cache if data has changed
        cache_key = f"anti_spam_chat_{chat_id}"
        region.delete(cache_key)


async def orm_get_expired_anti_spam_chat_ids(session: AsyncSession, bot: Bot):
    chats = await session.execute(select(AntiSpamChat.id))
    chats = chats.scalars().all()

    # Проверяем, что пользователи являются админами в своих чатах
    chat_ids_to_delete = set()
    for chat in chats:
        try:
            await bot.get_chat(chat.id)
        except TelegramForbiddenError:
            chat_ids_to_delete.add(chat.chat_id)

    return chat_ids_to_delete


async def orm_get_expired_chat_admin_ids(session: AsyncSession, bot: Bot):
    chat_admins = await session.execute(select(ChatAdmin))
    chat_admins = chat_admins.scalars().all()

    # Проверяем, что пользователи являются админами в своих чатах
    chat_admin_ids_to_delete = set()
    for chat_admin in chat_admins:
        try:
            chat_member = await bot.get_chat_member(
                chat_admin.chat_id, chat_admin.user_id
            )
            if isinstance(chat_member, (ChatMemberOwner, ChatMemberAdministrator)):
                pass
            else:
                chat_admin_ids_to_delete.add(chat_admin.id)
        except TelegramForbiddenError:
            chat_admin_ids_to_delete.add(chat_admin.id)

    return chat_admin_ids_to_delete


async def orm_add_banned_user(
    session: AsyncSession, chat_id: int, user_id: int, banned_till: datetime = None
):
    banned_user = BannedUser(chat_id=chat_id, user_id=user_id, banned_till=banned_till)

    session.add(banned_user)
    await session.commit()


async def orm_add_muted_user(
    session: AsyncSession, chat_id: int, user_id: int, muted_till: datetime
):
    muted_user = MutedUser(chat_id=chat_id, user_id=user_id, muted_till=muted_till)

    session.add(muted_user)
    await session.commit()


async def orm_get_banned_users(session: AsyncSession, chat_id: int):
    query = select(BannedUser).where(BannedUser.chat_id == chat_id)
    result = await session.execute(query)
    return result.scalars()


async def orm_get_muted_users(session: AsyncSession, chat_id: int):
    query = select(MutedUser).where(MutedUser.chat_id == chat_id)
    result = await session.execute(query)
    return result.scalars()


async def orm_get_anti_spam_chat_info(session: AsyncSession, chat_id: int):
    query = select(AntiSpamChat).where(AntiSpamChat.chat_id == chat_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def orm_get_anti_spam_chat_ban_and_mute_counts(
    session: AsyncSession, chat_id: int
):
    # Get the current UTC time with timezone information
    current_time = func.now()

    # Query to get count of banned users who are currently banned
    banned_users_count_query = (
        select(func.count())
        .select_from(BannedUser)
        .where(
            BannedUser.chat_id == chat_id,
            BannedUser.banned_at <= current_time,
            BannedUser.banned_till > current_time,
        )
    )

    banned_users_count_result = await session.execute(banned_users_count_query)
    banned_users_count = banned_users_count_result.scalar()

    # Query to get count of muted users who are currently muted
    muted_users_count_query = (
        select(func.count())
        .select_from(MutedUser)
        .where(
            MutedUser.chat_id == chat_id,
            MutedUser.muted_at <= current_time,
            MutedUser.muted_till > current_time,
        )
    )

    muted_users_count_result = await session.execute(muted_users_count_query)
    muted_users_count = muted_users_count_result.scalar()

    return banned_users_count, muted_users_count

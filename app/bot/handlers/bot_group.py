from aiogram import F, types, Router, Bot
from aiogram.types.user import User
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import (
    as_list,
    as_marked_section,
    Bold,
)
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import AntiSpamChat, Punishment, BannedUser, MutedUser

from bot.filters.chat_types import ChatTypeFilter

from bot.kbds.reply import get_keyboard

from bot.text_utils import text

from os import getenv

from database.orm_query import (
    orm_get_anti_spam_chat,
    orm_add_banned_user,
    orm_add_muted_user,
    get_till_time,
)


bot_group_router = Router()
bot_group_router.message.filter(ChatTypeFilter(["group", "supergroup"]))
bot_group_router.edited_message.filter(ChatTypeFilter(["group", "supergroup"]))


@bot_group_router.message(F.text)
@bot_group_router.edited_message(F.text)
async def check_for_spam(message: types.Message, session: AsyncSession):
    chat_id = message.chat.id

    chat_info = await orm_get_anti_spam_chat(session, chat_id)

    if chat_info is None:
        return

    if not chat_info.is_enabled:
        return

    if message.bot.spam_detector.is_spam(message.text):
        await message.delete()
        await punish_user(message.bot, message.from_user, chat_info, session)


async def punish_user(
    bot: Bot, user: User, chat_info: AntiSpamChat, session: AsyncSession
):
    # Вычисление времени окончания мута
    punished_till = None
    if chat_info.punishment_duration is not None:
        punished_till = get_till_time(chat_info.punishment_duration)

    if chat_info.punishment == Punishment.BAN:
        if await bot.ban_chat_member(chat_info.chat_id, user.id, punished_till):
            await orm_add_muted_user(session, chat_info.chat_id, user.id, punished_till)
    elif chat_info.punishment == Punishment.MUTE:
        if await bot.restrict_chat_member(
            chat_id=chat_info.chat_id,
            user_id=user.id,
            permissions=types.ChatPermissions(),
            until_date=punished_till,
        ):
            await orm_add_banned_user(
                session, chat_info.chat_id, user.id, punished_till
            )

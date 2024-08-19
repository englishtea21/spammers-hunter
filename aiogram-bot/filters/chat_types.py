from aiogram.filters import Filter
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot, types

from database.orm_query import orm_get_admin_chats, orm_is_user_admin


class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types


# for group chats
class AdminOrOwnerFilter(Filter):
    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        chat_id = message.chat.id
        user_id = message.from_user.id

        try:
            chat_member = await bot.get_chat_member(chat_id, user_id)
            return isinstance(
                chat_member, (types.ChatMemberAdministrator, types.ChatMemberOwner)
            )
        except Exception:
            return False


# for private chat with bot
class AdminPrivateFilter(Filter):
    async def __call__(self, message: types.Message, session: AsyncSession) -> bool:
        user_id = message.from_user.id
        return await orm_is_user_admin(session, user_id)

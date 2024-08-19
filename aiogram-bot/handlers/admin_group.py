from string import punctuation

from aiogram import Bot, types, Router
from aiogram.filters import Command, ChatMemberUpdatedFilter

from filters.chat_types import ChatTypeFilter, AdminOrOwnerFilter

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import (
    orm_add_admin_chat,
    orm_add_anti_spam_chat,
    orm_get_anti_spam_chat,
    orm_update_anti_spam_chat,
    orm_toggle_anti_spam_chat_is_enabled,
)

from text_utils import text

# router for admins commands handling in antispam chat
admin_group_router = Router()
admin_group_router.message.filter(ChatTypeFilter(["group", "supergroup"]))
admin_group_router.edited_message.filter(ChatTypeFilter(["group", "supergroup"]))

admin_group_router.message.filter(
    ChatTypeFilter(["group", "supergroup", "channel"]), AdminOrOwnerFilter()
)


# handling command for the first time bot registration with retrieving all admins from chat
# also can be used to turn on bot later
@admin_group_router.message(Command("start_spam_hunting"))
async def start_spam_hunting(message: types.Message, bot: Bot, session: AsyncSession):
    chat_id = message.chat.id

    bot_as_member = await bot.get_chat_member(chat_id, bot.id)

    if not isinstance(bot_as_member, types.ChatMemberAdministrator):
        await message.answer(text.text_templates["IN_GROUP"]["RIGHTS_REQUIRED"])
        return

    obj = await orm_get_anti_spam_chat(session, chat_id)

    if obj is None:
        try:
            await orm_add_anti_spam_chat(session, {"chat_id": chat_id})

            admins = await bot.get_chat_administrators(chat_id)
            for admin in admins:
                if admin.user.id == bot.id:
                    continue
                await orm_add_admin_chat(
                    session, {"chat_id": chat_id, "user_id": admin.user.id}
                )

        except Exception as ex:
            await message.answer(text.text_templates["ERRORS"]["CANT_GET_ADMINS"])
            print(ex)

    elif obj.is_enabled:
        await message.answer(text.text_templates["IN_GROUP"]["IS_ALREADY_ENABLED"])
        return
    else:
        await orm_toggle_anti_spam_chat_is_enabled(session, chat_id)

    await message.answer(
        text.text_templates["IN_GROUP"]["SPAMMERS_HUNTING_STARTED_SUCCESSFULLY"]
    )


# temporary disabling bot action in chat
@admin_group_router.message(Command("end_spam_hunting"))
async def end_spam_hunting(message: types.Message, bot: Bot, session: AsyncSession):
    chat_id = message.chat.id

    obj = await orm_get_anti_spam_chat(session, chat_id)

    if not obj.is_enabled:
        await message.answer(text.text_templates["IN_GROUP"]["IS_ALREADY_DISABLED"])
        return

    bot_as_member = await bot.get_chat_member(chat_id, bot.id)

    if not isinstance(bot_as_member, types.ChatMemberAdministrator):
        await message.answer(text.text_templates["IN_GROUP"]["RIGHTS_REQUIRED"])
        return

    await orm_update_anti_spam_chat(session, chat_id, {"is_enabled": False})

    await message.answer(
        text.text_templates["IN_GROUP"]["SPAMMERS_HUNTING_ENDED_SUCCESSFULLY"]
    )

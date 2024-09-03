from aiogram import Bot

from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.types import InlineKeyboardButton

from bot.text_utils import text_generator, text

from bot.kbds.reply import get_keyboard

from aiogram.types.chat_member_administrator import ChatMemberAdministrator
from aiogram.types.chat_member_owner import ChatMemberOwner

from aiogram.exceptions import TelegramForbiddenError

# admin panel keyboards and pagination for chat button list

ADMIN_KB = get_keyboard(
    text.text_templates["ADMIN_PRIVATE_CHAT"]["OPTIONS"]["CHECK_CHATS"],
    text.text_templates["ADMIN_PRIVATE_CHAT"]["OPTIONS"]["EXIT_ADMIN_MODE"],
    placeholder=text.text_templates["PLACEHOLDERS"]["SELECT_OPTION"],
    sizes=(2, 1),
)

CHATS_PER_PAGE = 5


async def build_admin_chats_page(bot, page: int, admin_chats):
    start_idx = page * CHATS_PER_PAGE
    end_idx = start_idx + CHATS_PER_PAGE
    builder = InlineKeyboardBuilder()

    valid_chats = []

    for admin_chat in admin_chats[start_idx:end_idx]:
        # show only relevant chats where the bot is admin
        try:
            chat_member = await bot.get_chat_member(admin_chat.chat_id, bot.id)
            if isinstance(chat_member, (ChatMemberAdministrator, ChatMemberOwner)):
                chat = await bot.get_chat(admin_chat.chat_id)
                valid_chats.append(chat)
                builder.row(
                    InlineKeyboardButton(
                        text=chat.title, callback_data=f"chat_info:{admin_chat.chat_id}"
                    )
                )
        except TelegramForbiddenError:
            pass

    # Кнопки навигации
    navigation_buttons = []
    if start_idx > 0:
        navigation_buttons.append(
            InlineKeyboardButton(text="⬅️", callback_data=f"admin_chats_page:{page - 1}")
        )
    if end_idx < len(admin_chats):
        navigation_buttons.append(
            InlineKeyboardButton(text="➡️", callback_data=f"admin_chats_page:{page + 1}")
        )

    if navigation_buttons:
        builder.row(*navigation_buttons)

    return builder.as_markup()


async def build_chat_info_markup(chat_info):
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=text_generator.toggle_spam_button(chat_info.is_enabled),
            callback_data="toggle_antispam",
        )
    )

    builder.row(
        InlineKeyboardButton(
            text=text_generator.toggle_punishment_button(chat_info.punishment),
            callback_data="toggle_punishment",
        )
    )

    builder.row(
        InlineKeyboardButton(
            text=text.text_templates["ADMIN_PRIVATE_CHAT"]["CHAT_INFO_MODIFY"][
                "REQUESTS"
            ]["CHANGE_PUNISHMENT_DURATION"],
            callback_data="enter_punishment_duration",
        )
    )

    markup = builder.as_markup()

    return markup

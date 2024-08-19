from aiogram import Bot

from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.types import InlineKeyboardButton

from text_utils import text_generator, text

CHATS_PER_PAGE = 5


async def build_admin_chats_page(bot, page: int, admin_chats):
    start_idx = page * CHATS_PER_PAGE
    end_idx = start_idx + CHATS_PER_PAGE
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки чатов в колонку
    for admin_chat in admin_chats[start_idx:end_idx]:
        chat = await bot.get_chat(admin_chat.chat_id)
        builder.row(
            InlineKeyboardButton(
                text=chat.title, callback_data=f"chat_info:{admin_chat.chat_id}"
            )
        )

    # Добавляем кнопки навигации в одну строку
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

    # toggle антиспама в чате
    builder.row(
        InlineKeyboardButton(
            text=text_generator.toggle_spam_button(chat_info.is_enabled),
            callback_data="toggle_antispam",
        )
    )

    # toggle антиспама в чате
    builder.row(
        InlineKeyboardButton(
            text=text_generator.toggle_punishment_button(chat_info.punishment),
            callback_data="toggle_punishment",
        )
    )

    # ввод длительности наказания
    builder.row(
        InlineKeyboardButton(
            text=text.text_templates["ADMIN_PRIVATE_CHAT"]["CHAT_INFO_MODIFY"]["REQUESTS"]["CHANGE_PUNISHMENT_DURATION"],
            callback_data="enter_punishment_duration",
        )
    )

    markup = builder.as_markup()

    return markup

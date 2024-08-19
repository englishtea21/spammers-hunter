import asyncio

from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession

from aiogram.types.callback_query import CallbackQuery

from database.orm_query import (
    orm_get_admin_chats,
    orm_toggle_anti_spam_chat_is_enabled,
    orm_toggle_anti_spam_chat_punishment,
    orm_get_anti_spam_chat_info,
    orm_get_anti_spam_chat_ban_and_mute_counts,
    orm_update_anti_spam_chat,
)

from filters.chat_types import ChatTypeFilter, AdminPrivateFilter

from aiogram.enums.chat_type import ChatType

from handlers.user_private import ADMIN_KB, USER_KB

from kbds.inline import get_callback_btns
from kbds.reply import get_keyboard
from kbds.admin_panel import build_admin_chats_page, build_chat_info_markup

from text_utils import text, text_generator


# fsm states for admin panel
class AdminState(StatesGroup):
    selecting_chat_from_list = State()
    browsing_chat_info = State()
    waiting_for_punishment_duration = State()


# router for handling actions in admin panel
admin_private_router = Router()
admin_private_router.message.filter(ChatTypeFilter(["private"]), AdminPrivateFilter())


async def close_panel(state: FSMContext, bot, chat_id, panel_key: str):
    data = await state.get_data()
    panel_id = data.get(panel_key)

    if panel_id is not None:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=panel_id)
            await state.update_data({panel_key: None})
        except:
            pass


# retrieves all admin chats in a paginated button list
@admin_private_router.message(
    or_f(
        Command("my_admin_chats"),
        F.text == text.text_templates["ADMIN_PRIVATE_CHAT"]["OPTIONS"]["CHECK_CHATS"],
    )
)
async def show_admin_chats(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    await close_panel(
        state, message.bot, message.chat.id, "current_chat_selection_panel_id"
    )
    await close_panel(state, message.bot, message.chat.id, "current_chat_pannel_id")

    admin_id = message.from_user.id
    admin_chats = list(await orm_get_admin_chats(session, admin_id))

    new_message = await send_admin_chats_page(message, page=0, admin_chats=admin_chats)
    await state.update_data(current_chat_selection_panel_id=new_message.message_id)
    await state.set_state(AdminState.selecting_chat_from_list)


async def send_admin_chats_page(message: types.Message, page: int, admin_chats):
    markup = await build_admin_chats_page(message.bot, page, admin_chats)
    return await message.answer(
        text.text_templates["ADMIN_PRIVATE_CHAT"]["ANSWERS"]["YOUR_CHATS"],
        reply_markup=markup,
    )


# implements arrow swithing on chats button list
@admin_private_router.callback_query(
    and_f(
        lambda c: c.data.startswith("admin_chats_page:"),
        StateFilter(AdminState.selecting_chat_from_list),
    )
)
async def change_admin_chats_page(callback_query: CallbackQuery, state: FSMContext):
    page = int(callback_query.data.split(":")[1])
    admin_chats = (await state.get_data()).get("admin_chats")

    if not admin_chats:
        await callback_query.answer(text.text_templates["ERRORS"]["NO_CHATS"])
        return

    new_markup = await build_admin_chats_page(callback_query.bot, page, admin_chats)
    await callback_query.message.edit_reply_markup(reply_markup=new_markup)
    await callback_query.answer()


# retrieves antispam chat info with control panel
@admin_private_router.callback_query(
    and_f(
        lambda c: c.data.startswith("chat_info:"),
        or_f(
            StateFilter(AdminState.selecting_chat_from_list),
            StateFilter(AdminState.browsing_chat_info),
        ),
    )
)
async def show_chat_info(
    callback_query: CallbackQuery, state: FSMContext, session: AsyncSession
):
    chat_id = int(callback_query.data.split(":")[1])
    await close_panel(
        state,
        callback_query.bot,
        callback_query.message.chat.id,
        "current_chat_pannel_id",
    )

    chat_info = await orm_get_anti_spam_chat_info(session, chat_id)
    await extend_chat_info(session, chat_info, callback_query.bot)

    new_message = await send_chat_info_page(callback_query.message, chat_info)
    await state.update_data(
        current_chat_id=chat_id,
        chat_data=chat_info,
        current_chat_pannel_id=new_message.message_id,
    )

    await callback_query.answer()
    await state.set_state(AdminState.browsing_chat_info)


async def extend_chat_info(session: AsyncSession, chat_info, bot):
    chat_info.title = (await bot.get_chat(chat_info.chat_id)).title
    chat_info.banned_users_amount, chat_info.muted_users_amount = (
        await orm_get_anti_spam_chat_ban_and_mute_counts(session, chat_info.chat_id)
    )


async def get_chat_link(bot, chat_id):
    chat = await bot.get_chat(chat_id)
    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
        return f"https://t.me/{chat.username}" if chat.username else None
    return None


async def send_chat_info_page(message: types.Message, chat_info):
    markup = await build_chat_info_markup(chat_info)
    chat_link = await get_chat_link(message.bot, chat_info.chat_id)
    return await message.answer(
        text_generator.chat_info_message(chat_info, chat_link),
        reply_markup=markup,
    )


# general wrapper for toggle chat commands
async def toggle_chat_setting(
    callback_query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    toggle_func,
    text_func,
):
    chat_id = (await state.get_data()).get("current_chat_id")
    await toggle_func(session, chat_id)

    chat_info = await orm_get_anti_spam_chat_info(session, chat_id)
    await extend_chat_info(session, chat_info, callback_query.bot)

    chat_link = await get_chat_link(callback_query.bot, chat_info.chat_id)
    await callback_query.message.edit_text(
        text_generator.chat_info_message(chat_info, chat_link)
    )
    await callback_query.message.edit_reply_markup(
        reply_markup=await build_chat_info_markup(chat_info)
    )
    await callback_query.answer(text_func(chat_info))


# toggles antispam active status
@admin_private_router.callback_query(
    and_f(
        lambda c: c.data == "toggle_antispam",
        StateFilter(AdminState.browsing_chat_info),
    )
)
async def toggle_antispam(
    callback_query: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await toggle_chat_setting(
        callback_query,
        state,
        session,
        orm_toggle_anti_spam_chat_is_enabled,
        lambda info: text_generator.toggle_spam_performed(info.is_enabled),
    )
    await callback_query.answer()


# toggles punishment way
@admin_private_router.callback_query(
    and_f(
        lambda c: c.data == "toggle_punishment",
        StateFilter(AdminState.browsing_chat_info),
    )
)
async def toggle_punishment(
    callback_query: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await toggle_chat_setting(
        callback_query,
        state,
        session,
        orm_toggle_anti_spam_chat_punishment,
        lambda info: text_generator.toggle_punishment_performed(info.punishment),
    )
    await callback_query.answer()


# updates punishment duration
@admin_private_router.callback_query(
    and_f(
        lambda c: c.data == "enter_punishment_duration",
        StateFilter(AdminState.browsing_chat_info),
    )
)
async def change_punishment_duration(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        text.text_templates["ADMIN_PRIVATE_CHAT"]["CHAT_INFO_MODIFY"]["ANSWERS"][
            "WRITE_PUNISHMENT_DURATION"
        ],
    )
    await state.set_state(AdminState.waiting_for_punishment_duration)
    await callback_query.answer()


# handling written punishment duration by user
@admin_private_router.message(StateFilter(AdminState.waiting_for_punishment_duration))
async def handle_change_punishment_duration(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    try:
        duration = int(message.text)
        if duration < 0:
            raise ValueError
    except ValueError:
        await message.answer(
            text.text_templates["ADMIN_PRIVATE_CHAT"]["CHAT_INFO_MODIFY"]["ANSWERS"][
                "WRONG_PUNISHMENT_DURATION_FORMAT"
            ]
        )
        await state.set_state(AdminState.browsing_chat_info)
        return

    chat_id = (await state.get_data()).get("current_chat_id")
    await orm_update_anti_spam_chat(session, chat_id, {"punishment_duration": duration})
    await message.answer(text_generator.punishment_duration_set_successfully(duration))
    await state.set_state(AdminState.browsing_chat_info)


# exits from the admin panel
@admin_private_router.message(
    or_f(
        Command("exit_admin_mode"),
        F.text
        == text.text_templates["ADMIN_PRIVATE_CHAT"]["OPTIONS"]["EXIT_ADMIN_MODE"],
    )
)
async def exit_admin_mode_cmd(message: types.Message, state: FSMContext):
    await close_panel(
        state, message.bot, message.chat.id, "current_chat_selection_panel_id"
    )
    await close_panel(state, message.bot, message.chat.id, "current_chat_pannel_id")
    await message.answer(
        text=text.text_templates["ADMIN_PRIVATE_CHAT"]["ANSWERS"]["SEE_YOU"],
        reply_markup=USER_KB,
    )

    await state.clear()

from aiogram import F, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import (
    as_list,
    as_marked_section,
    Bold,
)
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_is_user_admin

# from database.orm_query import orm_get_products  # Italic, as_numbered_list и тд

from filters.chat_types import ChatTypeFilter

from kbds.reply import get_keyboard

from text_utils import text, text_generator

from os import getenv

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from kbds import user_panel, admin_panel

# router for first-time work with antispam bot in private chat
user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    await message.answer(
        text_generator.start_message(),
        reply_markup=user_panel.USER_KB,
    )
    await message.answer(
        text.text_templates["USER_PRIVATE_CHAT"]["START_SETTING_ME"],
        reply_markup=user_panel.ADD_TO_GROUPS,
    )


# sends link to project repository
@user_private_router.message(
    or_f(
        Command("repo"),
        (
            F.text
            == text.text_templates["USER_PRIVATE_CHAT"]["OPTIONS"]["ABOUT_PROJECT"]
        ),
    )
)
async def repo_cmd(message: types.Message):
    await message.answer(
        text.text_templates["USER_PRIVATE_CHAT"]["ANSWERS"]["ABOUT_PROJECT"].format(
            getenv("REPOSITORY_LINK")
        )
    )


# sends instruction for bot setting in chats
@user_private_router.message(
    or_f(
        Command("help"),
        (F.text == text.text_templates["USER_PRIVATE_CHAT"]["OPTIONS"]["HOW_TO"]),
    )
)
async def help_cmd(message: types.Message, session: AsyncSession):
    await message.answer(
        text_generator.instructions_message(), reply_markup=user_panel.ADD_TO_GROUPS
    )


# transfers the user to the admin panel
@user_private_router.message(
    or_f(
        Command("to_admin_mode"),
        (
            F.text
            == text.text_templates["USER_PRIVATE_CHAT"]["OPTIONS"]["TO_ADMIN_MODE"]
        ),
    )
)
async def to_admin_mode_cmd(
    message: types.Message, session: AsyncSession, state: FSMContext
):
    if not await orm_is_user_admin(session, message.from_user.id):
        await message.answer(
            text.text_templates["USER_PRIVATE_CHAT"]["ANSWERS"][
                "FIRSTLY_ADD_ME_TO_YOUR_CHATS"
            ]
        )
        return
    else:
        await message.answer(
            text=text.text_templates["USER_PRIVATE_CHAT"]["ANSWERS"]["ADMIN_ON"],
            reply_markup=admin_panel.ADMIN_KB,
        )

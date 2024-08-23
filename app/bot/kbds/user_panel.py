from bot.text_utils.text import text_templates

from bot.kbds.reply import get_keyboard
from bot.kbds.inline import get_url_btns


USER_KB = get_keyboard(
    text_templates["USER_PRIVATE_CHAT"]["OPTIONS"]["HOW_TO"],
    text_templates["USER_PRIVATE_CHAT"]["OPTIONS"]["ABOUT_PROJECT"],
    text_templates["USER_PRIVATE_CHAT"]["OPTIONS"]["CHANGE_LANGUAGE"],
    text_templates["USER_PRIVATE_CHAT"]["OPTIONS"]["TO_ADMIN_MODE"],
    placeholder=text_templates["PLACEHOLDERS"]["SELECT_OPTIONS_BELOW"],
    sizes=(2, 2),
)

ADD_TO_GROUPS = get_url_btns(
    btns={
        "Добавить меня в свои чаты": f"https://t.me/SpammersHunterBot?startgroup=newgroups"
    }
)

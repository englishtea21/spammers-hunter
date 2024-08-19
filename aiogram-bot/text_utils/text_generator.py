import text_utils.text
import database.models as models

# implements formatted text generation according to context


def start_message():
    return (
        """
Привет! Я — <b>интеллектуальный защитник</b> 🛡 от спама в чатах.\n\n"""
        + instructions_message()
    )


def instructions_message():
    return """
Для настройки в чатах тебе необходимо:

- <u>Быть администратором</u> 👑 в чатах, где хочешь меня настроить, и <u>отключить анонимность</u> для себя и других админов, которым хочешь дать доступ ко мне.\n
- <u>Добавить меня</u> в чаты как <u>администратора</u> 🪪 с полномочиями банить пользователей и удалять сообщения.\n
- После этого <u>введи команду в чате</u>: <code>/start_spam_hunting</code>. С этого момента антиспам начнет работу по умолчанию.\n

Управлять настройками каждого отдельного чата ты сможешь <u>здесь, после перехода в режим админа</u>. 👀

Удачи! 👾
"""


def chat_info_message(chat_info: models.AntiSpamChat, chat_link: str):
    return f"""
<b>Информация о чате "<a href="{chat_link}">{chat_info.title}</a>":</b>
    
<b>Антиспам: {'✅' if chat_info.is_enabled else '❌'}</b>
    
<b>Мера наказания: {'🔨 бан' if chat_info.punishment == models.Punishment.BAN else '🔇 мут'}</b>

<b>Длительность наказания: {str(chat_info.punishment_duration)+" часов" if chat_info.punishment_duration!=0 else "Навсегда"}</b>
    
<b>Число в бане за спам сейчас: {chat_info.banned_users_amount}</b>
    
<b>Число в муте за спам сейчас: {chat_info.muted_users_amount}</b>
"""


def toggle_spam_performed(is_enabled: bool):
    return ("Активация " if is_enabled else "Деактивация ") + "антиспама выполнена!"


def toggle_spam_button(is_enabled: bool):
    return ("✅Активировать " if not is_enabled else "❌Деактивировать") + " антиспам"


def toggle_punishment_performed(punishment: models.Punishment):
    return (
        f"Наказание за спам - {'бан' if punishment==models.Punishment.BAN else 'мут'}"
    )


def toggle_punishment_button(punishment: models.Punishment):
    return f"Включить {'🔨 бан' if punishment==models.Punishment.MUTE else '🔇 мут'} за спам"


def punishment_duration_set_successfully(punishment_duration: int):
    return text_utils.text.text_templates["ADMIN_PRIVATE_CHAT"]["CHAT_INFO_MODIFY"][
        "ANSWERS"
    ]["PUNISHMENT_DURATION_SET_SUCCESSFULLY"].format(
        punishment_duration
        if punishment_duration != 0
        else text_utils.text.text_templates["ADMIN_PRIVATE_CHAT"]["CHAT_INFO_MODIFY"][
            "ANSWERS"
        ]["FOREVER"]
    )

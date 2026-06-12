from telegram import Update
from telegram.ext import ContextTypes

import schedule_service as sched
from formatters import format_day, format_week
from keyboards import (
    BTN_GROUP,
    BTN_HELP,
    BTN_NOTIFY_OFF,
    BTN_NOTIFY_ON,
    BTN_SETTINGS,
    BTN_TODAY,
    BTN_TOMORROW,
    BTN_WEEK,
    MAIN_KEYBOARD,
)
from storage import Storage, UserSettings

storage = Storage()

HELP_TEXT = """
<b>Команды бота</b>

/group 253-331 — указать группу
/today — расписание на сегодня
/tomorrow — на завтра
/week — на текущую неделю
/notify 15 — за сколько минут напоминать (5–120)
/notify_on — включить оповещения
/notify_off — выключить оповещения
/settings — ваши настройки
/help — эта справка
""".strip()

WELCOME = """
👋 Привет! Я бот с оповещениями о парах Московского политеха.

Укажите группу, например:
<code>/group 253-331</code>

После этого я буду присылать напоминания перед парами (по умолчанию за 15 минут).
""".strip()


def _get_settings(update: Update) -> UserSettings:
    return storage.get_user(update.effective_user.id)


def _save_settings(settings: UserSettings) -> None:
    storage.save_user(settings)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(WELCOME, reply_markup=MAIN_KEYBOARD)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        HELP_TEXT,
        disable_web_page_preview=True,
        reply_markup=MAIN_KEYBOARD,
    )


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip()
    await update.message.reply_html(
        f"Не понял сообщение «{text}».\n\n{HELP_TEXT}",
        disable_web_page_preview=True,
        reply_markup=MAIN_KEYBOARD,
    )


async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = _get_settings(update)
    notify = "включены" if s.notifications_enabled else "выключены"
    group = s.group_name or "не указана"
    await update.message.reply_html(
        f"<b>Настройки</b>\n\n"
        f"Группа: <code>{group}</code>\n"
        f"Оповещения: {notify}\n"
        f"Напоминать за: {s.notify_minutes} мин."
    )


async def group_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        context.user_data["awaiting_group"] = True
        await update.message.reply_text(
            "Отправьте название группы, например: 253-331\n"
            "Или: /group 253-331",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    name = " ".join(context.args)
    await _set_group(update, name)


async def _set_group(update: Update, name: str) -> None:
    found = sched.find_group(name)
    if not found:
        await update.message.reply_text(
            f"Группа «{name}» не найдена.\n"
            "Проверьте название на https://rasp.dmami.ru/"
        )
        return

    s = _get_settings(update)
    s.group_name = found
    _save_settings(s)
    await update.message.reply_html(
        f"✅ Группа сохранена: <code>{found}</code>\n"
        f"Оповещения: {'вкл.' if s.notifications_enabled else 'выкл.'} "
        f"(за {s.notify_minutes} мин. до пары)"
    )


async def _send_day(update: Update, date: str, title: str) -> None:
    s = _get_settings(update)
    if not s.group_name:
        await update.message.reply_text("Сначала укажите группу: /group 253-331")
        return
    try:
        day = sched.get_day(s.group_name, date, s.is_session)
    except ValueError as e:
        await update.message.reply_text(f"Расписание недоступно: {e}")
        return
    except Exception:
        await update.message.reply_text(
            "Не удалось загрузить расписание. Попробуйте позже."
        )
        return
    await update.message.reply_text(format_day(day, title))


async def today_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _send_day(update, sched.today_str(), "📅 Расписание на сегодня")


async def tomorrow_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _send_day(update, sched.tomorrow_str(), "📅 Расписание на завтра")


async def week_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = _get_settings(update)
    if not s.group_name:
        await update.message.reply_text("Сначала укажите группу: /group 253-331")
        return
    try:
        week = sched.get_week(s.group_name, sched.today_str(), s.is_session)
    except Exception:
        await update.message.reply_text(
            "Не удалось загрузить расписание. Попробуйте позже."
        )
        return
    await update.message.reply_text(format_week(week))


async def notify_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        s = _get_settings(update)
        await update.message.reply_text(
            f"Сейчас напоминания за {s.notify_minutes} мин.\n"
            "Изменить: /notify 15"
        )
        return
    try:
        minutes = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Укажите число минут: /notify 15")
        return
    if not 5 <= minutes <= 120:
        await update.message.reply_text("Допустимый диапазон: от 5 до 120 минут.")
        return
    s = _get_settings(update)
    s.notify_minutes = minutes
    _save_settings(s)
    await update.message.reply_text(f"✅ Напоминать за {minutes} мин. до пары.")


async def notify_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = _get_settings(update)
    s.notifications_enabled = True
    _save_settings(s)
    await update.message.reply_text("✅ Оповещения включены.")


async def notify_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = _get_settings(update)
    s.notifications_enabled = False
    _save_settings(s)
    await update.message.reply_text("🔕 Оповещения выключены.")


_BUTTON_HANDLERS = {
    BTN_TODAY: today_cmd,
    BTN_TOMORROW: tomorrow_cmd,
    BTN_WEEK: week_cmd,
    BTN_SETTINGS: settings_cmd,
    BTN_NOTIFY_ON: notify_on,
    BTN_NOTIFY_OFF: notify_off,
    BTN_HELP: help_cmd,
}


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip()
    if not text:
        return

    handler = _BUTTON_HANDLERS.get(text)
    if handler is not None:
        await handler(update, context)
        return

    if text == BTN_GROUP:
        context.user_data["awaiting_group"] = True
        await update.message.reply_text(
            "Отправьте название группы, например: 253-331",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    if context.user_data.pop("awaiting_group", False):
        await _set_group(update, text)
        return

    s = _get_settings(update)
    if not s.group_name and sched.find_group(text):
        await _set_group(update, text)
        return

    await unknown_message(update, context)

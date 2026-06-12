from telegram import BotCommand, KeyboardButton, ReplyKeyboardMarkup

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📅 Сегодня"), KeyboardButton("📆 Завтра")],
        [KeyboardButton("📋 Неделя"), KeyboardButton("⚙️ Настройки")],
        [KeyboardButton("🔔 Вкл. оповещения"), KeyboardButton("🔕 Выкл. оповещения")],
        [KeyboardButton("👥 Группа"), KeyboardButton("❓ Справка")],
    ],
    resize_keyboard=True,
)

BTN_TODAY = "📅 Сегодня"
BTN_TOMORROW = "📆 Завтра"
BTN_WEEK = "📋 Неделя"
BTN_SETTINGS = "⚙️ Настройки"
BTN_NOTIFY_ON = "🔔 Вкл. оповещения"
BTN_NOTIFY_OFF = "🔕 Выкл. оповещения"
BTN_HELP = "❓ Справка"
BTN_GROUP = "👥 Группа"

BOT_COMMANDS = [
    BotCommand("start", "Запуск бота"),
    BotCommand("group", "Указать группу"),
    BotCommand("today", "Расписание на сегодня"),
    BotCommand("tomorrow", "Расписание на завтра"),
    BotCommand("week", "Расписание на неделю"),
    BotCommand("settings", "Настройки"),
    BotCommand("notify", "За сколько минут напоминать"),
    BotCommand("notify_on", "Включить оповещения"),
    BotCommand("notify_off", "Выключить оповещения"),
    BotCommand("help", "Справка"),
]

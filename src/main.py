import logging
import sys

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import BOT_TOKEN, NOTIFY_CHECK_INTERVAL
from handlers import (
    group_cmd,
    handle_text,
    help_cmd,
    notify_cmd,
    notify_off,
    notify_on,
    settings_cmd,
    start,
    today_cmd,
    tomorrow_cmd,
    week_cmd,
)
from keyboards import BOT_COMMANDS
from notifications import check_notifications


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(BOT_COMMANDS)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    if not BOT_TOKEN:
        logger.error("Укажите BOT_TOKEN в файле .env")
        sys.exit(1)

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("settings", settings_cmd))
    app.add_handler(CommandHandler("group", group_cmd))
    app.add_handler(CommandHandler("today", today_cmd))
    app.add_handler(CommandHandler("tomorrow", tomorrow_cmd))
    app.add_handler(CommandHandler("week", week_cmd))
    app.add_handler(CommandHandler("notify", notify_cmd))
    app.add_handler(CommandHandler("notify_on", notify_on))
    app.add_handler(CommandHandler("notify_off", notify_off))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )

    app.job_queue.run_repeating(
        check_notifications,
        interval=NOTIFY_CHECK_INTERVAL,
        first=15,
        name="lesson_notifications",
    )

    logger.info("Бот запущен")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()

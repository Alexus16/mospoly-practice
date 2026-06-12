import logging
from datetime import datetime, timedelta

from telegram.ext import ContextTypes

import schedule_service as sched
from formatters import format_notification
from storage import Storage
from timezone_utils import now as moscow_now

logger = logging.getLogger(__name__)
storage = Storage()


def _parse_lesson_start(date_str: str, time_start: str) -> datetime:
    return datetime.strptime(f"{date_str} {time_start}", "%d.%m.%Y %H:%M")


def _notify_key(date_str: str, time_start: str, title: str) -> str:
    return f"{date_str}_{time_start}_{title}"


async def check_notifications(context: ContextTypes.DEFAULT_TYPE) -> None:
    today = sched.today_str()
    tomorrow = sched.tomorrow_str()
    storage.prune_notifications({today, tomorrow})

    current = moscow_now()
    users = storage.get_subscribed_users()

    for user in users:
        if not user.group_name:
            continue
        try:
            day_data = sched.get_day(user.group_name, today, user.is_session)
        except ValueError:
            logger.warning("Расписание недоступно для %s", user.group_name)
            continue
        except Exception:
            logger.exception("Ошибка загрузки расписания для %s", user.group_name)
            continue

        for slot in day_data["day"]:
            subject = slot.get("subject")
            if not subject:
                continue

            time_range = slot["time"]
            start_str = time_range[0]
            try:
                lesson_start = _parse_lesson_start(today, start_str)
            except ValueError:
                continue

            notify_at = lesson_start - timedelta(minutes=user.notify_minutes)
            if not (notify_at <= current < lesson_start):
                continue

            key = _notify_key(today, start_str, subject["title"])
            if storage.was_notified(user.user_id, key):
                continue

            text = format_notification(
                user.group_name,
                today,
                time_range,
                subject,
                user.notify_minutes,
            )
            try:
                await context.bot.send_message(chat_id=user.user_id, text=text)
                storage.mark_notified(user.user_id, key)
            except Exception:
                logger.exception("Не удалось отправить уведомление пользователю %s", user.user_id)

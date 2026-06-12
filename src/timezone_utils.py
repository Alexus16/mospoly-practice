"""Время расписания (Москва). На VPS в UTC без этого уведомления уходят с опозданием."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config import TIMEZONE


def now() -> datetime:
    """Текущее время в поясе расписания (наивное datetime для сравнения с парами)."""
    return datetime.now(TIMEZONE).replace(tzinfo=None)


def today_str() -> str:
    return datetime.now(TIMEZONE).strftime("%d.%m.%Y")


def tomorrow_str() -> str:
    return (datetime.now(TIMEZONE) + timedelta(days=1)).strftime("%d.%m.%Y")

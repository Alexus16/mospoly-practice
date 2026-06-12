import os
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
# Расписание Политеха — по московскому времени
TIMEZONE = ZoneInfo(os.getenv("BOT_TIMEZONE", "Europe/Moscow"))
HASH_SALT_PATH = ROOT_DIR / "hash_salt.txt"
DB_PATH = ROOT_DIR / "bot_data.db"

DEFAULT_NOTIFY_MINUTES = 15
GROUPS_CACHE_TTL = 3600
SCHEDULE_CACHE_TTL = 1800
NOTIFY_CHECK_INTERVAL = 60

import time
from typing import Optional

from mospolytech_api.api import API
from mospolytech_api.schedule import Schedule

from config import GROUPS_CACHE_TTL, HASH_SALT_PATH, SCHEDULE_CACHE_TTL
from timezone_utils import today_str, tomorrow_str

_api = API(hash_salt_path=str(HASH_SALT_PATH))
_groups_cache: dict = {"data": None, "ts": 0.0}
_schedule_cache: dict[tuple[str, bool], dict] = {}


def _now_ts() -> float:
    return time.time()


def get_groups() -> list[str]:
    if _groups_cache["data"] is not None and _now_ts() - _groups_cache["ts"] < GROUPS_CACHE_TTL:
        return _groups_cache["data"]
    groups = _api.get_groups()
    _groups_cache["data"] = groups
    _groups_cache["ts"] = _now_ts()
    return groups


def find_group(name: str) -> Optional[str]:
    query = name.strip()
    if not query:
        return None
    groups = get_groups()
    if query in groups:
        return query
    lower = query.lower()
    for group in groups:
        if group.lower() == lower:
            return group
    return None


def _get_raw_schedule(group: str, is_session: bool) -> dict:
    key = (group, is_session)
    cached = _schedule_cache.get(key)
    if cached and _now_ts() - cached["ts"] < SCHEDULE_CACHE_TTL:
        return cached["data"]
    data = _api.get_schedule(group=group, is_session=is_session)
    _schedule_cache[key] = {"data": data, "ts": _now_ts()}
    return data


def get_day(group: str, date: str, is_session: bool = False) -> dict:
    schedule = Schedule(_get_raw_schedule(group, is_session))
    return schedule.get_day(date)


def get_week(group: str, date: str, is_session: bool = False) -> dict:
    schedule = Schedule(_get_raw_schedule(group, is_session))
    return schedule.get_week(date)

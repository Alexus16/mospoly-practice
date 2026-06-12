from datetime import datetime
from typing import Optional


WEEKDAYS = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")


def _format_subject(subject: Optional[dict]) -> str:
    if not subject:
        return "— окно —"
    teachers = ", ".join(subject.get("teachers") or [])
    rooms = ", ".join(subject.get("rooms") or [])
    location = subject.get("location") or ""
    place_parts = [p for p in (location, rooms) if p]
    place = " / ".join(place_parts) if place_parts else "—"
    link = subject.get("link")
    link_line = f"\n🔗 {link}" if link else ""
    return (
        f"📚 {subject['title']}\n"
        f"📝 {subject['type']}\n"
        f"👤 {teachers or '—'}\n"
        f"📍 {place}"
        f"{link_line}"
    )


def format_slot(time_range: list[str], subject: Optional[dict]) -> str:
    start, end = time_range
    body = _format_subject(subject)
    return f"🕐 {start}–{end}\n{body}"


def format_day(day_data: dict, title: str) -> str:
    lines = [
        title,
        f"Группа: {day_data['group']}",
        f"Дата: {day_data['date']}",
        "",
    ]
    has_lessons = False
    for slot in day_data["day"]:
        if slot.get("subject"):
            has_lessons = True
        lines.append(format_slot(slot["time"], slot.get("subject")))
        lines.append("")
    if not has_lessons:
        lines.append("На этот день пар нет 🎉")
    return "\n".join(lines).strip()


def format_week(week_data: dict) -> str:
    lines = [
        f"📅 Расписание на неделю {week_data['dates'][0]} — {week_data['dates'][1]}",
        f"Группа: {week_data['group']}",
        "",
    ]
    for day in week_data["week"]:
        date = day["date"]
        weekday = WEEKDAYS[datetime.strptime(date, "%d.%m.%Y").weekday()]
        lessons = [s for s in day["day"] if s.get("subject")]
        lines.append(f"—— {weekday}, {date} ——")
        if not lessons:
            lines.append("Пар нет")
        else:
            for slot in lessons:
                t = slot["time"]
                subj = slot["subject"]
                lines.append(f"• {t[0]}–{t[1]} — {subj['title']} ({subj['type']})")
        lines.append("")
    return "\n".join(lines).strip()


def format_notification(
    group: str,
    date: str,
    time_range: list[str],
    subject: dict,
    minutes_before: int,
) -> str:
    start, end = time_range
    return (
        f"⏰ Через {minutes_before} мин начнётся пара\n\n"
        f"Группа: {group}\n"
        f"Дата: {date}\n"
        f"Время: {start}–{end}\n\n"
        f"{_format_subject(subject)}"
    )

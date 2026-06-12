import sqlite3
from dataclasses import dataclass
from typing import Optional

from config import DB_PATH, DEFAULT_NOTIFY_MINUTES


@dataclass
class UserSettings:
    user_id: int
    group_name: Optional[str]
    notify_minutes: int
    notifications_enabled: bool
    is_session: bool


class Storage:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    group_name TEXT,
                    notify_minutes INTEGER NOT NULL DEFAULT 15,
                    notifications_enabled INTEGER NOT NULL DEFAULT 1,
                    is_session INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS sent_notifications (
                    user_id INTEGER NOT NULL,
                    notify_key TEXT NOT NULL,
                    PRIMARY KEY (user_id, notify_key)
                );
                """
            )

    def get_user(self, user_id: int) -> UserSettings:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
        if row is None:
            return UserSettings(
                user_id=user_id,
                group_name=None,
                notify_minutes=DEFAULT_NOTIFY_MINUTES,
                notifications_enabled=True,
                is_session=False,
            )
        return UserSettings(
            user_id=row["user_id"],
            group_name=row["group_name"],
            notify_minutes=row["notify_minutes"],
            notifications_enabled=bool(row["notifications_enabled"]),
            is_session=bool(row["is_session"]),
        )

    def save_user(self, settings: UserSettings) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO users (
                    user_id, group_name, notify_minutes,
                    notifications_enabled, is_session
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    group_name = excluded.group_name,
                    notify_minutes = excluded.notify_minutes,
                    notifications_enabled = excluded.notifications_enabled,
                    is_session = excluded.is_session
                """,
                (
                    settings.user_id,
                    settings.group_name,
                    settings.notify_minutes,
                    int(settings.notifications_enabled),
                    int(settings.is_session),
                ),
            )

    def get_subscribed_users(self) -> list[UserSettings]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM users
                WHERE group_name IS NOT NULL AND notifications_enabled = 1
                """
            ).fetchall()
        return [
            UserSettings(
                user_id=row["user_id"],
                group_name=row["group_name"],
                notify_minutes=row["notify_minutes"],
                notifications_enabled=True,
                is_session=bool(row["is_session"]),
            )
            for row in rows
        ]

    def was_notified(self, user_id: int, notify_key: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT 1 FROM sent_notifications
                WHERE user_id = ? AND notify_key = ?
                """,
                (user_id, notify_key),
            ).fetchone()
        return row is not None

    def mark_notified(self, user_id: int, notify_key: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO sent_notifications (user_id, notify_key)
                VALUES (?, ?)
                """,
                (user_id, notify_key),
            )

    def prune_notifications(self, active_dates: set[str]) -> None:
        if not active_dates:
            return
        with self._connect() as conn:
            rows = conn.execute("SELECT user_id, notify_key FROM sent_notifications").fetchall()
            for row in rows:
                date_part = row["notify_key"].split("_", 1)[0]
                if date_part not in active_dates:
                    conn.execute(
                        "DELETE FROM sent_notifications WHERE user_id = ? AND notify_key = ?",
                        (row["user_id"], row["notify_key"]),
                    )

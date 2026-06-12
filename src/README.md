# Telegram-бот: расписание и напоминания (Московский политех)

Бот показывает расписание занятий и присылает напоминания перед парами. Данные берутся через [mospolytech_api](https://github.com/r4nd0lph-c/mospolytech_api) с [rasp.dmami.ru](https://rasp.dmami.ru/).

**Стек:** Python 3, [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot), SQLite, long polling.

---

## Возможности

- Выбор учебной группы (`/group`)
- Расписание: сегодня, завтра, неделя
- Напоминания за N минут до пары (по умолчанию 15)
- Вкл/выкл оповещений, настройки
- Кнопки под полем ввода и меню команд

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие |
| `/group 253-331` | Указать группу |
| `/today` | Расписание на сегодня |
| `/tomorrow` | На завтра |
| `/week` | На неделю |
| `/notify 15` | За сколько минут напоминать (5–120) |
| `/notify_on` / `/notify_off` | Вкл/выкл оповещения |
| `/settings` | Текущие настройки |
| `/help` | Справка |

---

## Как это работает

### Два режима

1. **Команды и кнопки** — пользователь пишет боту → `handlers.py` читает настройки из БД → `schedule_service.py` запрашивает расписание → `formatters.py` формирует текст → ответ в Telegram.

2. **Напоминания** — раз в 60 секунд (`NOTIFY_CHECK_INTERVAL` в `config.py`) вызывается `notifications.check_notifications`: для подписчиков с группой и включёнными оповещениями проверяется расписание на сегодня; если пора напомнить — отправляется сообщение (без дублей через таблицу `sent_notifications`).

### Связь с Telegram

- **Long polling** — бот постоянно опрашивает Telegram (`getUpdates`), сообщения обрабатываются сразу.
- Раз в минуту — только проверка напоминаний, не polling.

### Внешние сервисы

- **Telegram Bot API** — приём команд и отправка сообщений.
- **rasp.dmami.ru** — JSON с расписанием (через пакет `mospolytech_api`).

### Хранение данных

Файл **`bot_data.db`** (SQLite):

| Таблица | Содержимое |
|---------|------------|
| `users` | Telegram ID, группа, минуты до пары, вкл/выкл оповещений |
| `sent_notifications` | Уже отправленные напоминания (чтобы не слать дважды) |

Расписание в БД не кэшируется постоянно; в памяти кэш API ~30–60 минут.

### Часовой пояс

Время пар — **московское** (`Europe/Moscow` в `config.py` / `timezone_utils.py`). На VPS в UTC без этого напоминания уходят с опозданием.

---

## Структура проекта

```
тгбот/
├── main.py              # Запуск, polling, фоновая задача
├── handlers.py          # Команды и кнопки
├── schedule_service.py  # API расписания, кэш
├── notifications.py     # Напоминания о парах
├── storage.py           # SQLite
├── formatters.py        # Текст сообщений
├── keyboards.py         # Клавиатура и меню команд
├── config.py            # Настройки и константы
├── timezone_utils.py    # Время по Москве
├── mospolytech_api/     # Клиент rasp.dmami.ru
├── hash_salt.txt        # Для API (из репозитория mospolytech_api)
├── requirements.txt
├── .env.example
└── deploy/
    └── mospolytech-bot.service   # Пример unit для systemd
```

---

## Требования

- Python 3.10+
- Токен бота от [@BotFather](https://t.me/BotFather)
- Доступ к `api.telegram.org` (на части сетей в РФ нужен VPN)

---

## Установка и запуск (локально)

```bash
cd путь/к/тгбот
python -m venv .venv
```

**Windows:**

```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Отредактируйте .env: BOT_TOKEN=...
.\.venv\Scripts\python main.py
```

**Linux / macOS:**

```bash
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# nano .env — BOT_TOKEN=...
python main.py
```

В логе должно появиться `Application started`. Остановка: `Ctrl+C`.

> Используйте Python из `.venv`. Команда `python main.py` без venv выдаст `No module named 'telegram'`.

### Переменные окружения (`.env`)

| Переменная | Описание |
|------------|----------|
| `BOT_TOKEN` | Токен от BotFather (обязательно) |
| `BOT_TIMEZONE` | Часовой пояс расписания (по умолчанию `Europe/Moscow`) |

---

## Запуск на VPS (Ubuntu)

Один экземпляр бота: не запускайте одновременно на ПК и на сервере (будет `409 Conflict`).

```bash
cd /opt/тгбот   # или ваш путь к проекту

apt install -y python3 python3-venv
rm -rf .venv
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt

nano .env   # BOT_TOKEN=...
```

**systemd** (путь в unit подставьте свой; пример в `deploy/mospolytech-bot.service`):

```bash
cp deploy/mospolytech-bot.service /etc/systemd/system/mospolytech-bot.service
# В файле замените WorkingDirectory и ExecStart на ваш путь, например /opt/тгбот

systemctl daemon-reload
systemctl enable mospolytech-bot
systemctl start mospolytech-bot
systemctl status mospolytech-bot
```

Логи: `journalctl -u mospolytech-bot -f`

После закрытия SSH бот продолжит работать, если запущен через `systemctl`, а не `./.venv/bin/python main.py` в сессии терминала.

**Минимальный VPS:** 1 CPU, 512 MB–1 GB RAM, Ubuntu 22.04 LTS. Домен не нужен (long polling).

---

## Конфигурация (`config.py`)

| Параметр | Значение | Назначение |
|----------|----------|------------|
| `NOTIFY_CHECK_INTERVAL` | 60 | Интервал проверки напоминаний (сек) |
| `DEFAULT_NOTIFY_MINUTES` | 15 | Напоминание по умолчанию |
| `SCHEDULE_CACHE_TTL` | 1800 | Кэш расписания (сек) |
| `GROUPS_CACHE_TTL` | 3600 | Кэш списка групп (сек) |
| `DB_PATH` | `bot_data.db` | База настроек |

---

## Безопасность

- Не коммитьте `.env` и `bot_data.db` (уже в `.gitignore`).
- Токен не публикуйте; при утечке — `/revoke` в BotFather и новый токен.

---

## Ограничения

- Нет уведомлений об **изменениях** расписания (переносы) — только напоминания **до** пары.
- Зависимость от доступности rasp.dmami.ru и Telegram API.

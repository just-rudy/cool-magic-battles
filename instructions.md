# Инструкция по проекту «Крутые магические битвы»

Онлайн-реализация настольной колодостроительной игры. Стек: **Python 3.11 + FastAPI + PostgreSQL + SQLAlchemy** (бэкенд), **React + TypeScript + Vite** (фронтенд).

---

## Содержание

1. [Быстрый старт](#быстрый-старт)
2. [Команды](#команды)
3. [Структура репозитория](#структура-репозитория)
4. [Бэкенд (`src/`)](#бэкенд-src)
5. [Фронтенд (`frontend/`)](#фронтенд-frontend)
6. [Документация и отчётность](#документация-и-отчётность)
7. [База данных](#база-данных)
8. [API и Swagger](#api-и-swagger)

---

## Быстрый старт

```bash
cd ~/cool-magic-battles

# 1. Зависимости Python
pip install -r requirements.txt

# 2. Переменные окружения
cp env.example .env
# для локального PostgreSQL (без Docker) строка уже подходит:
# DATABASE_URL=postgresql+psycopg:///cool_magic_battles

# 3. База (локальный PostgreSQL, один раз)
psql -d postgres -c "CREATE DATABASE cool_magic_battles OWNER $USER;"
make db-migrate
make db-seed

# 4. Запуск (два терминала)
make run-api        # http://localhost:8000
make run-frontend   # http://localhost:5173
```

Альтернатива — PostgreSQL в Docker (порт **5433**, см. [База данных](#база-данных)).

---

## Команды

### Установка

| Команда | Описание |
|---------|----------|
| `make install` | Установить Python-зависимости из `requirements.txt` |
| `cd frontend && npm install` | Установить зависимости фронтенда |

### API (бэкенд)

| Команда | Описание |
|---------|----------|
| `make run-api` | Запустить FastAPI с hot-reload на **http://localhost:8000** |
| `PYTHONPATH=src uvicorn api.app:app --reload --host 0.0.0.0 --port 8000` | То же вручную |

**Swagger (интерактивная документация API):**

| URL | Описание |
|-----|----------|
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/openapi.json | OpenAPI-схема (JSON) |

### Фронтенд

| Команда | Описание |
|---------|----------|
| `make run-frontend` | Dev-сервер Vite на **http://localhost:5173** |
| `cd frontend && npm run dev` | То же вручную |
| `cd frontend && npm run build` | Production-сборка в `frontend/dist/` |
| `cd frontend && npm run preview` | Просмотр production-сборки |
| `cd frontend && npm run lint` | ESLint |

Прокси: запросы с фронта на `/api/*` уходят на `localhost:8000` (см. `frontend/vite.config.ts`).

### База данных — Make

| Команда | Описание |
|---------|----------|
| `make db-check` | Проверить подключение к **локальной** БД `cool_magic_battles` |
| `make db-up` | Поднять PostgreSQL в Docker (порт **5433**) |
| `make db-down` | Остановить контейнеры Docker Compose |
| `make db-wait` | Ждать готовности PostgreSQL в Docker |
| `make db-migrate` | Применить миграции Alembic (`upgrade head`) |
| `make db-seed` | Добавить тестовых пользователей (`gandalf`, `saruman`, `radagast`) |
| `make db-reset` | Откатить миграции → применить заново → seed |
| `make db-stamp` | Пометить схему как актуальную, если таблицы уже есть без `alembic_version` |

> Docker-команды в Makefile вызываются через `sg docker`, чтобы обойти проблему «группа docker не подхватилась в текущем терминале» после `usermod -aG docker $USER`.

### База данных — скрипт `scripts/db.py`

```bash
# из корня проекта, с PYTHONPATH=src
PYTHONPATH=src python3 scripts/db.py upgrade      # применить миграции
PYTHONPATH=src python3 scripts/db.py downgrade    # откат на 1 шаг
PYTHONPATH=src python3 scripts/db.py downgrade 001_initial  # до конкретной ревизии
PYTHONPATH=src python3 scripts/db.py current      # текущая ревизия
PYTHONPATH=src python3 scripts/db.py seed         # тестовые пользователи
PYTHONPATH=src python3 scripts/db.py revision "описание" --autogenerate  # новая миграция
```

### База данных — Alembic напрямую

> Не используйте `python -m alembic` из корня проекта — каталог `./alembic/` конфликтует с пакетом.  
> Используйте `scripts/db.py`, `make db-migrate` или бинарник `alembic` из venv.

```bash
cd ~/cool-magic-battles
export PYTHONPATH=src
# DATABASE_URL берётся из .env / config.yaml

alembic current          # текущая версия схемы
alembic history          # история миграций
alembic upgrade head     # применить все
alembic downgrade -1     # откат на одну
alembic stamp head       # «подписать» существующую схему

# или через обёртку (рекомендуется):
python3 scripts/db.py current
python3 scripts/db.py upgrade
python3 scripts/db.py stamp
```

### Открыть / подключиться к БД (psql)

**Локальный PostgreSQL (порт 5432, peer auth):**

```bash
psql -d cool_magic_battles
```

**Docker PostgreSQL (порт 5433):**

```bash
psql "postgresql://cmb:cmb@localhost:5433/cool_magic_battles"
# или
make db-up
sg docker -c "docker-compose exec db psql -U cmb -d cool_magic_battles"
```

**Полезные SQL-запросы в psql:**

```sql
\dt                          -- список таблиц
SELECT * FROM users;
SELECT * FROM games;
SELECT version_num FROM alembic_version;
```

### Очистить / сбросить БД

**Вариант A — через миграции (сохраняется пустая схема):**

```bash
make db-reset
# или
PYTHONPATH=src python3 scripts/db.py downgrade base
PYTHONPATH=src python3 scripts/db.py upgrade
make db-seed
```

**Вариант B — удалить все данные, оставить таблицы:**

```bash
psql -d cool_magic_battles <<'SQL'
TRUNCATE deck_cards, decks, players, games, cards, users CASCADE;
SQL
```

**Вариант C — полностью удалить БД (локально):**

```bash
psql -d postgres -c "DROP DATABASE IF EXISTS cool_magic_battles;"
psql -d postgres -c "CREATE DATABASE cool_magic_battles OWNER $USER;"
make db-migrate
make db-seed
```

**Вариант D — Docker: удалить контейнер и том (все данные в контейнере):**

```bash
make db-down
sg docker -c "docker-compose down -v"   # -v удаляет volume pgdata
make db-up
make db-wait
# в .env переключить на Docker URL:
# DATABASE_URL=postgresql+psycopg://cmb:cmb@localhost:5433/cool_magic_battles
make db-migrate
make db-seed
```

### Консольное приложение (без HTTP)

```bash
PYTHONPATH=src python3 -m main
```

Интерактивная CLI для отладки игровой логики (создание игры, колод, ходов).

### Тесты

```bash
cd ~/cool-magic-battles
PYTHONPATH=src pytest src/tests/
PYTHONPATH=src pytest src/tests/domain/          # юнит-тесты логики
PYTHONPATH=src pytest src/tests/integration/   # репозитории (SQLite in-memory)
```

### Линтеры (Python)

```bash
ruff check src/
mypy src/
```

---

## Структура репозитория

```
cool-magic-battles/
├── src/                    # Исходный код бэкенда (Python)
├── frontend/               # Веб-клиент (React)
├── alembic/                # Миграции БД
├── scripts/                # Вспомогательные скрипты
├── docs/                   # Диаграммы (UML, C4, DBML, draw.io)
├── img/                    # Экспорт диаграмм (PNG)
├── labs/                   # Материалы лабораторных работ
├── report/                 # Курсовая (LaTeX)
├── logs/                   # Логи приложения
├── instructions.md         # Этот файл
├── README.md               # Описание предметной области и архитектуры
├── attributes.md           # Игровые атрибуты (ОЗ, эхо, памятки и т.д.)
├── Makefile                # Команды для БД, API, фронта
├── docker-compose.yml      # PostgreSQL в Docker
├── env.example             # Шаблон .env
├── alembic.ini             # Конфиг Alembic
├── requirements.txt        # Python-зависимости
└── pyproject.toml          # Настройки ruff, mypy, pytest
```

### Корневые файлы

| Файл | Назначение |
|------|------------|
| `README.md` | Описание игры, акторы, сценарии, C4, ER, технологический стек |
| `attributes.md` | Памятка по игровым терминам (HP, эхо, памятки, колоды) |
| `instructions.md` | Инструкция по запуску и структуре проекта |
| `Makefile` | Сокращения для Docker, миграций, API, фронта |
| `docker-compose.yml` | Сервис `db`: PostgreSQL 16, порт **5433→5432** |
| `env.example` | Шаблон `DATABASE_URL` (локально / Docker) |
| `.env` | Локальные секреты и URL БД (не в git, создаётся из `env.example`) |
| `requirements.txt` | Зависимости: FastAPI, SQLAlchemy, psycopg, alembic, uvicorn, pytest… |
| `pyproject.toml` | Конфигурация ruff, mypy, pytest |
| `alembic.ini` | Точка входа Alembic (`script_location = alembic`) |

### `alembic/` — миграции

| Путь | Назначение |
|------|------------|
| `alembic/env.py` | Подключение к БД через `config.load_config()`, metadata из ORM |
| `alembic/script.py.mako` | Шаблон новых миграций |
| `alembic/versions/001_initial_schema.py` | Первая миграция: `users`, `games`, `players`, `cards`, `decks`, `deck_cards` |

### `scripts/`

| Файл | Назначение |
|------|------------|
| `scripts/db.py` | CLI: `upgrade`, `downgrade`, `seed`, `revision`, `current` |
| `scripts/setup_postgres_native.sh` | Создание роли `cmb` и БД без Docker (нужен `sudo`) |

### `docs/` и `img/`

| Каталог | Назначение |
|---------|------------|
| `docs/` | Исходники диаграмм: `.puml`, `.graphml`, `.drawio`, `db-diagram.dbml` |
| `img/` | PNG-экспорты для README (C4, ER, BPMN, sequence diagrams) |
| `labs/` | Тексты лабораторных работ (`lab_01.md` … `lab_05.md`) |
| `report/` | Исходники курсовой работы (LaTeX, `coursework.tex`, главы, библиография) |
| `logs/` | Файл логов (`app.log`), путь задаётся в `config.yaml` |

---

## Бэкенд (`src/`)

Архитектура: **Domain → Application → Infrastructure → API**.

```
src/
├── main.py                 # Точка входа консольного приложения
├── main_test.py            # Вспомогательный скрипт для тестов
├── api/                    # HTTP-слой (FastAPI)
├── application/            # Сценарии, сервисы, DTO, интерфейсы репозиториев
├── domain/                 # Сущности и перечисления (чистая логика)
├── infrastructure/         # БД, консольный UI, логирование
├── bootstrap/              # Сборка зависимостей (DI-контейнер)
├── config/                 # config.yaml, load_config()
└── tests/                  # pytest: domain + integration
```

### `src/api/` — REST API

| Файл | Назначение |
|------|------------|
| `api/app.py` | FastAPI-приложение, CORS, подключение роутеров |
| `api/dependencies.py` | DI: сессия SQLAlchemy, `GameAppService` |
| `api/routers/games.py` | Игры: создать, join, start, play, buy, end-turn, get |
| `api/routers/users.py` | Пользователи: register, list, get |
| `api/appendenceies.py` | Устаревший черновик зависимостей (не используется в `app.py`) |

**Префиксы API:**

- `/api/v1/game/...` — игровые операции
- `/api/v1/users/...` — пользователи

### `src/application/` — прикладной слой

| Путь | Назначение |
|------|------------|
| `application/dto/requests.py` | Pydantic-модели запросов (`CreateGameRequest`, `PlayCardRequest`, …) |
| `application/dto/responses.py` | Pydantic-модели ответов (`GameResponse`, `PlayerResponse`, `CardResponse`) |
| `application/services/game_service.py` | Фасад API: создание игры, миграция колод при старте, ходы |
| `application/services/game_logic.py` | Правила: join, play, buy, end_turn, start |
| `application/services/card_logic.py` | Можно ли сыграть/купить карту, эффекты |
| `application/services/deck_service.py` | Перемешивание, добор карт |
| `application/services/game_state_manager.py` | Валидация хода, смена игрока |
| `application/controllers/` | Контроллеры для **консоли** (богаче, чем HTTP-слой) |
| `application/interfaces/` | Абстракции репозиториев (`GameRepository`, `UserRepository`, …) |

### `src/domain/` — домен

| Путь | Назначение |
|------|------------|
| `domain/entities/game.py` | Игра: статус, игроки, колоды рынка/банка |
| `domain/entities/player.py` | Игрок: ОЗ, эхо, колоды (рука, стол, добор, сброс) |
| `domain/entities/card.py` | Карта: сила, цена, эхо, крутость |
| `domain/entities/deck.py` | Колода карт |
| `domain/entities/user.py` | Пользователь системы |
| `domain/enums.py` | `GameStatus`, `CardType`, `DeckType` |

### `src/infrastructure/` — инфраструктура

| Путь | Назначение |
|------|------------|
| `infrastructure/db/models/` | SQLAlchemy ORM: `UserModel`, `GameModel`, `PlayerModel`, `CardModel`, `DeckModel`, `DeckCardModel` |
| `infrastructure/db/mappers/` | Преобразование ORM ↔ domain entities |
| `infrastructure/db/repositories/` | `SqlAlchemyGameRepository`, `SqlAlchemyUserRepository`, … |
| `infrastructure/db/exceptions/` | `EntityNotFoundError`, `PersistenceError`, … |
| `infrastructure/db/base.py` | `DeclarativeBase` |
| `infrastructure/db/utils.py` | `create_tables` / `drop_tables` (без Alembic) |
| `infrastructure/db/session.py` | Настройка сессий |
| `infrastructure/ui/console/` | CLI: меню, команды, форматирование (Rich) |
| `infrastructure/ui/api/main.py` | Заглушка health-check (не основной API) |
| `infrastructure/logging/logger.py` | Логирование в файл |

### `src/bootstrap/`

| Файл | Назначение |
|------|------------|
| `bootstrap/container.py` | Сборка консольного приложения и зависимостей |

### `src/config/`

| Файл | Назначение |
|------|------------|
| `config/config.yaml` | URL БД, размер руки/рынка, путь к логу |
| `config/config.py` | `load_config()`: читает yaml + `.env` (`DATABASE_URL`) |

### `src/tests/`

| Путь | Назначение |
|------|------------|
| `tests/domain/` | Тесты `GameLogic`, `CardLogic`, `DeckService`, `GameController` |
| `tests/integration/` | Тесты репозиториев на SQLite in-memory |
| `tests/integration/conftest.py` | Фикстуры engine/session |

---

## Фронтенд (`frontend/`)

SPA на React 19 + Vite 8 + TypeScript + Tailwind CSS 4.

```
frontend/
├── public/                 # Статика (favicon, icons)
├── src/
│   ├── main.tsx            # Точка входа React
│   ├── App.tsx             # Роутинг: / и /game/:gameId
│   ├── index.css           # Tailwind + тема
│   ├── app/
│   │   └── providers.tsx   # React Query provider
│   ├── pages/
│   │   ├── HomePage.tsx    # Лобби: регистрация, создать/войти в игру
│   │   └── GamePage.tsx    # Игровой стол
│   ├── features/game/
│   │   ├── components/     # GameBoard, PlayersBar
│   │   └── hooks/          # useGame, useGameActions (polling)
│   ├── entities/
│   │   ├── game/           # types.ts, gameApi.ts
│   │   └── user/           # userApi.ts
│   ├── shared/
│   │   ├── api/client.ts   # axios → /api/v1
│   │   ├── store/          # zustand: сессия (userId, gameId, playerId)
│   │   ├── ui/             # CardTile, Layout
│   │   └── lib/game.ts     # хелперы (isMyTurn, findPlayer)
│   ├── views/              # Доп. компоненты (legacy / черновики)
│   ├── presenters/         # Presenter-слой (черновик)
│   └── services/           # Дубликаты API (legacy)
├── vite.config.ts          # alias @, proxy /api → :8000
├── package.json
├── tsconfig*.json
├── tailwind.config.js
└── postcss.config.js
```

| Файл / каталог | Назначение |
|----------------|------------|
| `vite.config.ts` | Плагины React + Tailwind, proxy API, alias `@/` → `src/` |
| `src/pages/HomePage.tsx` | Регистрация мага, создание игры, join по UUID |
| `src/pages/GamePage.tsx` | Загрузка состояния игры, игровой UI |
| `src/features/game/components/GameBoard.tsx` | Рынок, рука, стол, кнопки хода |
| `src/entities/game/api/gameApi.ts` | HTTP: create, join, start, play, buy, end-turn, get |
| `src/shared/store/sessionStore.ts` | localStorage: userId, gameId, playerId |

**Маршруты UI:**

| URL | Страница |
|-----|----------|
| http://localhost:5173/ | Лобби |
| http://localhost:5173/game/{uuid} | Игровой стол |

---

## Документация и отчётность

| Ресурс | Описание |
|--------|----------|
| `README.md` | Основное описание проекта для репозитория |
| `attributes.md` | Игровые термины |
| `docs/db-diagram.dbml` | ER-диаграмма для dbdiagram.io |
| `docs/*.puml` | UML/C4 в PlantUML |
| `report/coursework.tex` | Курсовая работа (LaTeX) |

---

## База данных

### Схема (таблицы)

| Таблица | Содержимое |
|---------|------------|
| `users` | Пользователи системы (`id`, `username`) |
| `games` | Игровые сессии (`status`, `cur_turn`, `cur_player_id`, `host_user_id`) |
| `players` | Игроки в партии (`health`, `cur_echo`, `hand_size`, …) |
| `cards` | Шаблоны/экземпляры карт |
| `decks` | Колоды (рынок, рука, стол, добор, сброс, банк) |
| `deck_cards` | Связь колода ↔ карта + позиция |
| `alembic_version` | Текущая версия миграции |

### Два способа подключения

| Режим | `DATABASE_URL` в `.env` |
|-------|-------------------------|
| **Локальный PostgreSQL** (порт 5432, peer auth) | `postgresql+psycopg:///cool_magic_battles` |
| **Docker** (порт **5433**) | `postgresql+psycopg://cmb:cmb@localhost:5433/cool_magic_battles` |

Приоритет URL: переменная **`DATABASE_URL`** в `.env` → иначе `src/config/config.yaml`.

### Docker и права

```bash
# если docker ps без sudo не работает — перелогин или:
newgrp docker
# Makefile уже использует sg docker для make db-up / db-down
```

---

## API и Swagger

После `make run-api`:

### Пользователи

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/users/register` | Регистрация `{"username": "..."}` |
| POST | `/api/v1/users/login` | Вход в существующий аккаунт `{"username": "..."}` |
| GET | `/api/v1/users` | Список пользователей |
| GET | `/api/v1/users/{user_id}` | Пользователь по ID |

### Игра

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/game/new` | Создать игру `{"host_user_id": "uuid"}` |
| GET | `/api/v1/game/{game_id}` | Состояние игры |
| POST | `/api/v1/game/{game_id}/join` | Присоединиться `{"user_id": "uuid"}` |
| POST | `/api/v1/game/{game_id}/start` | Старт (генерация колод) |
| POST | `/api/v1/game/{game_id}/play` | Сыграть карту |
| POST | `/api/v1/game/{game_id}/buy` | Купить с рынка |
| POST | `/api/v1/game/{game_id}/end-turn` | Завершить ход |

### Типичный сценарий через API

1. `POST /users/register` → получить `user_id`
2. `POST /game/new` → `game_id`
3. `POST /game/{id}/join` (для каждого игрока)
4. `POST /game/{id}/start`
5. `GET /game/{id}` — polling состояния
6. `play` / `buy` / `end-turn` по очереди

---

## Переменные окружения

| Переменная | Описание |
|------------|----------|
| `DATABASE_URL` | Строка подключения SQLAlchemy + psycopg |
| `DEFAULT_HAND_SIZE` | (опционально) размер руки |
| `DEFAULT_MARKET_SIZE` | (опционально) размер рынка |
| `LOG_FILE` | (опционально) путь к логу |

---

## Частые проблемы

| Симптом | Решение |
|---------|---------|
| `permission denied` на Docker | `sudo usermod -aG docker $USER`, новый терминал, или `make db-up` (использует `sg docker`) |
| Порт 5432 занят | Docker уже на **5433**; локальная БД — на 5432, не мешают |
| `relation "users" already exists` при migrate | `make db-stamp`, затем `make db-migrate` |
| API не видит БД | Проверить `.env`, `make db-check`, `make db-migrate` |
| Фронт не достучится до API | Запущен ли `make run-api`, proxy в `vite.config.ts` |
| `python` not found | Использовать `python3` |

---

## Шпаргалка «всё с нуля»

```bash
# Терминал 1 — бэкенд
cd ~/cool-magic-battles
pip install -r requirements.txt
cp env.example .env
make db-check || psql -d postgres -c "CREATE DATABASE cool_magic_battles OWNER $USER;"
make db-migrate && make db-seed
make run-api
# → Swagger: http://localhost:8000/docs

# Терминал 2 — фронт
cd ~/cool-magic-battles/frontend
npm install
npm run dev
# → UI: http://localhost:5173
```

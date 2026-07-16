# FastapiDockerSqlalchemyLayersTemplate

Стартовый шаблон **FastAPI**-приложения с **Docker**, **SQLAlchemy 2.0 async**, **Alembic** и **слойной архитектурой**.

Подходит как база для нового backend-сервиса: auth-модуль уже подключён, DAO-слой вынесен отдельно, миграции и Docker настроены.

## Возможности

- **FastAPI** + **Uvicorn** с lifespan-хуками и CORS
- **Async SQLAlchemy 2.0** — `BaseDAO` с CRUD, пагинацией, upsert, bulk update
- **Session manager** — зависимости `SessionDep` / `TransactionSessionDep` для FastAPI
- **Auth-модуль** — регистрация, login/logout, JWT в cookie, `/me`, admin-only эндпоинт
- **Alembic** — миграции в `app/migrations/`
- **Docker** — `Dockerfile` + `docker-compose.yml`
- **SQLite по умолчанию** — можно заменить на PostgreSQL через `DB_URL`

## Архитектура

Проект разделён на слои:

```
app/
├── main.py              # FastAPI app, CORS, роутеры
├── config.py            # Настройки из .env (Pydantic Settings)
├── exceptions.py        # HTTP-исключения
├── dao/                 # Общий слой доступа к данным
│   ├── database.py      # Engine, Base, async session maker
│   ├── base.py          # Generic BaseDAO
│   └── session_maker.py # DatabaseSessionManager + Depends
├── auth/                # Доменный модуль (пример)
│   ├── models.py        # SQLAlchemy: User, Role
│   ├── schemas.py       # Pydantic-схемы
│   ├── dao.py           # UsersDAO, RoleDAO
│   ├── auth.py          # JWT, authenticate_user
│   ├── dependencies.py  # get_current_user, get_current_admin_user
│   ├── router.py        # /auth/* эндпоинты
│   └── utils.py         # hash/verify password
└── migrations/          # Alembic
```

**Паттерн добавления нового модуля:** `models` → `schemas` → `dao` → `router` → `app.include_router(...)`.

## API

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| `POST` | `/auth/register/` | Регистрация | публичный |
| `POST` | `/auth/login/` | Авторизация (JWT в cookie + body) | публичный |
| `POST` | `/auth/logout/` | Выход | публичный |
| `GET` | `/auth/me/` | Текущий пользователь | авторизованный |
| `GET` | `/auth/all_users/` | Список пользователей | admin (role_id 3 или 4) |

Документация: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Быстрый старт

### 1. Клонирование

```bash
git clone https://github.com/fancyman00/FastapiDockerSqlalchemyLayersTemplate.git
cd FastapiDockerSqlalchemyLayersTemplate
```

### 2. Переменные окружения

Создайте `.env` в корне проекта:

```env
SECRET_KEY=change-me-openssl-rand-hex-32
ALGORITHM=HS256
# DB_URL=sqlite+aiosqlite:///./data/db.sqlite3   # опционально, есть дефолт
```

### 3. Локальный запуск

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

mkdir -p data
alembic upgrade head

uvicorn app.main:app --reload
```

### 4. Docker

```bash
docker compose up --build
```

Приложение будет доступно на порту **8000**.

> **Примечание:** в `docker-compose.yml` используется `network_mode: host`. Для изолированной сети Docker замените на обычный `networks` + `ports`.

## Миграции

```bash
# Применить миграции
alembic upgrade head

# Создать новую ревизию (после изменения models)
alembic revision --autogenerate -m "описание"
alembic upgrade head
```

## BaseDAO

`app/dao/base.py` — generic DAO для любой SQLAlchemy-модели:

- `find_one_or_none_by_id`, `find_one_or_none`, `find_all`
- `add`, `add_many`, `update`, `delete`
- `count`, `paginate`, `find_by_ids`
- `upsert`, `bulk_update`

Пример:

```python
from app.auth.dao import UsersDAO
from app.auth.schemas import EmailModel

user = await UsersDAO.find_one_or_none(
    session=session,
    filters=EmailModel(email="user@example.com"),
)
```

## Сессии и транзакции

`DatabaseSessionManager` предоставляет две FastAPI-зависимости:

| Зависимость | Поведение |
|-------------|-----------|
| `SessionDep` | сессия без автокоммита |
| `TransactionSessionDep` | сессия + commit/rollback |

```python
@router.post("/register/")
async def register_user(
    user_data: SUserRegister,
    session: AsyncSession = TransactionSessionDep,
):
    ...
```

## Стек

- Python 3.12
- [FastAPI](https://fastapi.tiangolo.com/) 0.115
- [SQLAlchemy](https://docs.sqlalchemy.org/) 2.0 (async)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Pydantic v2](https://docs.pydantic.dev/) + pydantic-settings
- [python-jose](https://python-jose.readthedocs.io/) (JWT)
- [passlib](https://passlib.readthedocs.io/) + bcrypt
- [loguru](https://github.com/Delgan/loguru)
- Docker + docker-compose

## Что можно улучшить для продакшена

- заменить SQLite на PostgreSQL (`asyncpg`)
- вынести JWT из cookie-only в Bearer + refresh tokens
- добавить rate-limit на `/auth/login`
- убрать `allow_origins=["*"]` в CORS
- добавить тесты (`pytest` + `httpx.AsyncClient`)

## Лицензия

MIT

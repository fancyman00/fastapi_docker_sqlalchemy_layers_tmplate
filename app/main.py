from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.auth.router import router as router_auth
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from contextlib import asynccontextmanager





@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет жизненным циклом приложения

    Args:
        app (FastAPI): Экземпляр приложения FastAPI
    """
    try:
        # Настройка и запуск сервиса
        logger.info("Сервис запущен")
        yield
    except Exception as e:
        logger.error(f"Ошибка инициализации сервиса: {e}")
    finally:
        # Завершение работы сервиса
        logger.info("Сервис остановлен")


app = FastAPI(lifespan=lifespan)

# Добавляем middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки
)

app.include_router(router_auth)

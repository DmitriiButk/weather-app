from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


from database.database import init_db
from routes.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Контекстный менеджер жизненного цикла приложения.
    """
    await init_db()
    yield


app = FastAPI(title="Прогноз погоды")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router)

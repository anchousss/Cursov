from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers import attempts, auth, tests, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Сервис тестов и опросов",
    description=(
        "Веб-API для создания и прохождения тестов. "
        "Поддерживает регистрацию, JWT-аутентификацию, CRUD тестов, "
        "добавление вопросов и прохождение попыток."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tests.router)
app.include_router(attempts.router)


@app.get("/", tags=["Служебное"], summary="Проверка доступности API")
async def root() -> dict:
    return {"status": "ok", "docs": "/docs", "redoc": "/redoc"}
# Сервис генерации тестов и опросов

Веб-API на FastAPI для создания и прохождения тестов.

## Возможности
- Регистрация и вход (JWT, bcrypt)
- CRUD тестов и вопросов
- Прохождение тестов и подсчёт результата
- Автоматическая документация Swagger UI (`/docs`) и ReDoc (`/redoc`)

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
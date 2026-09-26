# Сервис генерации тестов и опросов

Веб-API на FastAPI для создания и прохождения тестов.

## 🚀 Развёрнутое приложение

- **API:** https://artem.pythonanywhere.com/
- **Документация Swagger UI:** https://artem.pythonanywhere.com/docs
- **ReDoc:** https://artem.pythonanywhere.com/redoc

## Возможности

- Регистрация и вход (JWT + bcrypt)
- CRUD тестов и вопросов
- Прохождение тестов и подсчёт результата
- Автоматическая документация

## Стек

- Python 3.12
- FastAPI
- SQLAlchemy 2.0 (async)
- SQLite + aiosqlite
- Pydantic v2
- python-jose (JWT)
- passlib + bcrypt

## Локальный запуск

\`\`\`bash
git clone <repo-url>
cd fastapi-tests-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# заполнить SECRET_KEY
uvicorn app.main:app --reload
\`\`\`

API: http://127.0.0.1:8000
Документация: http://127.0.0.1:8000/docs

## Эндпоинты

### Аутентификация
- `POST /auth/register` — регистрация
- `POST /auth/login` — логин (OAuth2-форма)

### Пользователи
- `GET /users/me` — текущий пользователь (требует токен)

### Тесты
- `GET /tests/` — список опубликованных тестов
- `POST /tests/` — создать тест
- `GET /tests/{id}` — получить тест
- `PUT /tests/{id}` — обновить тест
- `DELETE /tests/{id}` — удалить тест
- `POST /tests/{id}/questions` — добавить вопрос

### Прохождение
- `POST /attempts/start/{test_id}` — начать попытку
- `POST /attempts/{id}/submit` — отправить ответы
- `GET /attempts/my` — мои попытки

## Развёртывание

Сервис развёрнут на PythonAnywhere в ASGI-режиме (uvicorn + UDS-сокет).
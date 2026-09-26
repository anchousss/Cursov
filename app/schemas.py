from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------- Пользователи ----------
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Варианты ответов ----------
class AnswerOptionCreate(BaseModel):
    text: str = Field(min_length=1)
    is_correct: bool = False


class AnswerOptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    is_correct: bool


# ---------- Вопросы ----------
class QuestionCreate(BaseModel):
    text: str = Field(min_length=1)
    question_type: Literal["single", "multiple", "text"] = "single"
    order_num: int = 0
    options: list[AnswerOptionCreate] = []


class QuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    question_type: str
    order_num: int
    options: list[AnswerOptionRead] = []


# ---------- Тесты ----------
class TestCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = None
    is_published: bool = False


class TestUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = None
    is_published: bool | None = None


class TestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    is_published: bool
    author_id: int
    created_at: datetime


class TestReadFull(TestRead):
    questions: list[QuestionRead] = []


# ---------- Попытки ----------
class AnswerSubmit(BaseModel):
    question_id: int
    option_id: int | None = None
    text_answer: str | None = None


class AttemptStart(BaseModel):
    test_id: int


class AttemptSubmit(BaseModel):
    answers: list[AnswerSubmit]


class AttemptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    test_id: int
    user_id: int
    started_at: datetime
    finished_at: datetime | None
    score: int | None


class AttemptResult(BaseModel):
    attempt_id: int
    test_id: int
    total_questions: int
    correct_answers: int
    score_percent: float
    finished_at: datetime
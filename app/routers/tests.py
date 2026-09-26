from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.dependencies import get_current_user
from app.models import AnswerOption, Question, Test, User
from app.schemas import (
    QuestionCreate,
    QuestionRead,
    TestCreate,
    TestRead,
    TestReadFull,
    TestUpdate,
)

router = APIRouter(prefix="/tests", tags=["Тесты"])


async def _get_test_or_404(session: AsyncSession, test_id: int) -> Test:
    result = await session.execute(select(Test).where(Test.id == test_id))
    test = result.scalar_one_or_none()
    if test is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тест не найден")
    return test


@router.get(
    "/",
    response_model=list[TestRead],
    summary="Список тестов",
    description="Возвращает список всех опубликованных тестов.",
)
async def list_tests(session: AsyncSession = Depends(get_session)) -> list[Test]:
    result = await session.execute(select(Test).where(Test.is_published.is_(True)))
    return list(result.scalars().all())


@router.get(
    "/{test_id}",
    response_model=TestReadFull,
    summary="Получить тест по id",
    description="Возвращает тест вместе со списком вопросов и вариантов ответа.",
)
async def get_test(test_id: int, session: AsyncSession = Depends(get_session)) -> Test:
    result = await session.execute(
        select(Test)
        .where(Test.id == test_id)
        .options(selectinload(Test.questions).selectinload(Question.options))
    )
    test = result.scalar_one_or_none()
    if test is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тест не найден")
    return test


@router.post(
    "/",
    response_model=TestRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать тест",
    description="Создаёт новый тест. Требуется аутентификация.",
)
async def create_test(
    payload: TestCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Test:
    test = Test(
        title=payload.title,
        description=payload.description,
        is_published=payload.is_published,
        author_id=current_user.id,
    )
    session.add(test)
    await session.commit()
    await session.refresh(test)
    return test


@router.put(
    "/{test_id}",
    response_model=TestRead,
    summary="Обновить тест",
    description="Обновляет тест. Редактировать может только автор.",
)
async def update_test(
    test_id: int,
    payload: TestUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Test:
    test = await _get_test_or_404(session, test_id)
    if test.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на изменение теста")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(test, key, value)

    await session.commit()
    await session.refresh(test)
    return test


@router.delete(
    "/{test_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить тест",
    description="Удаляет тест. Удалять может только автор.",
)
async def delete_test(
    test_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    test = await _get_test_or_404(session, test_id)
    if test.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на удаление теста")
    await session.delete(test)
    await session.commit()


@router.post(
    "/{test_id}/questions",
    response_model=QuestionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить вопрос",
    description="Добавляет вопрос к тесту вместе с вариантами ответа.",
)
async def add_question(
    test_id: int,
    payload: QuestionCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Question:
    test = await _get_test_or_404(session, test_id)
    if test.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на изменение теста")

    question = Question(
        test_id=test.id,
        text=payload.text,
        question_type=payload.question_type,
        order_num=payload.order_num,
    )
    for opt in payload.options:
        question.options.append(AnswerOption(text=opt.text, is_correct=opt.is_correct))

    session.add(question)
    await session.commit()
    await session.refresh(question, attribute_names=["options"])
    return question

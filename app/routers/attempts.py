from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.dependencies import get_current_user
from app.models import AnswerOption, Attempt, AttemptAnswer, Question, Test, User
from app.schemas import AttemptRead, AttemptResult, AttemptSubmit

router = APIRouter(prefix="/attempts", tags=["Прохождение тестов"])


@router.post(
    "/start/{test_id}",
    response_model=AttemptRead,
    status_code=status.HTTP_201_CREATED,
    summary="Начать попытку прохождения теста",
    description="Создаёт новую попытку прохождения указанного теста.",
)
async def start_attempt(
    test_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Attempt:
    result = await session.execute(select(Test).where(Test.id == test_id))
    test = result.scalar_one_or_none()
    if test is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тест не найден")

    attempt = Attempt(test_id=test_id, user_id=current_user.id)
    session.add(attempt)
    await session.commit()
    await session.refresh(attempt)
    return attempt


@router.post(
    "/{attempt_id}/submit",
    response_model=AttemptResult,
    summary="Отправить ответы",
    description="Принимает ответы, проверяет их и возвращает результат.",
)
async def submit_attempt(
    attempt_id: int,
    payload: AttemptSubmit,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> AttemptResult:
    result = await session.execute(
        select(Attempt)
        .where(Attempt.id == attempt_id)
        .options(selectinload(Attempt.answers))
    )
    attempt = result.scalar_one_or_none()
    if attempt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Попытка не найдена")
    if attempt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к этой попытке")
    if attempt.finished_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Попытка уже завершена")

    questions_result = await session.execute(
        select(Question)
        .where(Question.test_id == attempt.test_id)
        .options(selectinload(Question.options))
    )
    questions = list(questions_result.scalars().all())
    if not questions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="В тесте нет вопросов")

    q_map = {q.id: q for q in questions}
    correct = 0

    for ans in payload.answers:
        question = q_map.get(ans.question_id)
        if question is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Вопрос {ans.question_id} не принадлежит этому тесту",
            )

        session.add(
            AttemptAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                option_id=ans.option_id,
                text_answer=ans.text_answer,
            )
        )

        if question.question_type in ("single", "multiple") and ans.option_id is not None:
            opt_result = await session.execute(
                select(AnswerOption).where(AnswerOption.id == ans.option_id)
            )
            option = opt_result.scalar_one_or_none()
            if option and option.question_id == question.id and option.is_correct:
                correct += 1

    attempt.finished_at = datetime.now(timezone.utc)
    attempt.score = correct
    await session.commit()
    await session.refresh(attempt)

    total = len(questions)
    percent = round(correct / total * 100, 2) if total else 0.0

    return AttemptResult(
        attempt_id=attempt.id,
        test_id=attempt.test_id,
        total_questions=total,
        correct_answers=correct,
        score_percent=percent,
        finished_at=attempt.finished_at,
    )


@router.get(
    "/my",
    response_model=list[AttemptRead],
    summary="Мои попытки",
    description="Возвращает список попыток текущего пользователя.",
)
async def my_attempts(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[Attempt]:
    result = await session.execute(
        select(Attempt).where(Attempt.user_id == current_user.id).order_by(Attempt.id.desc())
    )
    return list(result.scalars().all())
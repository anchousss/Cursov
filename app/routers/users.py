from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models import User
from app.schemas import UserRead

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get(
    "/me",
    response_model=UserRead,
    summary="Информация о текущем пользователе",
    description="Возвращает данные пользователя, которому принадлежит JWT-токен.",
)
async def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

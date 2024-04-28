"""Модуль для описания endpoint`ов к модели `Image`"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import y_blog_db
from Y_blog.check_user_token import token_required
from . import crud


router = APIRouter(prefix="/api/medias", tags=["Medias"])


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
@token_required
async def save_img(
    tweet_id: int,
    image_file: UploadFile,
    api_key: str,
    user_id: Annotated[int | None, Query(include_in_schema=False)] = None,
    session: AsyncSession = Depends(y_blog_db.session_dependency),
):
    """
    Endpoint для загрузки изображения, приложенного к твиту
    :param tweet_id: id твита
    :param image_file: загружаемая картинка
    :param api_key: api_key автора
    :param user_id: id автора
    :param session: объект сессии
    """
    return await crud.save_image(
        session=session,
        user_image=image_file,
        tweet_id=tweet_id,
        token=api_key,
        user_id=user_id,
    )

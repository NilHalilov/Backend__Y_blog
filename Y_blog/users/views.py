"""Модуль для описания endpoint`ов к модели `User`"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import y_blog_db
from Y_blog.check_user_token import token_required
from Y_blog.users import crud
from Y_blog.users.schemas import User, UserCreate


router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=dict, status_code=status.HTTP_200_OK)
@token_required
async def get_user_info(
    api_key: str,
    user_id: Annotated[int | None, Query(include_in_schema=False)] = None,
    session: AsyncSession = Depends(y_blog_db.session_dependency),
):
    """
    Endpoint для получения информации о пользователе по `api_key`
    :param api_key: api_key пользователя
    :param user_id: id пользователя
    :param session: объект сессии
    """
    return await crud.read_user_profile(
        session=session,
        user_id=user_id,
    )


@router.get("/{id}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_user_info_by_id(
    id: Annotated[int, Path(..., ge=1)],
    session: AsyncSession = Depends(y_blog_db.session_dependency),
):
    """
    Endpoint для получения информации о пользователе по `id`
    :param id: id пользователя
    :param session: объект сессии
    """
    return await crud.read_user_profile(session=session, user_id=id)


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    api_key: str,
    session: AsyncSession = Depends(y_blog_db.session_dependency),
):
    """
    Endpoint для создания нового пользователя
    :param user: информация о пользователе
    :param api_key: api_key пользователя
    :param session: объект сессии
    """
    return await crud.create_user(session=session, new_user=user, token=api_key)


@router.post("/{id}/follow/", response_model=dict, status_code=status.HTTP_201_CREATED)
@token_required
async def follow(
    api_key: str,
    id: Annotated[int, Path(..., ge=1)],
    user_id: Annotated[int | None, Query(include_in_schema=False)] = None,
    session: AsyncSession = Depends(y_blog_db.session_dependency),
):
    """
    Endpoint, чтобы подписаться на пользователя
    :param api_key: api_key подписчика
    :param id: id пользователя, на которого нужно подписаться
    :param user_id: id подписчика
    :param session: объект сессии
    """
    return await crud.create_user_follower(
        session=session, main_user_id=id, follower_id=user_id
    )


@router.delete("/{id}/follow/", response_model=dict, status_code=status.HTTP_200_OK)
@token_required
async def unfollow(
    api_key: str,
    id: Annotated[int, Path(..., ge=1)],
    user_id: Annotated[int | None, Query(include_in_schema=False)] = None,
    session: AsyncSession = Depends(y_blog_db.session_dependency),
):
    """
    Endpoint, чтобы отписаться от пользователя
    :param api_key: api_key подписчика
    :param id: id пользователя, от которого нужно подписаться
    :param user_id: id подписчика
    :param session: объект сессии
    """
    return await crud.delete_user_follower(
        session=session,
        main_user_id=id,
        follower_id=user_id,
    )

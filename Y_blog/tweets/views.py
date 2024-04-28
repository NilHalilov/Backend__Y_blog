"""Модуль для описания endpoint`ов к модели `Tweet`"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import y_blog_db
from Y_blog.check_user_token import token_required
from . import crud
from .schemas import TweetCreate


router = APIRouter(prefix="/api/tweets", tags=["Tweets"])


@router.get("/", response_model=dict, status_code=status.HTTP_200_OK)
@token_required
async def get_tweets(
    api_key: str,
    user_id: Annotated[int | None, Query(include_in_schema=False)] = None,
    session: AsyncSession = Depends(y_blog_db.session_dependency),
):
    """
    Endpoint для получения списка твитов тех, на кого подписан пользователь
    :param api_key: api_key пользователя
    :param user_id: id пользователя
    :param session: объект сессии
    """
    return await crud.read_user_tweets_list(session=session, user_id=user_id)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
@token_required
async def post_tweet(
    new_tweet: TweetCreate,
    api_key: str,
    user_id: Annotated[int | None, Query(include_in_schema=False)] = None,
    session: AsyncSession = Depends(y_blog_db.session_dependency),
):
    """
    Endpoint для отправки нового твита
    :param new_tweet: содержимое твита
    :param api_key: api_key пользователя
    :param user_id: id пользователя
    :param session: объект сессии
    """
    return await crud.create_tweet(
        session=session, new_tweet=new_tweet, user_id=user_id
    )


@router.delete("/{tweet_id}/", response_model=dict, status_code=status.HTTP_200_OK)
@token_required
async def del_tweet(
    tweet_id: Annotated[int, Path(..., ge=1)],
    api_key: str,
    user_id: Annotated[int | None, Query(include_in_schema=False)] = None,
    session: AsyncSession = Depends(y_blog_db.session_dependency),
):
    """
    Endpoint для удаления твита
    :param tweet_id: id удаляемого твита
    :param api_key: api_key пользователя
    :param user_id: id пользователя
    :param session: объект сессии
    """
    return await crud.delete_tweet(
        session=session,
        user_id=user_id,
        tweet_id=tweet_id,
    )


@router.post(
    "/{tweet_id}/likes/", response_model=dict, status_code=status.HTTP_201_CREATED
)
@token_required
async def like_tweet(
    tweet_id: Annotated[int, Path(..., ge=1)],
    api_key: str,
    user_id: Annotated[int, None, Query(include_in_schema=False)] = None,
    session: AsyncSession = Depends(y_blog_db.session_dependency),
):
    """
    Endpoint чтобы лайкнуть твит
    :param tweet_id: id понравившегося твита
    :param api_key: api_key пользователя
    :param user_id: id пользователя
    :param session: объект сессии
    """
    return await crud.create_like(
        session=session,
        user_id=user_id,
        tweet_id=tweet_id,
    )


@router.delete(
    "/{tweet_id}/likes/", response_model=dict, status_code=status.HTTP_200_OK
)
@token_required
async def dislike_tweet(
    tweet_id: Annotated[int, Path(..., ge=1)],
    api_key: str,
    user_id: Annotated[int, None, Query(include_in_schema=False)] = None,
    session: AsyncSession = Depends(y_blog_db.session_dependency),
):
    """
    Endpoint, чтобы убрать лайк с твита
    :param tweet_id: id твита
    :param api_key: api_key пользователя
    :param user_id: id пользователя
    :param session: объект сессии
    """
    return await crud.delete_like(
        session=session,
        user_id=user_id,
        tweet_id=tweet_id,
    )

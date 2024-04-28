"""Модуль для описания CRUD-действий модели `User`"""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from models.followers import FollowerModel
from models.user import UserModel
from Y_blog.users.schemas import UserCreate


async def create_user(
    session: AsyncSession, new_user: UserCreate, token: str
) -> UserModel:
    """
    Создание в БД новой записи пользователя
    :param session: объект сессии
    :param new_user: информация о новом пользователе
    :param token: api_key нового пользователя
    """
    user = UserModel(**new_user.model_dump(), token=token)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def create_user_follower(
    session: AsyncSession, main_user_id: int, follower_id: int
) -> dict:
    """
    Создание в БД новой записи подписчика
    :param session: объект сессии
    :param main_user_id: id пользователя на которого подписались
    :param follower_id: id подписчика
    """
    if main_user_id == follower_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can't follow yourself :("
        )

    query_relationship = (
        select(FollowerModel)
        .options(joinedload(FollowerModel.follow_to))
        .where(
            FollowerModel.following_id == main_user_id,
            FollowerModel.followers_id == follower_id,
        )
    )
    relationship_result: FollowerModel | None = await session.scalar(query_relationship)

    if relationship_result is None:
        try:
            new_relationship = FollowerModel(
                following_id=main_user_id, followers_id=follower_id
            )
            session.add(new_relationship)
            await session.commit()

            return {
                "result": True,
            }
        except IntegrityError:
            return {
                "result": False,
                "ERROR": f"You can't follow user with id={main_user_id}, because he doesn't exist.",
            }
        finally:
            await session.close()

    else:
        return {
            "result": False,
            "message": f"You have already follow user '{relationship_result.follow_to.nickname}'!",
        }


async def delete_user_follower(
    session: AsyncSession, main_user_id: int, follower_id: int
) -> dict:
    """
    Удаление из БД записи о подписчике
    :param session: объект сессии
    :param main_user_id: id пользователя на которого была подписка
    :param follower_id: id подписчика
    """
    if main_user_id == follower_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't unfollow yourself ;)",
        )

    query_relationship = select(FollowerModel).where(
        FollowerModel.following_id == main_user_id,
        FollowerModel.followers_id == follower_id,
    )
    relationship_result: FollowerModel | None = await session.scalar(query_relationship)

    if relationship_result is not None:
        await session.delete(relationship_result)
        await session.commit()
        await session.close()
        return {
            "result": True,
        }

    else:
        return {"result": False, "message": f"You are not follow this user yet!"}


async def read_user_profile(session: AsyncSession, user_id: int) -> dict:
    """
    Получение из БД информации о пользователе
    :param session: объект сессии
    :param user_id: id пользователя
    """
    query = (
        select(UserModel)
        .options(
            selectinload(UserModel.follower_list).joinedload(FollowerModel.follow_to),
            selectinload(UserModel.following_list).joinedload(FollowerModel.follow_by),
        )
        .where(UserModel.id == user_id)
    )
    result: UserModel | None = await session.scalar(query)
    all_user_subscriptions = []
    all_user_subscribers = []

    if result is not None:

        if result.follower_list is not None:
            for i_user in result.follower_list:
                subscriptions_info = {
                    "id": i_user.follow_to.id,
                    "name": i_user.follow_to.nickname,
                }
                all_user_subscriptions.append(subscriptions_info)

        if result.following_list is not None:
            for i_user in result.following_list:
                subscribers_info = {
                    "id": i_user.follow_by.id,
                    "name": i_user.follow_by.nickname,
                }
                all_user_subscribers.append(subscribers_info)

        return {
            "result": True,
            "user": {
                "id": result.id,
                "name": result.nickname,
                "followers": all_user_subscribers,
                "following": all_user_subscriptions,
            },
        }
    await session.close()

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User id=`{user_id}` not found !"
    )

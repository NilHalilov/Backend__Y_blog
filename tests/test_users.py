"""Модуль для тестов endpoint`ов связанных с моделью `User`"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from .conftest import test_db
from models.user import UserModel
from models.followers import FollowerModel


@pytest.mark.asyncio(scope="session")
async def test_get_user_info(ac: AsyncClient):
    """Тест на получение информации о пользователе по `api_key`"""
    async with test_db.async_session() as session:
        test_user: UserModel = UserModel(
            name="Cammy", nickname="Hooligan", email="C@capcom.com", token="ccc"
        )

        session.add(test_user)
        await session.commit()
        response = await ac.get(f"api/users/me?api_key={test_user.token}")

        assert response.status_code == 200
        assert (
            test_user.id == response.json()["user"]["id"]
        ), "Запрашиваемый id не совпадает с возвращаемым id"


@pytest.mark.asyncio(scope="session")
async def test_get_user_by_id(ac: AsyncClient):
    """Тест на получение информации о пользователе по `id`"""
    async with test_db.async_session() as session:
        test_user: UserModel = UserModel(
            name="Ken", nickname="Tatsumaka", email="K@capcom.com", token="kkk"
        )

        session.add(test_user)
        await session.commit()
        response = await ac.get(f"api/users/{test_user.id}")

        assert response.status_code == 200
        assert (
            test_user.id == response.json()["user"]["id"]
        ), "Запрашиваемый id не совпадает с возвращаемым id"


@pytest.mark.asyncio(scope="session")
async def test_create_user(ac: AsyncClient):
    """Тест на создание нового пользователя"""
    response = await ac.post(
        "api/users/?api_key=lll",
        json={
            "name": "LILY",
            "nickname": "WING_DEATH",
            "email": "L@capcom.com",
        },
    )

    async with test_db.async_session() as session:
        query = select(UserModel).where(UserModel.token == "lll")
        result = await session.scalar(query)

    assert response.status_code == 201
    assert (
        result.id == response.json()["id"]
    ), "Запрашиваемый id не совпадает с возвращаемым id"


@pytest.mark.asyncio(scope="session")
async def test_follow(ac: AsyncClient):
    """Тест на создание подписки на пользователя"""
    async with test_db.async_session() as session:
        test_user: UserModel = UserModel(
            name="Ryu", nickname="Hadouken", email="R@capcom.com", token="rrr"
        )
        test_follower: UserModel = UserModel(
            name="EvilRyu", nickname="EvilHadouken", email="ER@capcom.com", token="eee"
        )
        session.add(test_user)
        session.add(test_follower)
        await session.commit()

    response = await ac.post(
        f"api/users/{test_user.id}/follow/?api_key={test_follower.token}"
    )

    assert response.status_code == 201
    assert response.json()["result"] is True


@pytest.mark.asyncio(scope="session")
async def test_unfollow(ac: AsyncClient):
    """Тест на удаление подписки на пользователя"""
    async with test_db.async_session() as session:
        test_user: UserModel = UserModel(
            name="M.Bison", nickname="Shadaloo", email="MB@capcom.com", token="bbb"
        )
        test_follower: UserModel = UserModel(
            name="Ed", nickname="Jab_jab", email="Ed@capcom.com", token="e11"
        )

        session.add(test_user)
        session.add(test_follower)
        await session.commit()

        test_relationship = FollowerModel(
            following_id=test_user.id,
            followers_id=test_follower.id,
        )
        session.add(test_relationship)
        await session.commit()

        query = select(FollowerModel).where(FollowerModel.following_id == test_user.id)
        result = await session.scalar(query)
        assert result is not None

        response = await ac.delete(
            f"api/users/{test_user.id}/follow/?api_key={test_follower.token}"
        )
        result = await session.scalar(query)
        assert result is None

    assert response.status_code == 200
    assert response.json()["result"] is True

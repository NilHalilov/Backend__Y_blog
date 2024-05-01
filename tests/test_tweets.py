"""Модуль для тестов endpoint`ов связанных с моделью `Tweet`"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select, desc

from .conftest import test_db
from models.tweet import TweetModel
from models.user import UserModel
from models.followers import FollowerModel
from models.likes import LikeModel


@pytest.mark.asyncio(scope="session")
async def test_get_tweets(ac: AsyncClient, user_for_tweets):
    """Тест на получение ленты твитов тех, на кого подписан пользователь"""
    async with test_db.async_session() as session:
        test_follower = UserModel(
            name="Balrog", nickname="Box", email="BB@capcom.com", token="bal"
        )
        test_tweet = TweetModel(
            author_id=user_for_tweets.id,
            content="FooBar",
        )
        session.add(test_tweet)
        session.add(test_follower)
        await session.commit()

        test_relationship = FollowerModel(
            following_id=user_for_tweets.id,
            followers_id=test_follower.id,
        )
        session.add(test_relationship)
        await session.commit()

        response = await ac.get(f"/api/tweets/?api_key={test_follower.token}")

        assert response.status_code == 200
        assert len(response.json()["tweets"]) != 0


@pytest.mark.asyncio(scope="session")
async def test_post_tweet(ac: AsyncClient, user_for_tweets):
    """Тест на создание твита"""
    response = await ac.post(
        f"/api/tweets/?api_key={user_for_tweets.token}",
        json={
            "content": "Foo",
            "tweet_media_ids": [0],
        },
    )

    async with test_db.async_session() as session:
        query = select(TweetModel).order_by(desc(TweetModel.id)).limit(1)
        result = await session.scalar(query)

    assert response.status_code == 201
    assert response.json()["tweet_id"] == result.id


@pytest.mark.asyncio(scope="session")
async def test_delete_tweet(ac: AsyncClient, user_for_tweets):
    """Тест на удаление твита"""
    async with test_db.async_session() as session:
        test_tweet = TweetModel(
            author_id=user_for_tweets.id,
            content="FooBar",
        )
        session.add(test_tweet)
        await session.commit()

        query = select(TweetModel).order_by(desc(TweetModel.id)).limit(1)
        result = await session.scalar(query)
        assert result.id == test_tweet.id

        response = await ac.delete(
            f"/api/tweets/{result.id}/?api_key={user_for_tweets.token}"
        )
        result = await session.scalar(query)
        assert result is None or result.id != test_tweet.id

    assert response.status_code == 200
    assert response.json()["result"] is True


@pytest.mark.asyncio(scope="session")
async def test_like_tweet(ac: AsyncClient, user_for_tweets):
    """Тест на добавление лайка у твита"""
    async with test_db.async_session() as session:
        test_tweet = TweetModel(
            author_id=user_for_tweets.id,
            content="FooBar",
        )
        session.add(test_tweet)
        await session.commit()

    response = await ac.post(
        f"/api/tweets/{test_tweet.id}/likes/?api_key={user_for_tweets.token}"
    )

    async with test_db.async_session() as session:  # без новой сессии возвращает первоначальное кол-во лайков
        query = select(TweetModel).where(TweetModel.id == test_tweet.id)
        result = await session.scalar(query)

    assert response.status_code == 201
    assert response.json()["result"] is True
    assert result.likes_count == test_tweet.likes_count + 1


@pytest.mark.asyncio(scope="session")
async def test_delete_like(ac: AsyncClient, user_for_tweets):
    """Тест на удаление лайка у твита"""
    async with test_db.async_session() as session:
        test_tweet = TweetModel(
            author_id=user_for_tweets.id,
            content="FooBar",
            likes_count=2,
        )
        session.add(test_tweet)
        await session.flush()

        like_relationship = LikeModel(
            user_id=user_for_tweets.id,
            tweet_id=test_tweet.id,
        )
        session.add(like_relationship)
        await session.commit()

    response = await ac.delete(
        f"/api/tweets/{test_tweet.id}/likes/?api_key={user_for_tweets.token}"
    )

    async with test_db.async_session() as session:  # без новой сессии возвращает первоначальное кол-во лайков
        query = select(TweetModel).where(TweetModel.id == test_tweet.id)
        result = await session.scalar(query)

    assert response.status_code == 200
    assert response.json()["result"] is True
    assert result.likes_count == test_tweet.likes_count - 1

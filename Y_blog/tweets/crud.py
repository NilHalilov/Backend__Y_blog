"""Модуль для описания CRUD-действий модели `Tweet`"""

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from models.followers import FollowerModel
from models.likes import LikeModel
from models.tweet import TweetModel
from Y_blog.images import crud
from .schemas import TweetCreate, TweetInList


async def read_user_tweets_list(session: AsyncSession, user_id: int) -> dict | None:
    """
    Получение ленты твитов из БД от тех, на кого подписан пользователь.
    :param session объект сессии
    :param user_id: id пользователя
    """
    query = (
        select(TweetModel)
        .options(
            selectinload(TweetModel.images),
            joinedload(TweetModel.user),
            selectinload(TweetModel.all_likes).joinedload(LikeModel.user),
        )
        .filter(
            TweetModel.author_id.in_(
                select(FollowerModel.following_id).where(
                    FollowerModel.followers_id == user_id
                )
            )
        )
        .order_by(desc(TweetModel.likes_count))
    )
    result: Result = await session.execute(query)
    tweets = result.scalars().all()

    if tweets is not None:
        all_user_tweets = []

        for i_tweet in tweets:
            img_links = []
            tweet_likes = []
            author_info = {"id": i_tweet.user.id, "name": i_tweet.user.nickname}

            if i_tweet.all_likes is not None:
                for i_like in i_tweet.all_likes:
                    like_info = {
                        "user_id": i_like.user_id,
                        "name": i_like.user.nickname,
                    }
                    tweet_likes.append(like_info)

            if i_tweet.images is not None:
                for img_path in i_tweet.images:
                    img_links.append(img_path.filepath)

            all_user_tweets.append(
                TweetInList(
                    id=i_tweet.id,
                    content=i_tweet.content,
                    attachments=img_links,
                    author=author_info,
                    likes=tweet_likes,
                )
            )

        return {
            "result": True,
            "tweets": all_user_tweets,
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Tweets not found!"
    )


async def create_tweet(
    session: AsyncSession, new_tweet: TweetCreate, user_id: int
) -> dict:
    """
    Создание в БД новой записи твита
    :param session: объект сессии
    :param new_tweet: содержание нового твита
    :param user_id: id автора
    """
    tweet_info = new_tweet.model_dump()
    tweet = TweetModel(content=tweet_info["content"], author_id=user_id)
    session.add(tweet)
    await session.commit()
    await session.refresh(tweet)
    return {"result": True, "tweet_id": tweet.id}


async def delete_tweet(session: AsyncSession, user_id: int, tweet_id: int) -> dict:
    """
    Удаление в БД записи твита
    :param session: объект сессии
    :param user_id: id автора
    :param tweet_id: id удаляемого твита
    """
    query = (
        select(TweetModel)
        .options(selectinload(TweetModel.images))
        .where(TweetModel.id == tweet_id, TweetModel.author_id == user_id)
    )
    cur_tweet: TweetModel | None = await session.scalar(query)

    if cur_tweet is not None:
        if cur_tweet.images is not None:
            for img in cur_tweet.images:
                await crud.delete_img(img.filepath)

        await session.delete(cur_tweet)
        await session.commit()
        await session.close()
        return {
            "result": True,
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Tweet id=`{tweet_id}` not found for this user!",
    )


async def create_like(session: AsyncSession, user_id: int, tweet_id: int) -> dict:
    """
    Создание в БД отметки `лайк` для твита
    :param session: объект сессии
    :param user_id: id того кто ставит `лайк`
    :param tweet_id: id понравившегося твита
    """
    query_like = select(LikeModel).where(
        LikeModel.user_id == user_id, LikeModel.tweet_id == tweet_id
    )
    like_result: LikeModel | None = await session.scalar(query_like)

    if like_result is None:
        query_tweet = select(TweetModel).where(TweetModel.id == tweet_id)
        tweet_result: TweetModel | None = await session.scalar(query_tweet)

        if tweet_result is not None:
            tweet_result.likes_count = tweet_result.likes_count + 1
            await session.flush()  # для тестов
            new_like = LikeModel(user_id=user_id, tweet_id=tweet_id)
            session.add(new_like)
            await session.commit()

            return {
                "result": True,
            }

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tweet id=`{tweet_id}` not found !",
        )

    else:
        return {"result": False, "message": "You have already liked this tweet!"}


async def delete_like(session: AsyncSession, user_id: int, tweet_id: int) -> dict:
    """
    Удаление в БД отметки `лайк` для твита
    :param session: объект сессии
    :param user_id: id того кто убирает `лайк`
    :param tweet_id: id твита который разонравился
    """
    query_like = select(LikeModel).where(
        LikeModel.user_id == user_id, LikeModel.tweet_id == tweet_id
    )
    like_result: LikeModel | None = await session.scalar(query_like)

    if like_result is not None:
        query_tweet = select(TweetModel).where(TweetModel.id == tweet_id)
        tweet_result: TweetModel | None = await session.scalar(query_tweet)

        if tweet_result is not None:
            tweet_result.likes_count = tweet_result.likes_count - 1
            await session.delete(like_result)
            await session.commit()
            await session.close()
            return {
                "result": True,
            }

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tweet id=`{tweet_id}` not found for this user!",
        )

    else:
        return {"result": False, "message": "This tweet doesn't have your like!"}

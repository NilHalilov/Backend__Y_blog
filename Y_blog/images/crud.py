"""Модуль для описания CRUD-действий модели `Image`"""

import os

import aiofiles
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import MEDIA_PATH, AllOWED_IMG_EXTENSIONS
from models.media_img import ImageModel
from models.tweet import TweetModel


async def save_image(session: AsyncSession, user_image: UploadFile, token: str, tweet_id: int, user_id: int) -> dict:
    """
    Сохранение картинки.
    :param session объект сессии
    :param user_image: Загружаемая картинка пользователя
    :param token: api_key пользователя
    :param tweet_id: id твита
    :param user_id: id пользователя
    """
    query_tweet = select(TweetModel).where(TweetModel.id == tweet_id, TweetModel.author_id == user_id)
    img_tweet: TweetModel | None = await session.scalar(query_tweet)
    if img_tweet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This picture doesn't belong to specified tweet or user !",
        )

    if '.' not in user_image.filename or user_image.filename.rsplit('.', 1)[1] not in AllOWED_IMG_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Invalid extension of the uploaded image!",
        )

    try:
        contents = await user_image.read()
        if not os.path.exists(MEDIA_PATH + f"{token}"):
            os.chdir(MEDIA_PATH)
            os.mkdir(f"{token}")
        img_path = MEDIA_PATH + f"{token}/" + user_image.filename
        async with aiofiles.open(img_path, "wb") as file:
            await file.write(contents)

        img_info = ImageModel(
            tweet_id=tweet_id,
            filename=user_image.filename,
            filepath=img_path,
        )
        session.add(img_info)
        await session.commit()
        await session.refresh(img_info)
        return {
            "result": True,
            "media_id": img_info.id
        }

    except Exception as e:
        return {"ERROR": e.args}

    finally:
        await user_image.close()


async def delete_img(filepath: str):
    """
    Удаление картинки
    :param filepath: Путь до картинки
    """
    if os.path.exists(filepath):
        return os.remove(filepath)

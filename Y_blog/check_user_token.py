"""Модуль для создания декоратора, который проверяет пользовательский `api_key`"""

from functools import wraps

from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy import select

from models.user import UserModel


def token_required(func):

    @wraps(func)
    async def wrapper(*args, **kwargs):
        query = select(UserModel).where(UserModel.token == kwargs["api_key"])
        user: UserModel | None = await kwargs["session"].scalar(query)
        if user is not None:
            kwargs["user_id"] = user.id
            return await func(*args, **kwargs)

        return JSONResponse(
            content={
                "result": False,
                "message": "Wrong api-key token. This user does not exist.",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return wrapper

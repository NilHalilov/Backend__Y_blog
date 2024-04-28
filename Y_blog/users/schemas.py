"""Модуль для описания схем `User`"""

from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    name: Annotated[str, MinLen(2), MaxLen(30)]
    nickname: Annotated[str, MinLen(2), MaxLen(15)]
    email: EmailStr


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    token: str


class UserCreate(UserBase):
    pass

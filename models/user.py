"""Модуль для создания модели `User` в БД"""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:
    from .followers import FollowerModel
    from .likes import LikeModel
    from .tweet import TweetModel


class UserModel(Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(30))
    nickname: Mapped[str] = mapped_column(String(15), unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    token: Mapped[str] = mapped_column(unique=True)

    tweets: Mapped[list["TweetModel"]] = relationship(back_populates="user")
    following_list: Mapped[list["FollowerModel"]] = relationship(
        back_populates="follow_to", foreign_keys="FollowerModel.following_id"
    )
    follower_list: Mapped[list["FollowerModel"]] = relationship(
        back_populates="follow_by", foreign_keys="FollowerModel.followers_id"
    )
    users_who_liked: Mapped[list["LikeModel"]] = relationship(back_populates="user")

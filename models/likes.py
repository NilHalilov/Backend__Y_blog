"""Модуль для создания модели `Like` в БД"""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:
    from .tweet import TweetModel
    from .user import UserModel


class LikeModel(Base):
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "tweet_id",
            name="idx_user_tweet",
        ),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"))

    user: Mapped["UserModel"] = relationship(back_populates="users_who_liked")
    tweet: Mapped["TweetModel"] = relationship(back_populates="all_likes")

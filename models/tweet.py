"""Модуль для создания модели `Tweet` в БД"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .likes import LikeModel
    from .media_img import ImageModel
    from .user import UserModel


class TweetModel(Base):
    __tablename__ = "tweets"

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)
    likes_count: Mapped[int] = mapped_column(default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), default=datetime.now)

    user: Mapped["UserModel"] = relationship(back_populates="tweets")
    images: Mapped[list["ImageModel"]] = relationship(back_populates="tweet", cascade="all, delete")
    all_likes: Mapped[list["LikeModel"]] = relationship(back_populates="tweet", cascade="all, delete")

"""Модуль для создания модели `Image` в БД"""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:
    from .tweet import TweetModel


class ImageModel(Base):
    __tablename__ = "images"

    filename: Mapped[str]
    filepath: Mapped[str]
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"))

    tweet: Mapped["TweetModel"] = relationship(back_populates="images")

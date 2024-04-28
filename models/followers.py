"""Модуль для создания модели `Follower` в БД"""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:
    from .user import UserModel


class FollowerModel(Base):
    __tablename__ = "followers"
    __table_args__ = (
        UniqueConstraint(
            "following_id",
            "followers_id",
            name="idx_unique_following_followers"
        ),
    )

    following_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    followers_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    follow_to: Mapped["UserModel"] = relationship(back_populates="following_list", foreign_keys=[following_id])
    follow_by: Mapped["UserModel"] = relationship(back_populates="follower_list", foreign_keys=[followers_id])

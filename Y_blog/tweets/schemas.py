"""Модуль для описания схем `Tweet`"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TweetBase(BaseModel):
    content: str


class Tweet(TweetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    likes_count: int
    created_at: datetime


class TweetCreate(TweetBase):
    tweet_media_ids: list[int] | None


class TweetInList(TweetBase):
    id: int
    attachments: list
    author: dict
    likes: list

"""Модуль для описания схем `Image`"""

from pydantic import BaseModel, ConfigDict


class ImageBase(BaseModel):
    tweet_id: int


class Image(ImageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    filepath: str


class ImageSave(ImageBase):
    pass

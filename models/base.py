"""Модуль для создания: базового класса для моделей БД, асинхронного подключения к БД"""

from asyncio import current_task

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
)

from config import settings_db


class Base(DeclarativeBase):
    """Базовый класс для моделей БД"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)

    # @declared_attr.directive
    # def __tablename__(cls) -> str:
    #     return f"Y_blog_{cls.__name__.lower()}"


class DBConnect:
    """Класс для создания асинхронного подключения к БД"""

    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.async_session = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.async_session,
            scopefunc=current_task,
        )
        return session

    async def session_dependency(self):
        """Метод для создания сессии для каждого запроса"""
        session = self.get_scoped_session()
        yield session
        await session.remove()


y_blog_db = DBConnect(url=settings_db.db_url, echo=settings_db.db_echo)

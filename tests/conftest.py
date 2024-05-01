import asyncio
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from config import TEST_DB_PATH
from main import app
from models.base import Base, DBConnect, y_blog_db
from models.user import UserModel


test_db = DBConnect(url=TEST_DB_PATH, echo=False)
app.dependency_overrides[y_blog_db.session_dependency] = test_db.session_dependency


@pytest_asyncio.fixture(autouse=True, scope="session")
async def prepare_db():
    async with test_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000/"
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="session")
async def user_for_tweets():
    async with test_db.async_session() as session:
        test_user: UserModel = UserModel(
            name="Vega", nickname="Masher", email="V@capcom.com", token="vvv"
        )

        session.add(test_user)
        await session.commit()

    return test_user

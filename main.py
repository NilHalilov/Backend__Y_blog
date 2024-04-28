from contextlib import asynccontextmanager

# import uvicorn
from fastapi import FastAPI

from models import Base, y_blog_db
from Y_blog.images.views import router as medias_router
from Y_blog.tweets.views import router as tweets_router
from Y_blog.users.views import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with y_blog_db.engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(users_router)
app.include_router(tweets_router)
app.include_router(medias_router)


# if __name__ == "__main__":
#     uvicorn.run("main:app", reload=True)

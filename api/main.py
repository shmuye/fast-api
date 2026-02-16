from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.database import database
from api.router.post import router as post_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI()
app.include_router(post_router)





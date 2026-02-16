from fastapi import FastAPI

from api.router.post import router as post_router

app = FastAPI()

app.include_router(post_router)





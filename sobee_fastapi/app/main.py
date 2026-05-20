from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import avatar, lifecycle, recommend
from app.db.connection import close_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_pool()


app = FastAPI(
    title="Sobee FastAPI - B조",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(avatar.router, prefix="/api/avatar", tags=["avatar"])
app.include_router(recommend.router, prefix="/api/recommend", tags=["recommend"])
app.include_router(lifecycle.router, prefix="/api/lifecycle", tags=["lifecycle"])


@app.get("/health")
def health_check():
    return {"status": "ok"}

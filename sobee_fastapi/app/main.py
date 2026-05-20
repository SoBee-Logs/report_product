from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import avatar, recommend, lifecycle, report 
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(avatar.router, prefix="/api/avatar", tags=["avatar"])
app.include_router(recommend.router, prefix="/api/recommend", tags=["recommend"])
app.include_router(lifecycle.router, prefix="/api/lifecycle", tags=["lifecycle"])
app.include_router(report.router, tags=["report"])  


@app.get("/health")
def health_check():
    return {"status": "ok"}

from fastapi import FastAPI
from app.api import avatar, recommend, lifecycle, vlm_router
from app.core.config import settings

app = FastAPI(
    title="Sobee FastAPI - B조",
    version="0.1.0"
)

app.include_router(avatar.router, prefix="/api/avatar", tags=["avatar"])
app.include_router(recommend.router, prefix="/api/recommend", tags=["recommend"])
app.include_router(lifecycle.router, prefix="/api/lifecycle", tags=["lifecycle"])
app.include_router(vlm_router.router, prefix="/api/vlm", tags=["vlm"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
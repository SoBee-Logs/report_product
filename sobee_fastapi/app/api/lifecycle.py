from fastapi import APIRouter
from app.models.schemas import LifecycleRequest, LifecycleResponse
from app.services.lifecycle_service import predict_lifecycle

router = APIRouter()

@router.post("", response_model=LifecycleResponse)
async def get_lifecycle(request: LifecycleRequest):
    return await predict_lifecycle(request)
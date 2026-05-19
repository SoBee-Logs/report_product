from fastapi import APIRouter
from app.models.schemas import AvatarRequest, AvatarResponse
from app.services.avatar_service import generate_avatar

router = APIRouter()

@router.post("", response_model=AvatarResponse)
async def create_avatar(request: AvatarRequest):
    return await generate_avatar(request)
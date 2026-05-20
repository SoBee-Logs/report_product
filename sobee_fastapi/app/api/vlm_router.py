from fastapi import APIRouter, UploadFile, File
from app.models.schemas import VLMResponse
from app.services.vlm_service import analyze_image

router = APIRouter()


@router.post("/analyze", response_model=VLMResponse)
async def analyze(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result = await analyze_image(file.filename, image_bytes)
    return result

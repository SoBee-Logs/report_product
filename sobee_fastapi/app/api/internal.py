from fastapi import APIRouter
from app.models.schemas import (
    SyncRequest, SyncResponse,
    MappingRequest, MappingResponse,
    PersonaGenerateRequest, AvatarResponse,
    DiaryGenerateRequest, DiaryGenerateResponse,
    ParseSearchRequest, ParseSearchResponse,
)
from app.services.sync_service import sync_transactions
from app.services.mapping_service import run_mapping
from app.services.avatar_service import _generate_and_save_avatar
from app.services.diary_service import generate_diary
from app.services.search_parse_service import parse_search_query

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/transactions/sync", response_model=SyncResponse)
async def transactions_sync(request: SyncRequest):
    result = await sync_transactions(request.user_id)
    return SyncResponse(message=result.get("message", "sync complete"))


@router.post("/mapping/run", response_model=MappingResponse)
async def mapping_run(request: MappingRequest):
    result = await run_mapping(request.user_id)
    return MappingResponse(message=result.get("message", "mapping complete"))


@router.post("/persona/generate", response_model=AvatarResponse)
async def persona_generate(request: PersonaGenerateRequest):
    return await _generate_and_save_avatar(request.user_id, request.start_date, request.end_date)


@router.post("/diary/generate", response_model=DiaryGenerateResponse)
async def diary_generate(request: DiaryGenerateRequest):
    result = await generate_diary(request.user_id)
    return DiaryGenerateResponse(message=result.get("message", "diary generated"))


@router.post("/parse-search", response_model=ParseSearchResponse)
async def parse_search(request: ParseSearchRequest):
    result = await parse_search_query(request.query)
    return ParseSearchResponse(**result)

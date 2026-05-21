from fastapi import APIRouter, Query
from app.services.report_service import get_transaction_report
from app.services.ai_insight_service import get_ai_insight
from app.models.schemas import AiInsightResponse

router = APIRouter()

@router.get("/report/mydata/transaction")
def get_transaction(user_id: int = Query(...)):
    return get_transaction_report(user_id)

@router.get("/report/ai-insight", response_model=AiInsightResponse)
async def ai_insight(user_id: int = Query(...)):
    return await get_ai_insight(user_id)
from fastapi import APIRouter, Query
from app.services.report_service import get_transaction_report
from app.services.ai_insight_service import get_ai_insight
from app.services.lifecycle_service import get_lifecycle
from app.services.question_service import generate_recommend_questions
from app.models.schemas import AiInsightResponse

router = APIRouter()

@router.get("/report/mydata/transaction")
def get_transaction(user_id: int = Query(...)):
    return get_transaction_report(user_id)

@router.get("/report/ai-insight", response_model=AiInsightResponse)
async def ai_insight(user_id: int = Query(...)):
    return await get_ai_insight(user_id)

@router.get("/report/recommend-questions")
async def recommend_questions(user_id: int = Query(...)):
    report = get_transaction_report(user_id)
    lifecycle = await get_lifecycle(user_id)

    category_price = report.get("category_price", {})
    lifecycle_label = lifecycle.life_stage_code

    questions = await generate_recommend_questions(category_price, lifecycle_label)
    return {"questions": questions}
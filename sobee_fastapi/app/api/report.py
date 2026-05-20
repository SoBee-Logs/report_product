from fastapi import APIRouter, Query
from app.services.report_service import get_transaction_report

router = APIRouter()

@router.get("/report/mydata/transaction")
def get_transaction(user_id: int = Query(...)):
    return get_transaction_report(user_id)
from app.models.schemas import LifecycleRequest, LifecycleResponse
from ml.lifecycle_model import lifecycle_model
from sqlalchemy import create_engine, text
from app.core.config import settings
import pandas as pd

engine = create_engine(
    f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# 임시 매핑 테이블 (Mock 데이터용)
USER_ID_MAP = {
    1: "user_haeun",
    2: "user_soyoung",
    3: "user_seokbin",
}

async def predict_lifecycle(request: LifecycleRequest) -> LifecycleResponse:

    # int → DB 문자열 변환
    user_id_str = USER_ID_MAP.get(request.user_id, f"user_{request.user_id}")

    # DB에서 트랜잭션 가져오기
    df_tx = pd.read_sql(text("""
        SELECT payment_category,
               payment_out
        FROM transactions
        WHERE user_id = :user_id
        AND payment_out > 0
    """), engine, params={"user_id": user_id_str})

    # DB에서 나이/성별 가져오기
    df_user = pd.read_sql(text("""
        SELECT age, gender
        FROM users
        WHERE user_id = :user_id
    """), engine, params={"user_id": user_id_str})

    # users 데이터 파싱 (없으면 request 값 사용)
    if not df_user.empty:
        age = int(df_user['age'].iloc[0])
        gender = 1 if df_user['gender'].iloc[0] == 'm' else 2
    else:
        age = request.age
        gender = 0

    # 트랜잭션 없으면 fallback
    if df_tx.empty:
        return LifecycleResponse(
            lifecycle_stage="사회초년생",
            description="트랜잭션 데이터가 없습니다."
        )

    # KNN 예측
    result = lifecycle_model.predict_from_transactions(
        user_transactions=df_tx.to_dict('records'),
        age=age,
        gender=gender
    )

    # 카테고리별 지출 TOP 3 분석
    category_summary = df_tx.groupby('payment_category')['payment_out'].sum()
    top3 = category_summary.nlargest(3)
    top3_str = ", ".join([f"{cat}({int(amt):,}원)" for cat, amt in top3.items()])

    # 설명 생성
    description = (
        f"주요 소비가 {top3_str}에 집중되어 있어 "
        f"'{result['lifecycle_label']}' 패턴으로 분류되었습니다. "
        f"(확신도 {result['confidence']*100:.0f}%)"
    )

    return LifecycleResponse(
        lifecycle_stage=result["lifecycle_label"],
        description=description
    )
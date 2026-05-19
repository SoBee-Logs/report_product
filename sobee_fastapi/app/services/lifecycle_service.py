from app.models.schemas import LifecycleRequest, LifecycleResponse

async def predict_lifecycle(request: LifecycleRequest) -> LifecycleResponse:
    # TODO: KNN 모델로 생애주기 예측
    return LifecycleResponse(
        lifecycle_stage="사회초년생",
        description="20대 초반, 외식/카페 지출 비중이 높은 소비 패턴입니다."
    )
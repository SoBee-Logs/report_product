from app.models.schemas import AvatarRequest, AvatarResponse

async def generate_avatar(request: AvatarRequest) -> AvatarResponse:
    # TODO: LLM 프롬프트로 아바타 생성
    return AvatarResponse(
        avatar_title="야행성 도시 탐험가",
        avatar_description="밤에 활동이 많고 외식을 즐기는 소비 패턴을 가진 사용자입니다."
    )

from pydantic import BaseModel
from typing import Optional

# 아바타
class AvatarRequest(BaseModel):
    user_id: int

class AvatarResponse(BaseModel):
    avatar_title: str
    avatar_description: str
    avatar_image: str  # S3 URL, 16:9 PNG, character + background combined

# 금융상품 추천
class RecommendRequest(BaseModel):
    user_id: int
    query: str
    lifecycle_stage: Optional[str] = None

class RecommendResponse(BaseModel):
    product_id: int
    product_name: str
    reason: str

# 생애주기
class LifecycleRequest(BaseModel):
    user_id: int
    age: int
    monthly_spend: float
    top_category: str

class LifecycleResponse(BaseModel):
    lifecycle_stage: str
    description: str
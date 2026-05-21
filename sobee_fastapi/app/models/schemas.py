from pydantic import BaseModel
from typing import Optional, List

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
    user_id: int = 1
    age: int
    monthly_spend: float
    top_category: str

class LifecycleResponse(BaseModel):
    lifecycle_stage: str
    description: str

# AI 상품 추천
class AiInsightContent(BaseModel):
    header: Optional[str] = None
    middle: Optional[str] = None
    small: Optional[str] = None
    url: Optional[str] = None

class AiInsightItem(BaseModel):
    product_name: str
    product_company: str
    product_img_url: Optional[str] = None
    product_type: str  # 'card' | 'savings'
    content: Optional[AiInsightContent] = None

class AiInsightResponse(BaseModel):
    recommned: List[AiInsightItem]  # 스펙 오타 유지
    message: Optional[str] = None
from pydantic import BaseModel
from typing import Optional, Literal

# 아바타
class AvatarRequest(BaseModel):
    user_id: int
    transaction_summary: str

class AvatarResponse(BaseModel):
    avatar_title: str
    avatar_description: str

# 금융상품 추천
class RecommendRequest(BaseModel):
    user_id: int
    query: str
    lifecycle_stage: Optional[str] = None

class RecommendResponse(BaseModel):
    product_id: int
    product_name: str
    reason: str

# VLM 이미지 분석
class GPSInfo(BaseModel):
    latitude: float
    longitude: float

class VLMResponse(BaseModel):
    file: str
    taken_at: Optional[str] = None
    gps: Optional[GPSInfo] = None
    address: Optional[str] = None
    category: Optional[str] = None
    item_name: Optional[str] = None
    price: Optional[float] = None
    location_type: Optional[str] = None
    store_name: Optional[str] = None
    description: Optional[str] = None
    confidence: Optional[Literal["high", "medium", "low"]] = None
    error: Optional[str] = None

# 생애주기
class LifecycleRequest(BaseModel):
    user_id: int
    age: int
    monthly_spend: float
    top_category: str

class LifecycleResponse(BaseModel):
    lifecycle_stage: str
    description: str
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
    life_stage_code: Optional[str] = None

class RecommendResponse(BaseModel):
    product_id: int
    product_name: str
    reason: str

# LifecycleRequest
class LifecycleRequest(BaseModel):
    user_id: int                           # 필수

# LifecycleResponse
class LifecycleResponse(BaseModel):
    life_stage_code: str
    description: str

# 내부 파이프라인
class SyncRequest(BaseModel):
    user_id: int
    days: Optional[int] = None  # None → daily default (3일), 30 → 최초 가입 시

class SyncResponse(BaseModel):
    message: str

class MappingRequest(BaseModel):
    user_id: int

class MappingResponse(BaseModel):
    message: str

class PersonaGenerateRequest(BaseModel):
    user_id: int
    start_date: Optional[str] = None  # 없으면 지난주 월~일 자동 적용
    end_date: Optional[str] = None

class RegisterAccountRequest(BaseModel):
    user_id: int
    business_type: str   # "BK" | "CD"
    org_code: str        # 기관코드 e.g. "0020"
    login_id: str
    login_pw: str

class RegisterAccountResponse(BaseModel):
    user_id: int
    business_type: str
    org_code: str
    message: str

class DiaryGenerateRequest(BaseModel):
    user_id: int

class DiaryGenerateResponse(BaseModel):
    message: str

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
    reason: Optional[str] = None
    content: Optional[AiInsightContent] = None

class AiInsightResponse(BaseModel):
    recommned: List[AiInsightItem]  # 스펙 오타 유지
    message: Optional[str] = None

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

class SyncResponse(BaseModel):
    message: str

class MappingRequest(BaseModel):
    user_id: int

class MappingResponse(BaseModel):
    message: str

class PersonaGenerateRequest(BaseModel):
    user_id: int
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD

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

# 검색 AI 분석 텍스트
class SearchProduct(BaseModel):
    product_name: str
    product_type: str  # card | savings | insurance
    header: Optional[str] = None

class AiSearchTextRequest(BaseModel):
    query: str
    user_id: int
    products: List[SearchProduct]

class AiSearchTextResponse(BaseModel):
    ai_text: str

# 시멘틱 검색 쿼리 파싱
class ParseSearchRequest(BaseModel):
    query: str

class ParseSearchResponse(BaseModel):
    product_types: List[str]
    category: Optional[str] = None
    keywords: List[str]
    ai_text: str

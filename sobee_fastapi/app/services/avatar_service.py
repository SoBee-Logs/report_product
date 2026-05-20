import base64
import io
import json
from collections import defaultdict
from datetime import datetime

import boto3
from openai import AsyncOpenAI
from PIL import Image
from fastapi import HTTPException

from app.core.config import settings
from app.db.transaction_repository import get_recent_transactions
from app.models.schemas import AvatarRequest, AvatarResponse

_AVATAR_PROMPT = """
A single wide illustration in Pixar-style soft 3D clay render. Overall canvas: 16:9 landscape (wide horizontal).

The scene contains TWO elements seamlessly combined:

1. CHARACTER (occupies roughly the left 1/3 of the canvas in a 3:4 portrait area):
A cute chubby bee-inspired mascot character in high-quality 3D render style, based on a simple flat illustration design.
The character has a rounded blob-shaped body with a soft matte clay texture, pastel blue upper body, and a yellow-and-blue striped belly.
Small translucent wings on both sides, short blue antennae on top of the head, tiny black dot eyes, and a warm smiling face.
Rounded yellow feet and tiny stubby arms.
Pixar-style 3D character design, clean topology, soft global illumination, subtle ambient occlusion, smooth shading, toy-like proportions, highly appealing mascot design.
Front-facing full body pose. The ENTIRE character from the tip of the antennae to the bottom of the feet must be fully visible — do not cut off any part of the body.
Minimal but expressive facial features, soft lighting, modern mobile app mascot aesthetic, polished 3D animation studio quality.

Consumer persona traits applied to the character:
- Lifestyle: {lifestyle}
- Consumption habits: {consumption_habit}
- Active time pattern: {time_pattern}
- Personality vibe: {personality}

Based on these traits, naturally generate on the character:
- fitting fashion and accessories
- matching facial expression and pose
- suitable props and items

2. BACKGROUND (fills the remaining right 2/3 and the full scene behind the character):
A richly detailed environment that reflects the persona's lifestyle and active time pattern.
Same Pixar 3D clay render art style and color palette as the character — fully cohesive visual language.
Cozy, vibrant, and emotionally expressive setting. Soft pastel colors, warm lighting.

The character and background must feel like one seamlessly integrated scene — not a composited cutout.
Final result: a premium wide banner card for a mobile finance app, cute and emotionally appealing.
"""

_ANALYSIS_PROMPT = """
다음은 사용자의 최근 결제 내역 요약입니다:
{summary}

이 소비 데이터를 분석하여 아래 JSON 형식으로만 응답하세요 (다른 설명 없이):
{{
    "title": "아바타 타이틀 (예: '야행성 도시 탐험가'처럼 2-4단어의 감성적 한국어 별명)",
    "description": "이 페르소나가 도출된 이유를 소비 데이터 기반으로 2문장 이내 한국어로 서술. 예시 없이 실제 데이터 근거만.",
    "lifestyle": "Lifestyle description in English (2-3 sentences)",
    "consumption_habit": "Consumption habit description in English (2-3 sentences)",
    "time_pattern": "Active time pattern description in English (1-2 sentences)",
    "personality": "Personality vibe description in English (1-2 sentences)"
}}
"""


def _build_transaction_summary(transactions: list[dict]) -> str:
    category_spend: dict[str, int] = defaultdict(int)
    time_buckets = {"morning (6-12)": 0, "afternoon (12-18)": 0, "evening (18-22)": 0, "night (22-6)": 0}
    place_count: dict[str, int] = defaultdict(int)

    for t in transactions:
        category = (t.get("payment_category") or "기타").strip() or "기타"
        amount = int(t.get("payment_out") or 0)
        category_spend[category] += amount

        time_str = str(t.get("payment_time") or "").zfill(6)
        if len(time_str) >= 2:
            hour = int(time_str[:2])
            if 6 <= hour < 12:
                time_buckets["morning (6-12)"] += 1
            elif 12 <= hour < 18:
                time_buckets["afternoon (12-18)"] += 1
            elif 18 <= hour < 22:
                time_buckets["evening (18-22)"] += 1
            else:
                time_buckets["night (22-6)"] += 1

        place = (t.get("payment_place") or "").strip()
        if place:
            place_count[place] += 1

    top_categories = sorted(category_spend.items(), key=lambda x: x[1], reverse=True)[:5]
    dominant_time = max(time_buckets, key=lambda k: time_buckets[k])
    top_places = sorted(place_count.items(), key=lambda x: x[1], reverse=True)[:3]

    return "\n".join([
        f"총 결제 건수: {len(transactions)}건",
        f"카테고리별 지출 (상위 5): " + ", ".join(f"{c} {a:,}원" for c, a in top_categories),
        f"주 활동 시간대: {dominant_time}",
        f"자주 방문 가맹점: " + ", ".join(p for p, _ in top_places),
    ])


async def _analyze_persona(summary: str) -> dict:
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    prompt = _ANALYSIS_PROMPT.format(summary=summary)

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


def _crop_to_ratio(image_bytes: bytes, width_ratio: int, height_ratio: int) -> bytes:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    target = width_ratio / height_ratio
    current = w / h

    if current > target:
        new_w = int(h * target)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    elif current < target:
        new_h = int(w / target)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


async def _generate_image(prompt: str) -> bytes:
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    response = await client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1536x1024",  # 3:2 landscape, 16:9로 크롭
        quality="high",
        n=1,
    )

    image_bytes = base64.b64decode(response.data[0].b64_json)
    return _crop_to_ratio(image_bytes, width_ratio=16, height_ratio=9)


def _upload_to_s3(image_bytes: bytes, user_id: int) -> str:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    key = f"avatars/{user_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    s3.put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=key,
        Body=image_bytes,
        ContentType="image/png",
    )
    return f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"


async def generate_avatar(request: AvatarRequest) -> AvatarResponse:
    transactions = await get_recent_transactions(request.user_id)
    if not transactions:
        raise HTTPException(status_code=404, detail=f"No transactions found for user_id: {request.user_id}")

    summary = _build_transaction_summary(transactions)
    analysis = await _analyze_persona(summary)

    prompt = _AVATAR_PROMPT.format(
        lifestyle=analysis["lifestyle"],
        consumption_habit=analysis["consumption_habit"],
        time_pattern=analysis["time_pattern"],
        personality=analysis["personality"],
    )

    image_bytes = await _generate_image(prompt)
    avatar_image_url = _upload_to_s3(image_bytes, request.user_id)

    return AvatarResponse(
        avatar_title=analysis["title"],
        avatar_description=analysis["description"],
        avatar_image=avatar_image_url,
    )

import io
import json
import urllib.request

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from google import genai
from google.genai import types
from fastapi import HTTPException

from app.core.config import settings


EXTRACTION_PROMPT = """이 사진을 분석해서 소비 정보를 추출해줘.

반드시 아래 JSON 형식으로만 응답하고, 다른 텍스트는 절대 포함하지 마.

{
    "category": "요식업 | 카페/디저트 | 유통/마트 | 편의점 | 교통 | 문화/레져 | 의류/잡화 | 보건/의료 | 기타",
    "item_name": "품목 또는 메뉴 이름",
    "price": 금액(숫자만, 원 단위. 알 수 없으면 한국 일반 시세로 반드시 추정),
    "location_type": "장소 유형 (식당, 카페, 마트, 편의점, 온라인 등)",
    "store_name": "가게 이름 (알 수 없으면 null)",
    "description": "사진에 대한 한 줄 설명",
    "confidence": "high | medium | low"
}

중요 규칙:
- category는 반드시 하나만 선택해
- 영수증이면 금액을 정확히 읽어줘
- 음식 사진이면 한국 일반 시세 기준으로 가격을 반드시 추정해줘
- JSON만 출력해. 마크다운 코드블록도 쓰지 마"""


def _get_client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY가 설정되지 않았습니다.")
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def _convert_gps_to_decimal(coords, ref) -> float | None:
    if not coords or not ref:
        return None
    try:
        degrees = float(coords[0])
        minutes = float(coords[1])
        seconds = float(coords[2])
        decimal = degrees + minutes / 60 + seconds / 3600
        if ref in ("S", "W"):
            decimal = -decimal
        return round(decimal, 6)
    except (TypeError, IndexError, ValueError):
        return None


def extract_exif(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes))
        exif_data = img._getexif()
    except Exception:
        return {"datetime": None, "gps": None}

    if not exif_data:
        return {"datetime": None, "gps": None}

    result = {"datetime": None, "gps": None}

    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, tag_id)
        if tag_name == "DateTimeOriginal":
            result["datetime"] = value.replace(":", "-", 2)
            break

    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, tag_id)
        if tag_name == "GPSInfo":
            gps_info = {GPSTAGS.get(k, k): v for k, v in value.items()}
            lat = _convert_gps_to_decimal(gps_info.get("GPSLatitude"), gps_info.get("GPSLatitudeRef"))
            lon = _convert_gps_to_decimal(gps_info.get("GPSLongitude"), gps_info.get("GPSLongitudeRef"))
            if lat is not None and lon is not None:
                result["gps"] = {"latitude": lat, "longitude": lon}
            break

    return result


def reverse_geocode(lat: float, lon: float) -> str | None:
    try:
        url = (
            f"https://nominatim.openstreetmap.org/reverse?"
            f"lat={lat}&lon={lon}&format=json&accept-language=ko"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "SoBee-VLM/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return data.get("display_name")
    except Exception:
        return None


def _get_mime_type(filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1]
    return {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(ext, "image/jpeg")


def _analyze_with_gemini(client: genai.Client, image_bytes: bytes, mime_type: str) -> dict:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part(inline_data=types.Blob(mime_type=mime_type, data=image_bytes)),
            EXTRACTION_PROMPT,
        ],
        config=types.GenerateContentConfig(temperature=0.1),
    )

    result_text = response.text.strip()
    if result_text.startswith("```"):
        result_text = result_text.split("\n", 1)[1].rsplit("```", 1)[0]

    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        return {"error": "JSON 파싱 실패", "raw_response": result_text}


async def analyze_image(filename: str, image_bytes: bytes) -> dict:
    client = _get_client()

    exif = extract_exif(image_bytes)

    address = None
    if exif["gps"]:
        address = reverse_geocode(exif["gps"]["latitude"], exif["gps"]["longitude"])

    mime_type = _get_mime_type(filename)
    vlm_result = _analyze_with_gemini(client, image_bytes, mime_type)

    return {
        "file": filename,
        "taken_at": exif["datetime"],
        "gps": exif["gps"],
        "address": address,
        **vlm_result,
    }

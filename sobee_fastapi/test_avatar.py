import base64
import subprocess
import sys
from pathlib import Path

import httpx

USER_ID = 1
OUTPUT_DIR = Path("test_output")
OUTPUT_DIR.mkdir(exist_ok=True)

print(f"아바타 생성 중... (user_id: {USER_ID})")

response = httpx.post(
    "http://localhost:8000/api/avatar",
    json={"user_id": USER_ID},
    timeout=120,
)

if response.status_code != 200:
    print(f"오류: {response.status_code}")
    print(response.text)
    sys.exit(1)

data = response.json()
print(f"\n타이틀: {data['avatar_title']}")
print(f"설명:   {data['avatar_description']}")

avatar_path = OUTPUT_DIR / "avatar.png"   # 16:9, 캐릭터+배경 통합
persona_path = OUTPUT_DIR / "persona.txt"

avatar_path.write_bytes(base64.b64decode(data["avatar_image"]))
persona_path.write_text(
    f"[아바타 타이틀]\n{data['avatar_title']}\n\n[페르소나 선정 이유]\n{data['avatar_description']}",
    encoding="utf-8",
)

print(f"\n아바타 이미지 (16:9): {avatar_path}")
print(f"페르소나 설명:         {persona_path}")

subprocess.run(["open", str(avatar_path), str(persona_path)])

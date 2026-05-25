# RDS 연결 가이드 (로컬 개발용)

> 로컬 맥북에서 개발/테스트할 때 팀 공용 DB(RDS)에 접속하는 방법입니다.

---

## 왜 이렇게 해야 하나요?

우리 DB(RDS)는 보안을 위해 인터넷에서 직접 접근할 수 없는 **프라이빗 네트워크** 안에 있습니다.
쉽게 말하면, DB가 자물쇠로 잠긴 방 안에 있고 우리는 밖에 있는 상황입니다.

이 자물쇠를 열 수 있는 열쇠가 **Bastion 서버**입니다.
Bastion은 외부에서 접근할 수 있는 중간 서버로, 이걸 통해 DB 방 안으로 들어갈 수 있습니다.

```
내 맥북 → Bastion 서버 → DB(RDS)
```

이 통로를 **SSH 터널**이라고 부릅니다.

---

## 준비물

- `sobee-prd-key.pem` 파일 (팀에서 공유받은 키 파일)
- 터미널 2개

---

## 순서

### Step 1. pem 키 권한 설정 (처음 한 번만)

```bash
chmod 400 /path/to/sobee-prd-key.pem
```

> `/path/to/` 부분을 실제 pem 파일 경로로 바꿔주세요.
> 예: `chmod 400 ~/Downloads/sobee-prd-key.pem`

---

### Step 2. SSH 터널 열기 (터미널 1)

```bash
ssh -i sobee-prd-key.pem -L 3307:sobee-prd-db-mysql.cboqcmk4y5y9.ap-northeast-2.rds.amazonaws.com:3306 ubuntu@13.124.37.8 -N
```

실행하면 아무것도 안 뜨고 멈춰 있는 것처럼 보입니다. **이게 정상입니다.**
이 터미널은 개발하는 동안 계속 열어둬야 합니다.

> 처음 실행하면 아래 문구가 나올 수 있습니다. `yes` 입력하세요.
> ```
> Are you sure you want to continue connecting (yes/no)?
> ```

---

### Step 3. .env 수정 (터미널 2)

`sobee_fastapi/.env` 파일에서 아래 두 줄을 수정합니다.

```
DB_HOST=127.0.0.1
DB_PORT=3307
```

> 나머지 값(DB_USER, DB_PASSWORD, DB_NAME 등)은 그대로 두세요.

---

### Step 4. FastAPI 실행

```bash
cd sobee_fastapi
uvicorn app.main:app --reload
```

브라우저에서 `http://localhost:8000/docs` 접속하면 API 테스트 가능합니다.

---

## 작업 끝나면 꼭 해주세요

### .env 원래대로 되돌리기

```
DB_HOST=sobee-prd-db-mysql.cboqcmk4y5y9.ap-northeast-2.rds.amazonaws.com
DB_PORT=3306
```

> EC2 서버에 배포할 때는 이 값을 써야 합니다.
> 127.0.0.1로 남겨두면 배포 후 DB 연결이 안 됩니다.

### 터미널 1 종료

터널 열어둔 터미널에서 `Ctrl + C` 누르면 됩니다.

---

## 자주 겪는 문제

**Q. SSH 터널 명령어 실행했더니 "Address already in use" 에러가 나요.**

이전에 열었던 터널이 아직 살아 있는 상태입니다.

```bash
lsof -ti :3307 | xargs kill -9
```

위 명령어로 종료하고 다시 실행하세요.

---

**Q. FastAPI 실행했더니 DB 연결 에러가 나요.**

터널이 열려있는지 확인하세요. 터미널 1이 실행 중인지 확인 후, .env의 `DB_HOST=127.0.0.1`, `DB_PORT=3307`로 되어 있는지 확인하세요.

---

**Q. `chmod 400` 안 하면 어떻게 되나요?**

아래 에러가 나고 접속이 거부됩니다.

```
WARNING: UNPROTECTED PRIVATE KEY FILE!
Permissions for 'sobee-prd-key.pem' are too open.
```

---

## 정리

| 상황 | DB_HOST | DB_PORT |
|------|---------|---------|
| 로컬에서 개발/테스트 | `127.0.0.1` | `3307` |
| EC2 서버에 배포 | RDS 엔드포인트 | `3306` |

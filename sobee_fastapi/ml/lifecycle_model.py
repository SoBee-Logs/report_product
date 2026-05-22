import pickle
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from lightgbm import LGBMClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from dotenv import load_dotenv
import os

# ─────────────────────────────────────────
# 환경변수
# ─────────────────────────────────────────
load_dotenv()

DB_HOST     = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT     = os.getenv("DB_PORT", "3306")
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME     = os.getenv("DB_NAME", "wonpick")
CSV_PATH    = os.getenv("CSV_PATH", "data/wooricard.csv")
MODEL_PATH  = os.getenv("MODEL_PATH", "ml/model.pkl")

# ─────────────────────────────────────────
# 피처 컬럼
# 나이/성별 + 소비 피처 조합
# → 우리카드가 LIFE_STAGE를 붙인 기준과 동일하게 맞춤
# ─────────────────────────────────────────
FEATURE_COLS = [
    'AGE',          # 나이 (5살 단위: 20,25,30...)
    'SEX_CD',       # 성별 (1:남, 2:여)
    'TOT_USE_AM',   # 총이용금액 (월평균)
    'CRDSL_USE_AM', # 신용카드 이용금액
    'CNF_USE_AM',   # 체크카드 이용금액
    'FSBZ_AM',      # 요식업 (카페+음식점 전체)
    'TRVLEC_AM',    # 여행/레져/문화
    'DIST_AM',      # 유통 (편의점/마트/온라인쇼핑)
    'CLOTHGDS_AM',  # 의류/신변잡화
    'AUTO_AM',      # 자동차/연료/정비
    'INTERIOR_AM',  # 가전/가구/주방용품
    'INSUHOS_AM',   # 보험/병원 (대분류)
    'OFFEDU_AM',    # 사무통신/서적/학원 (대분류)
    'PLSANIT_AM',   # 보건위생
    'HOS_AM',       # 의료기관 (중분류)
    'ACDM_AM',      # 학원 (중분류)
    'HOTEL_AM',     # 숙박업
    'TRVL_AM',      # 여행업
    'RESTRNT_AM',   # 일반/휴게음식
    'FUEL_AM',      # 연료판매
    'CULTURE_AM',   # 문화/취미
    'LEISURE_S_AM', # 레져업소
    'BOOK_AM',      # 서적/문구
]

# ─────────────────────────────────────────
# 생애주기 한글 매핑
# ─────────────────────────────────────────
LIFECYCLE_KO = {
    'TEEN':       '십대',
    'UNI':        '대학생',
    'NEW_JOB':    '사회초년생',
    'NEW_WED':    '신혼',
    'CHILD_BABY': '자녀영유아',
    'CHILD_TEEN': '자녀의무교육',
    'CHILD_UNI':  '자녀대학생',
    'GOLLIFE':    '중년기타',
    'SECLIFE':    '2nd Life',
    'RETIR':      '은퇴',
}

# ─────────────────────────────────────────
# 가맹점명 → 우리카드 대분류 카테고리 통일
# ─────────────────────────────────────────
RAW_TO_UNIFIED = {
    # 요식업
    '커피전문점':                   '요식업',
    '서양식전문점(커피류)':          '요식업',
    '일반대중음식':                  '요식업',
    '일반음식점':                    '요식업',
    '일반한식':                      '요식업',
    '한식':                          '요식업',
    '일식':                          '요식업',
    '중식':                          '요식업',
    '양식':                          '요식업',
    '패스트푸드':                    '요식업',
    '치킨':                          '요식업',
    '피자':                          '요식업',
    '분식':                          '요식업',
    '술집':                          '요식업',
    '주점':                          '요식업',
    '제과점':                        '요식업',
    '제과·제빵':                     '요식업',
    '식품류제조업':                  '요식업',

    # 유통
    '편의점':                        '유통',
    '편+의+점':                      '유통',
    '할인점/슈퍼마켓':               '유통',
    '대형마트':                      '유통',
    '백화점':                        '유통',
    '인터넷P/G':                     '유통',
    'PG일반(인증)':                  '유통',
    '인터넷상거래':                  '유통',
    '결제대행(PG)':                  '유통',
    '온라인상품권(카카오선물하기)':   '유통',
    '전자상거래(다품목취급)':         '유통',
    '온라인쇼핑':                    '유통',
    '소셜커머스':                    '유통',

    # 여행/레져/문화
    '관광민예,선물용품':             '여행/레져/문화',
    '인형++및++완구++아동용++자전거': '여행/레져/문화',
    '완+구+점':                      '여행/레져/문화',
    '공연장,극장':                   '여행/레져/문화',
    '공연/영화':                     '여행/레져/문화',
    '레저업소':                      '여행/레져/문화',
    '스포츠':                        '여행/레져/문화',
    '여행사':                        '여행/레져/문화',

    # 보험/병원
    '약국':                          '보험/병원',
    '개인병원':                      '보험/병원',

    # 보건위생
    '안경,콘텍트렌즈':               '보건위생',

    # 사무통신/서적/학원
    '서적':                          '사무통신/서적/학원',
    '인쇄,출판':                     '사무통신/서적/학원',

    # 자동차/연료/정비
    '택시':                          '자동차/연료/정비',
    '기타전문서비스(교통요금)':       '자동차/연료/정비',
    '기타전문점(교통-버스/지하철)':   '자동차/연료/정비',
    '인터넷상거래(버스/택시)':        '자동차/연료/정비',
    '온라인상품권(기후동행카드)':     '자동차/연료/정비',
    '주유소':                        '자동차/연료/정비',
    '세차':                          '자동차/연료/정비',
    '고속도로':                      '자동차/연료/정비',

    # 의류/신변잡화
    '의류':                          '의류/신변잡화',
    '스포츠용품':                    '의류/신변잡화',
    '신발':                          '의류/신변잡화',
    '잡화':                          '의류/신변잡화',

    # 가전/가구
    '가전제품':                      '가전/가구',
    '가구':                          '가전/가구',
    '인테리어':                      '가전/가구',

    # 학원
    '학원':                          '학원',
    '교육':                          '학원',

    # 숙박
    '숙박':                          '숙박',
    '호텔':                          '숙박',
    '모텔':                          '숙박',

    # 기타
    '기타4':                         '기타',
    '화+++원':                       '기타',
}

# ─────────────────────────────────────────
# 결제 카테고리 → 우리카드 피처 컬럼 매핑
# ─────────────────────────────────────────
CAT_MAP = {
    'FSBZ_AM':      ['요식업'],
    'RESTRNT_AM':   ['요식업'],
    'DIST_AM':      ['유통'],
    'TRVLEC_AM':    ['여행/레져/문화'],
    'TRVL_AM':      ['여행/레져/문화'],
    'CULTURE_AM':   ['여행/레져/문화'],
    'LEISURE_S_AM': ['여행/레져/문화'],
    'OFFEDU_AM':    ['사무통신/서적/학원'],
    'BOOK_AM':      ['사무통신/서적/학원'],
    'INSUHOS_AM':   ['보험/병원'],
    'HOS_AM':       ['보험/병원'],
    'PLSANIT_AM':   ['보건위생'],
    'AUTO_AM':      ['자동차/연료/정비'],
    'FUEL_AM':      ['자동차/연료/정비'],
    'CLOTHGDS_AM':  ['의류/신변잡화'],
    'INTERIOR_AM':  ['가전/가구'],
    'ACDM_AM':      ['학원'],
    'HOTEL_AM':     ['숙박'],
}


class LifecycleModel:
    def __init__(self):
        self.pipeline   = None
        self.le         = None
        self.is_trained = False

    # ─────────────────────────────────────
    # 학습 데이터 로딩
    # nrows: 테스트용 제한 (None이면 전체)
    # ─────────────────────────────────────
    def load_data(self, csv_path: str, nrows: int = None):
        if nrows:
            print(f"📂 CSV 로딩 중 (테스트 모드: {nrows:,}건만)...")
        else:
            print("📂 CSV 로딩 중 (전체)...")

        chunks = []
        total  = 0
        for chunk in pd.read_csv(csv_path, encoding='utf-8', chunksize=100000):
            chunk = chunk.dropna(subset=['LIFE_STAGE'])
            chunks.append(chunk)
            total += len(chunk)
            if nrows and total >= nrows:
                break
        df = pd.concat(chunks, ignore_index=True)
        if nrows:
            df = df.head(nrows)
        print(f"✅ 총 {len(df):,}건 로딩 완료")

        for col in FEATURE_COLS:
            if col not in df.columns:
                df[col] = 0

        df[FEATURE_COLS] = (
            df[FEATURE_COLS]
            .apply(pd.to_numeric, errors='coerce')
            .fillna(0)
        )

        return df[FEATURE_COLS], df['LIFE_STAGE']

    # ─────────────────────────────────────
    # 학습
    # ─────────────────────────────────────
    def train(self, csv_path: str = CSV_PATH, nrows: int = None):
        X, y = self.load_data(csv_path, nrows=nrows)

        self.le   = LabelEncoder()
        y_enc     = self.le.fit_transform(y)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
        )

        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('lgbm', LGBMClassifier(
                n_estimators=500,
                learning_rate=0.05,
                num_leaves=63,
                class_weight='balanced',
                n_jobs=-1,
                random_state=42,
                verbose=-1,
            ))
        ])

        print("🤖 LightGBM 학습 중...")
        self.pipeline.fit(X_train, y_train)
        self.is_trained = True

        y_pred = self.pipeline.predict(X_test)
        print("\n=== 학습 결과 ===")
        print(classification_report(y_test, y_pred, target_names=self.le.classes_))

        lgbm = self.pipeline.named_steps['lgbm']
        importance_df = pd.DataFrame({
            'feature':    FEATURE_COLS,
            'importance': lgbm.feature_importances_,
        }).sort_values('importance', ascending=False)

        print("\n=== 소비 피처 중요도 ===")
        max_imp = importance_df['importance'].max()
        for _, row in importance_df.iterrows():
            bar = '█' * int(row['importance'] / max_imp * 20)
            print(f"  {row['feature']:<15} {bar} {row['importance']:.0f}")

        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump({
                "pipeline":      self.pipeline,
                "label_encoder": self.le,
                "feature_cols":  FEATURE_COLS,
            }, f)
        print(f"\n✅ model.pkl 저장 완료! → {MODEL_PATH}")

    # ─────────────────────────────────────
    # 모델 로드
    # ─────────────────────────────────────
    def load_model(self):
        with open(MODEL_PATH, "rb") as f:
            saved = pickle.load(f)
        self.pipeline   = saved["pipeline"]
        self.le         = saved["label_encoder"]
        self.is_trained = True
        print("✅ model.pkl 로드 완료!")

    # ─────────────────────────────────────
    # 예측
    # INPUT:  피처 딕셔너리
    # OUTPUT: 생애주기 코드/라벨/확신도/상위3후보
    # ─────────────────────────────────────
    def predict(self, features: dict) -> dict:
        if not self.is_trained:
            self.load_model()

        X = pd.DataFrame(
            [[features.get(col, 0) for col in FEATURE_COLS]],
            columns=FEATURE_COLS
        )

        pred_enc   = self.pipeline.predict(X)[0]
        pred_label = self.le.inverse_transform([pred_enc])[0]
        proba      = self.pipeline.predict_proba(X)[0]

        top3_idx = np.argsort(proba)[::-1][:3]
        top3 = [
            {
                "code":        self.le.inverse_transform([i])[0],
                "label":       LIFECYCLE_KO.get(self.le.inverse_transform([i])[0], ""),
                "probability": round(float(proba[i]), 3),
            }
            for i in top3_idx
        ]

        return {
            "lifecycle_code":  pred_label,
            "lifecycle_label": LIFECYCLE_KO.get(pred_label, pred_label),
            "confidence":      round(float(proba.max()), 3),
            "top3_candidates": top3,
        }

    # ─────────────────────────────────────
    # 결제내역 → 피처 변환
    # INPUT:  transactions 리스트 + age + gender
    # OUTPUT: 피처 딕셔너리 (월평균 지출액)
    # ─────────────────────────────────────
    def transactions_to_features(self, user_transactions: list,
                                  age: int = 0, gender: int = 0) -> dict:
        df = pd.DataFrame(user_transactions)

        # payment_date 기반 실제 기간(월수) 계산
        if 'payment_date' in df.columns:
            df['payment_date'] = pd.to_datetime(
                df['payment_date'].astype(str), format='%Y%m%d', errors='coerce'
            )
            min_date = df['payment_date'].min()
            max_date = df['payment_date'].max()
            days     = (max_date - min_date).days + 1
            months   = max(days / 30, 0.1)
            print(f"📅 결제 기간: {min_date.date()} ~ {max_date.date()} ({days}일 = {months:.1f}개월)")
        else:
            months = 1.0
            print("📅 payment_date 없음 → 1개월로 가정")

        # 가맹점명 → 우리카드 대분류 카테고리
        df['payment_category'] = (
            df['payment_category']
            .map(RAW_TO_UNIFIED)
            .fillna('기타')
        )

        features = {}

        # 카테고리별 월평균 지출 계산
        for col, categories in CAT_MAP.items():
            if categories:
                mask = df['payment_category'].isin(categories)
                features[col] = float(df[mask]['payment_price'].sum() / months)
            else:
                features[col] = 0.0

        # 총이용금액
        features['TOT_USE_AM']   = float(df['payment_price'].sum() / months)
        features['CRDSL_USE_AM'] = features['TOT_USE_AM']
        features['CNF_USE_AM']   = 0.0

        # 나이/성별 (5살 단위)
        features['AGE']    = (age // 5) * 5
        features['SEX_CD'] = gender

        for col in FEATURE_COLS:
            if col not in features:
                features[col] = 0.0

        return features

    # ─────────────────────────────────────
    # 메인 예측 함수 (API에서 호출)
    # ─────────────────────────────────────
    def predict_from_transactions(self, user_transactions: list,
                                   age: int = 0, gender: int = 0) -> dict:
        features = self.transactions_to_features(user_transactions, age=age, gender=gender)
        return self.predict(features)


# 싱글톤
lifecycle_model = LifecycleModel()


# ─────────────────────────────────────────
# 직접 실행
#   python lifecycle_model.py             → user_id=1, 예측만
#   python lifecycle_model.py --train     → user_id=1, 재학습 후 예측
#   python lifecycle_model.py --user 2    → user_id=2, 예측만
#   python lifecycle_model.py --train --user 2 → user_id=2, 재학습 후 예측
# ─────────────────────────────────────────
if __name__ == "__main__":
    import sys

    force_train = "--train" in sys.argv

    # user_id 파싱 (default=1)
    user_id = 1
    if "--user" in sys.argv:
        idx = sys.argv.index("--user")
        if idx + 1 < len(sys.argv):
            user_id = int(sys.argv[idx + 1])
    print(f"👤 대상 user_id = {user_id}")

    # ── STEP 1. 학습 or 모델 로드 ──────────────
    if force_train:
        print("🔄 강제 재학습 모드")
        lifecycle_model.train()
    elif os.path.exists(MODEL_PATH):
        print(f"✅ 기존 model.pkl 발견 → 학습 생략 ({MODEL_PATH})")
        lifecycle_model.load_model()
    else:
        print(f"⚠️  model.pkl 없음 → 학습 시작")
        lifecycle_model.train()

    # ── STEP 2. DB 연결 ─────────────────────────
    print("\n🔌 DB 연결 중...")
    try:
        engine = create_engine(
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
            connect_args={"connect_timeout": 5}
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"✅ DB 연결 성공 ({DB_HOST}/{DB_NAME})")
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")
        sys.exit(1)

    # ── STEP 3. 유저 정보 조회 ──────────────────
    df_user = pd.read_sql(text("""
        SELECT age, gender
        FROM users
        WHERE user_id = :uid
    """), engine, params={"uid": user_id})

    if df_user.empty:
        age    = 0
        gender = 0
        print("⚠️  유저 정보 없음 → 나이/성별 0으로 처리")
    else:
        age    = int(df_user['age'].iloc[0])
        gender = 1 if str(df_user['gender'].iloc[0]).lower() == 'm' else 2
        print(f"✅ 유저 정보: 나이={age}, 성별={'남' if gender == 1 else '여'}")

    # ── STEP 4. 결제내역 조회 ───────────────────
    df_tx = pd.read_sql(text("""
        SELECT payment_category, payment_price, payment_date
        FROM transactions
        WHERE user_id = :uid
          AND payment_price > 0
    """), engine, params={"uid": user_id})

    if df_tx.empty:
        print(f"❌ user_id={user_id} 의 결제내역이 없습니다.")
        sys.exit(1)

    print(f"✅ 결제내역 {len(df_tx)}건 조회 완료")

    # 카테고리별 소비 현황
    print("\n[카테고리별 소비 현황]")
    _dates  = pd.to_datetime(df_tx['payment_date'].astype(str), format='%Y%m%d', errors='coerce')
    _days   = (_dates.max() - _dates.min()).days + 1
    _months = max(_days / 30, 0.1)
    cat_summary = (
        df_tx.groupby('payment_category')['payment_price']
        .agg(['sum', 'count'])
        .rename(columns={'sum': '총지출', 'count': '건수'})
        .sort_values('총지출', ascending=False)
    )
    cat_summary['월평균'] = (cat_summary['총지출'] / _months).astype(int)
    print(cat_summary.to_string())

    # ── STEP 5. 생애주기 예측 ───────────────────
    result = lifecycle_model.predict_from_transactions(
        df_tx.to_dict('records'), age=age, gender=gender
    )

    print("\n" + "=" * 45)
    print(f"  👤 user_id = {user_id}  (나이: {age}세, 성별: {'남' if gender==1 else '여'})")
    print(f"  🎯 예측 생애주기: {result['lifecycle_label']} ({result['lifecycle_code']})")
    print(f"  📊 확신도: {result['confidence'] * 100:.0f}%")
    print("=" * 45)

    print("\n🏅 상위 3개 후보:")
    for i, cand in enumerate(result['top3_candidates'], 1):
        bar = '█' * int(cand['probability'] * 30)
        print(f"  {i}. {cand['label']:<10} {bar} {cand['probability']*100:.0f}%")
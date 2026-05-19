import pickle
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from dotenv import load_dotenv
import os

# .env 로드
load_dotenv()

DB_HOST     = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT     = os.getenv("DB_PORT", "3306")
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME     = os.getenv("DB_NAME", "wonpick")
CSV_PATH    = os.getenv("CSV_PATH", "data/wooricard.csv")
MODEL_PATH  = os.getenv("MODEL_PATH", "ml/model.pkl")

FEATURE_COLS = [
    'AGE', 'AGE', 'AGE', 'AGE', 'AGE',
    'SEX_CD', 'MBR_RK',
    'TOT_USE_AM', 'CRDSL_USE_AM', 'CNF_USE_AM',
    'INTERIOR_AM', 'INSUHOSPAM', 'OFFEDUS_AM', 'TRVLEC_AM',
    'FSBZ_AM', 'DIST_AM', 'CLOTHGDS_AM', 'AUTO_AM',
    'RESTRNT_AM', 'HOS_AM', 'ACDM_AM', 'HOTEL_AM', 'TRVL_AM',
]

LIFECYCLE_KO = {
    'TEEN': '십대', 'UNI': '대학생', 'NEW_JOB': '사회초년생',
    'NEW_WED': '신혼', 'CHILD_BABY': '자녀영유아',
    'CHILD_TEEN': '자녀의무교육', 'CHILD_UNI': '자녀대학생',
    'GOLLIFE': '중년기타', 'SECLIFE': '2nd Life', 'RETIR': '은퇴'
}

RAW_TO_UNIFIED = {
    '커피전문점': '카페/음료', '서양식전문점(커피류)': '카페/음료', '결제대행(PG)': '카페/음료',
    '일반대중음식': '식사', '일반음식점': '식사', '일반한식': '식사',
    '한식': '식사', '일식': '식사', '패스트푸드': '식사',
    '편의점': '편의점', '편+의+점': '편의점',
    '약국': '의료/약국', '개인병원': '의료/약국',
    '제과점': '제과/베이커리', '제과·제빵': '제과/베이커리', '식품류제조업': '제과/베이커리',
    '택시': '교통', '기타전문서비스(교통요금)': '교통',
    '기타전문점(교통-버스/지하철)': '교통',
    '인터넷상거래(버스/택시)': '교통', '온라인상품권(기후동행카드)': '교통',
    '인터넷P/G': '쇼핑/온라인', 'PG일반(인증)': '쇼핑/온라인', '인터넷상거래': '쇼핑/온라인',
    '서적': '서적',
    '온라인상품권(카카오선물하기)': '선물/상품권', '관광민예,선물용품': '선물/상품권',
    '인형++및++완구++아동용++자전거': '완구/취미', '완+구+점': '완구/취미',
    '기타4': '기타', '안경,콘텍트렌즈': '기타',
    '인쇄,출판': '기타', '할인점/슈퍼마켓': '기타', '화+++원': '기타',
}

CAT_MAP = {
    'FSBZ_AM':     ['식사'],
    'RESTRNT_AM':  ['식사'],
    'TRVLEC_AM':   ['카페/음료'],
    'HOS_AM':      ['의료/약국'],
    'DIST_AM':     ['편의점'],
    'OFFEDUS_AM':  ['서적'],
    'CLOTHGDS_AM': ['제과/베이커리'],
    'AUTO_AM':     ['교통'],
    'TRVL_AM':     ['선물/상품권'],
    'INTERIOR_AM': ['완구/취미'],
    'ACDM_AM':     ['기타', '쇼핑/온라인'],
    'HOTEL_AM':    [],
    'INSUHOSPAM':  [],
    'CNF_USE_AM':  [],
}

IMPOSSIBLE_BY_AGE = {
    20: ['CHILD_BABY', 'CHILD_TEEN', 'CHILD_UNI', 'GOLLIFE', 'SECLIFE', 'RETIR'],
    25: ['CHILD_TEEN', 'CHILD_UNI', 'GOLLIFE', 'SECLIFE', 'RETIR'],
    30: ['CHILD_UNI', 'SECLIFE', 'RETIR', 'TEEN'],
    35: ['SECLIFE', 'RETIR', 'TEEN', 'UNI'],
    40: ['NEW_JOB', 'RETIR', 'TEEN', 'UNI'],
    45: ['NEW_JOB', 'NEW_WED', 'RETIR', 'TEEN', 'UNI'],
    50: ['NEW_JOB', 'NEW_WED', 'TEEN', 'UNI'],
    55: ['NEW_JOB', 'NEW_WED', 'TEEN', 'UNI'],
    60: ['NEW_JOB', 'NEW_WED', 'CHILD_BABY', 'TEEN', 'UNI'],
    65: ['NEW_JOB', 'NEW_WED', 'CHILD_BABY', 'CHILD_TEEN', 'TEEN', 'UNI'],
    70: ['NEW_JOB', 'NEW_WED', 'CHILD_BABY', 'CHILD_TEEN', 'TEEN', 'UNI'],
}

DEFAULT_BY_AGE = {
    20: 'NEW_JOB', 25: 'NEW_JOB', 30: 'NEW_WED',
    35: 'CHILD_BABY', 40: 'CHILD_TEEN', 45: 'CHILD_TEEN',
    50: 'CHILD_UNI', 55: 'SECLIFE', 60: 'SECLIFE',
    65: 'SECLIFE', 70: 'RETIR', 75: 'RETIR',
    80: 'RETIR', 85: 'RETIR'
}


class LifecycleModel:
    def __init__(self):
        self.pipeline = None
        self.le = None
        self.is_trained = False

    def load_data(self, csv_path: str):
        df = pd.read_csv(csv_path, encoding='utf-8', nrows=500000)
        df = df.dropna(subset=['LIFE_STAGE'])

        df = df[df['AGE'] != '기타']
        df['AGE'] = pd.to_numeric(df['AGE'], errors='coerce')
        df = df.dropna(subset=['AGE'])

        unique_cols = list(dict.fromkeys(FEATURE_COLS))
        for col in unique_cols:
            if col not in df.columns:
                df[col] = 0

        df[unique_cols] = df[unique_cols].fillna(0)
        df[unique_cols] = df[unique_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

        X = pd.concat([df[col] for col in FEATURE_COLS], axis=1)
        X.columns = range(len(FEATURE_COLS))
        return X, df['LIFE_STAGE']

    def train(self, csv_path: str = CSV_PATH):
        print("📂 데이터 로딩 중...")
        X, y = self.load_data(csv_path)
        print(f"✅ 데이터 로딩 완료: {len(X)}건")

        self.le = LabelEncoder()
        y_enc = self.le.fit_transform(y)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
        )

        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('knn', KNeighborsClassifier(n_neighbors=5, n_jobs=-1))
        ])

        print("🤖 KNN 학습 중...")
        self.pipeline.fit(X_train, y_train)
        self.is_trained = True

        print("\n=== 학습 결과 ===")
        print(classification_report(
            y_test,
            self.pipeline.predict(X_test),
            target_names=self.le.classes_
        ))

        with open(MODEL_PATH, "wb") as f:
            pickle.dump({"pipeline": self.pipeline, "label_encoder": self.le}, f)
        print("✅ model.pkl 저장 완료!")

    def load_model(self):
        with open(MODEL_PATH, "rb") as f:
            saved = pickle.load(f)
        self.pipeline = saved["pipeline"]
        self.le = saved["label_encoder"]
        self.is_trained = True
        print("✅ model.pkl 로드 완료!")

    def predict(self, features: dict) -> dict:
        if not self.is_trained:
            self.load_model()

        X = np.array([[features.get(col, 0) for col in FEATURE_COLS]])
        pred_enc = self.pipeline.predict(X)[0]
        pred_label = self.le.inverse_transform([pred_enc])[0]
        proba = self.pipeline.predict_proba(X)[0]

        return {
            "lifecycle_code": pred_label,
            "lifecycle_label": LIFECYCLE_KO.get(pred_label, pred_label),
            "confidence": round(float(proba.max()), 3)
        }

    def transactions_to_features(self, user_transactions: list, age: int = 0, gender: int = 0) -> dict:
        df = pd.DataFrame(user_transactions)

        df['payment_category'] = df['payment_category'].map(RAW_TO_UNIFIED).fillna('기타')

        features = {}
        for col, categories in CAT_MAP.items():
            if categories:
                mask = df['payment_category'].isin(categories)
                features[col] = float(df[mask]['payment_out'].sum() / 6)
            else:
                features[col] = 0.0

        features['TOT_USE_AM'] = float(df['payment_out'].sum() / 6)
        features['CRDSL_USE_AM'] = features['TOT_USE_AM']
        features['AGE'] = (age // 5) * 5
        features['SEX_CD'] = gender
        features['MBR_RK'] = 0

        for col in set(FEATURE_COLS):
            if col not in features:
                features[col] = 0

        return features

    def predict_from_transactions(self, user_transactions: list, age: int = 0, gender: int = 0) -> dict:
        features = self.transactions_to_features(user_transactions, age, gender)
        result = self.predict(features)

        age_5 = (age // 5) * 5
        if age_5 in IMPOSSIBLE_BY_AGE and result['lifecycle_code'] in IMPOSSIBLE_BY_AGE[age_5]:
            corrected = DEFAULT_BY_AGE.get(age_5, result['lifecycle_code'])
            result['lifecycle_code'] = corrected
            result['lifecycle_label'] = LIFECYCLE_KO.get(corrected, corrected)
            result['corrected'] = True

        return result


# 싱글톤
lifecycle_model = LifecycleModel()

if __name__ == "__main__":
    lifecycle_model.train()

    # .env에서 DB 연결
    engine = create_engine(
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    df_tx = pd.read_sql("""
        SELECT payment_category, payment_out
        FROM transactions
        WHERE user_id = 'user_haeun'
        AND payment_out > 0
    """, engine)

    user_df = pd.read_sql("""
        SELECT age, gender
        FROM users
        WHERE user_id = 'user_haeun'
    """, engine)

    age = int(user_df['age'].iloc[0]) if not user_df.empty else 0
    gender = 1 if user_df['gender'].iloc[0] == 'm' else 2

    result = lifecycle_model.predict_from_transactions(
        df_tx.to_dict('records'), age=age, gender=gender
    )

    print(f"\n👤 user_haeun (나이: {age}, 성별: {'남' if gender == 1 else '여'})")
    print(f"🎯 예측 생애주기: {result['lifecycle_label']} ({result['lifecycle_code']})")
    print(f"📊 확신도: {result['confidence'] * 100:.0f}%")
    if result.get('corrected'):
        print("⚠️ 나이 기반으로 보정됨")
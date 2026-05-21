from app.services.lifecycle_service import engine
from sqlalchemy import text
import pandas as pd
from datetime import datetime

# DB 카테고리 → 통합 카테고리 매핑
CATEGORY_MAP = {
    # 교통
    '기타전문서비스(교통요금)':              '교통',
    '인터넷상거래(버스/택시)':               '교통',
    '택시':                               '교통',
    '기타전문점(교통-버스/지하철)':           '교통',
    '온라인상품권(기후동행카드)':             '교통',

    # 카페/음료
    '서양식전문점(커피류)':                  '카페/음료',
    '커피전문점':                           '카페/음료',
    '결제대행(PG)':                         '카페/음료',

    # 식사
    '일반음식점':                           '식사',
    '일반대중음식':                         '식사',
    '일반한식':                             '식사',
    '한식':                               '식사',
    '일식':                               '식사',
    '패스트푸드':                           '식사',

    # 편의점
    '편의점':                              '편의점',
    '편+의+점':                            '편의점',

    # 쇼핑/온라인
    'PG일반(인증)':                         '쇼핑/온라인',
    '인터넷P/G':                           '쇼핑/온라인',
    '전자상거래(다품목취급)':                 '쇼핑/온라인',

    # 제과/베이커리
    '제과·제빵':                            '제과/베이커리',
    '제과점':                              '제과/베이커리',
    '식품류제조업':                          '제과/베이커리',

    # 선물/상품권
    '온라인상품권(카카오선물하기)':            '선물/상품권',
    '관광민예,선물용품':                     '선물/상품권',

    # 의료/약국
    '약국':                               '의료/약국',
    '개인병원':                            '의료/약국',

    # 완구/취미
    '인형++및++완구++아동용++자전거':          '완구/취미',
    '완+구+점':                            '완구/취미',
    '공연장,극장':                          '완구/취미',

    # 서적
    '서적':                               '서적',

    # 기타
    '기타4':                              '기타',
    '안경,콘텍트렌즈':                      '기타',
    '인쇄,출판':                           '기타',
    '할인점/슈퍼마켓':                      '기타',
}

# 통합 카테고리 색상
CATEGORY_COLORS = {
    '교통':        '#60a5fa',
    '카페/음료':   '#38BDF8',
    '식사':        '#1e73be',
    '편의점':      '#93c5fd',
    '쇼핑/온라인': '#2563eb',
    '제과/베이커리':'#0ea5e9',
    '선물/상품권': '#7dd3fc',
    '의료/약국':   '#1d4ed8',
    '완구/취미':   '#6366f1',
    '서적':        '#a5b4fc',
    '기타':        '#94a3b8',
}

def get_transaction_report(user_id: int):  
    
    # 이번 달 연월 계산
    current_ym = datetime.now().strftime("%Y%m")  # ex) "202605"

    df = pd.read_sql(text("""
        SELECT payment_category, payment_time, payment_date, payment_out
        FROM transactions
        WHERE user_id = :user_id
        AND payment_out > 0
        AND payment_date LIKE :ym
    """), engine, params={
        "user_id": user_id,
        "ym": f"{current_ym}%"  # "202605%" → 이번 달 데이터만
    })

    if df.empty:
        return {
            "payment_price": 0,
            "payment_total_num": 0,
            "category_price": {},
            "timepattern_price": {},
            "weekly_price": [],
            "weekly_categories": [],
        }

    # 카테고리 매핑 적용
    df['payment_category'] = df['payment_category'].map(CATEGORY_MAP).fillna('기타')

    def classify_time(t):
        if t is None: return '기타'
        hour = int(str(t).zfill(6)[:2])
        if 0 <= hour < 6:      return '새벽'
        elif 6 <= hour < 11:   return '아침'
        elif 11 <= hour < 14:  return '점심'
        elif 14 <= hour < 20:  return '저녁'
        else:                  return '심야'

    def classify_week(d):
        if d is None: return '기타'
        day = int(str(d)[6:8])
        if day <= 7:    return '1주'
        elif day <= 14: return '2주'
        elif day <= 21: return '3주'
        else:           return '4주'

    df['time_label'] = df['payment_time'].apply(classify_time)
    df['week_label'] = df['payment_date'].apply(classify_week)

    # 상위 2개 카테고리
    top2_categories = (
        df.groupby('payment_category')['payment_out']
        .sum().nlargest(2).index.tolist()
    )

    # 주차별 × 상위 2개 카테고리 집계
    df_top2 = df[df['payment_category'].isin(top2_categories)]
    weekly_pivot = (
        df_top2.groupby(['week_label', 'payment_category'])['payment_out']
        .sum().astype(int).unstack(fill_value=0)
    )

    week_order = ['1주', '2주', '3주', '4주']
    weekly_price = []
    for week in week_order:
        if week in weekly_pivot.index:
            row = {'week': week}
            for cat in top2_categories:
                row[cat] = int(weekly_pivot.loc[week, cat]) if cat in weekly_pivot.columns else 0
            weekly_price.append(row)

    return {
        "payment_price": int(df['payment_out'].sum()),
        "payment_total_num": len(df),
        "payment_days": df['payment_date'].nunique(),
        "category_price": df.groupby('payment_category')['payment_out'].sum().astype(int).to_dict(),
        "timepattern_price": df.groupby('time_label')['payment_out'].sum().astype(int).to_dict(),
        "weekly_price": weekly_price,
        "weekly_categories": top2_categories,
        "category_colors": CATEGORY_COLORS,
    }
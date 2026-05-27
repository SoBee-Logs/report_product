from sqlalchemy import text
import pandas as pd
from app.services.lifecycle_service import engine
from ml.lifecycle_model import RAW_TO_UNIFIED
from app.models.schemas import AiInsightContent, AiInsightItem, AiInsightResponse
from datetime import datetime
import calendar

CATEGORY_TO_CATE = {
    '카페/음료': '카페',
    '식사': '일반음식점',
    '편의점': '편의점',
    '쇼핑/온라인': '온라인쇼핑',
    '교통': '교통',
    '의료/약국': '약국',
    '제과/베이커리': '베이커리',
    '선물/상품권': '쇼핑',
    '서적': '도서',
    '기타': '모든가맹점',
}

LIFE_STAGE_KO = {
    'TEEN':       '십대',
    'UNI':        '대학생',
    'NEW_JOB':    '사회초년생',
    'NEW_WED':    '신혼부부',
    'CHILD_BABY': '영유아 자녀',
    'CHILD_TEEN': '자녀 의무교육',
    'CHILD_UNI':  '자녀 대학생',
    'GOLLIFE':    '중년',
    'SECLIFE':    '2nd Life',
    'RETIR':      '은퇴',
}

LIFE_STAGE_SAVE_TRM = {
    'TEEN':       6,
    'UNI':        12,
    'NEW_JOB':    12,
    'NEW_WED':    24,
    'CHILD_BABY': 36,
    'CHILD_TEEN': 36,
    'CHILD_UNI':  24,
    'GOLLIFE':    24,
    'SECLIFE':    12,
    'RETIR':      12,
}

CHILD_STAGES = {'TEEN', 'CHILD_BABY', 'CHILD_TEEN', 'CHILD_UNI'}

CHILD_KEYWORDS = '키즈|아이|어린이|주니어|청소년|영유아|태아|baby|kids|junior'


def _query_card(cate_name: str, top_category: str) -> AiInsightItem | None:
    df = pd.read_sql(text("""
        SELECT ci.card_name, ci.corp_name, ci.card_img_url, ci.gorilla_id,
               ci.annual_fee_basic, cb.title AS benefit_title, cb.comment AS benefit_comment
        FROM card_info ci
        JOIN card_benefits cb ON ci.card_info_id = cb.card_info_id
        WHERE cb.cate_name = :cate_name
          AND ci.card_img_url IS NOT NULL
          AND ci.is_discontinued = 0
        ORDER BY RAND()
        LIMIT 1
    """), engine, params={"cate_name": cate_name})

    if df.empty:
        df = pd.read_sql(text("""
            SELECT ci.card_name, ci.corp_name, ci.card_img_url, ci.gorilla_id,
                   ci.annual_fee_basic, cb.title AS benefit_title, cb.comment AS benefit_comment
            FROM card_info ci
            JOIN card_benefits cb ON ci.card_info_id = cb.card_info_id
            WHERE cb.cate_name = '모든가맹점'
              AND ci.card_img_url IS NOT NULL
              AND ci.is_discontinued = 0
            ORDER BY RAND()
            LIMIT 1
        """), engine)

    if df.empty:
        return None

    r = df.iloc[0]
    gorilla_id = r['gorilla_id']
    card_url = f"https://www.card-gorilla.com/card/detail/{gorilla_id}" if gorilla_id else None
    reason = f"이번 달 {top_category} 지출이 많아 관련 혜택 카드를 추천해요"

    return AiInsightItem(
        product_name=r['card_name'],
        product_company=r['corp_name'],
        product_img_url=r['card_img_url'] or None,
        product_type='card',
        reason=reason,
        content=AiInsightContent(
            header=r['benefit_title'],
            middle=r['benefit_comment'],
            small=f"연회비 {r['annual_fee_basic']}" if r['annual_fee_basic'] else None,
            url=card_url,
        ),
    )


def _query_savings(save_trm: int = 12, life_stage_code: str | None = None) -> AiInsightItem | None:
    is_child_stage = life_stage_code in CHILD_STAGES
    if is_child_stage:
        df = pd.read_sql(text("""
            SELECT fin_prdt_nm, kor_co_nm, intr_rate, intr_max_rate, save_trm, spcl_cnd
            FROM (
                SELECT fin_prdt_nm, kor_co_nm, intr_rate, intr_max_rate, save_trm, spcl_cnd
                FROM savings_products
                WHERE save_trm = :save_trm
                ORDER BY intr_max_rate DESC
                LIMIT 5
            ) AS top5
            ORDER BY RAND()
            LIMIT 1
        """), engine, params={"save_trm": save_trm})
    else:
        df = pd.read_sql(text("""
            SELECT fin_prdt_nm, kor_co_nm, intr_rate, intr_max_rate, save_trm, spcl_cnd
            FROM (
                SELECT fin_prdt_nm, kor_co_nm, intr_rate, intr_max_rate, save_trm, spcl_cnd
                FROM savings_products
                WHERE save_trm = :save_trm
                  AND fin_prdt_nm NOT REGEXP :child_kw
                ORDER BY intr_max_rate DESC
                LIMIT 5
            ) AS top5
            ORDER BY RAND()
            LIMIT 1
        """), engine, params={"save_trm": save_trm, "child_kw": CHILD_KEYWORDS})

    if df.empty:
        return None

    r = df.iloc[0]
    stage_ko = LIFE_STAGE_KO.get(life_stage_code, '회원')
    reason = f"{stage_ko}에게 맞는 {r['save_trm']}개월 적금 상품이에요 (최고 연 {r['intr_max_rate']}%)"

    return AiInsightItem(
        product_name=r['fin_prdt_nm'],
        product_company=r['kor_co_nm'],
        product_img_url=None,
        product_type='savings',
        reason=reason,
        content=AiInsightContent(
            header=f"최고 연 {r['intr_max_rate']}% (기본 {r['intr_rate']}%)",
            middle=f"{r['save_trm']}개월 정기적금",
        ),
    )


async def get_ai_insight(user_id: int, year: int = None, month: int = None) -> AiInsightResponse:
    # ✅ year/month 없으면 현재 달 fallback
    now = datetime.now()
    target_year  = year  if year  else now.year
    target_month = month if month else now.month

    first_day = datetime(target_year, target_month, 1).strftime("%Y-%m-%d")
    last_day  = datetime(
        target_year,
        target_month,
        calendar.monthrange(target_year, target_month)[1]
    ).strftime("%Y-%m-%d")

    df_user = pd.read_sql(text("""
        SELECT life_stage_code FROM users WHERE user_id = :user_id
    """), engine, params={"user_id": user_id})
    life_stage_code = df_user['life_stage_code'].iloc[0] if not df_user.empty else None
    if pd.isna(life_stage_code) if life_stage_code is not None else True:
        life_stage_code = None

    # ✅ 해당 월 데이터만 필터링
    df_tx = pd.read_sql(text("""
        SELECT payment_category, payment_out
        FROM transactions
        WHERE user_id = :user_id
          AND payment_date BETWEEN :start AND :end
    """), engine, params={
        "user_id": user_id,
        "start": first_day,
        "end": last_day,
    })

    top_category = '기타'
    cate_name = '모든가맹점'
    if not df_tx.empty:
        df_tx['unified'] = df_tx['payment_category'].map(RAW_TO_UNIFIED).fillna('기타')
        top_category = df_tx.groupby('unified')['payment_out'].sum().idxmax()
        cate_name = CATEGORY_TO_CATE.get(top_category, '모든가맹점')

    card_item = _query_card(cate_name, top_category)

    save_trm = LIFE_STAGE_SAVE_TRM.get(life_stage_code, 12)
    savings_item = _query_savings(save_trm, life_stage_code)

    items = [x for x in [card_item, savings_item] if x is not None]

    message = None
    if not life_stage_code:
        message = '생애주기 분석이 되지 않아 일반 추천을 드려요'

    return AiInsightResponse(recommned=items, message=message)
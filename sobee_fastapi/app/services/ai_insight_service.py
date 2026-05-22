from sqlalchemy import text
import pandas as pd
from app.services.lifecycle_service import engine
from ml.lifecycle_model import RAW_TO_UNIFIED
from app.models.schemas import AiInsightContent, AiInsightItem, AiInsightResponse

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


def _query_card(cate_name: str) -> AiInsightItem | None:
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
        # fallback: 모든가맹점
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

    return AiInsightItem(
        product_name=r['card_name'],
        product_company=r['corp_name'],
        product_img_url=r['card_img_url'] or None,
        product_type='card',
        content=AiInsightContent(
            header=r['benefit_title'],
            middle=r['benefit_comment'],
            small=f"연회비 {r['annual_fee_basic']}" if r['annual_fee_basic'] else None,
            url=card_url,
        ),
    )


def _query_savings() -> AiInsightItem | None:
    df = pd.read_sql(text("""
        SELECT fin_prdt_nm, kor_co_nm, intr_rate, intr_max_rate, save_trm, spcl_cnd
        FROM savings_products
        WHERE save_trm = 12
        ORDER BY intr_max_rate DESC
        LIMIT 1
    """), engine)

    if df.empty:
        return None

    r = df.iloc[0]
    spcl = r['spcl_cnd'] or ''
    spcl_short = (spcl[:80] + '...') if len(spcl) > 80 else spcl

    return AiInsightItem(
        product_name=r['fin_prdt_nm'],
        product_company=r['kor_co_nm'],
        product_img_url=None,
        product_type='savings',
        content=AiInsightContent(
            header=f"최고 연 {r['intr_max_rate']}% (기본 {r['intr_rate']}%)",
            middle=f"{r['save_trm']}개월 정기적금",
            small=spcl_short or None,
        ),
    )


async def get_ai_insight(user_id: int) -> AiInsightResponse:
    df_tx = pd.read_sql(text("""
        SELECT payment_category, payment_price
        FROM transactions
        WHERE user_id = :user_id AND payment_price > 0
    """), engine, params={"user_id": user_id})

    cate_name = '모든가맹점'
    if not df_tx.empty:
        df_tx['unified'] = df_tx['payment_category'].map(RAW_TO_UNIFIED).fillna('기타')
        top_category = df_tx.groupby('unified')['payment_price'].sum().idxmax()
        cate_name = CATEGORY_TO_CATE.get(top_category, '모든가맹점')

    card_item = _query_card(cate_name)
    savings_item = _query_savings()

    items = [x for x in [card_item, savings_item] if x is not None]

    df_user = pd.read_sql(text("""
        SELECT life_stage_code FROM users WHERE user_id = :user_id
    """), engine, params={"user_id": user_id})
    life_stage_code = df_user['life_stage_code'].iloc[0] if not df_user.empty else None

    message = None
    if not life_stage_code or pd.isna(life_stage_code):
        message = '생애주기 분석이 되지 않아 일반 추천을 드려요'

    return AiInsightResponse(recommned=items, message=message)

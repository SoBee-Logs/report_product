import aiomysql
from app.db.connection import get_pool


async def get_recent_transactions(user_id: str, limit: int = 50) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT payment_date, payment_time, payment_out,
                       payment_place, payment_category, payment_address
                FROM transactions
                WHERE user_id = %s
                ORDER BY payment_date DESC, payment_time DESC
                LIMIT %s
                """,
                (user_id, limit),
            )
            rows = await cur.fetchall()
    return [dict(row) for row in rows]

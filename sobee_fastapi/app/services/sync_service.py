async def sync_transactions(user_id: int) -> dict:
    """카드 + 계좌 원천 데이터를 수집해 transactions 테이블에 병합/적재.
    마이데이터 API 연동 후 구현 예정."""
    # TODO: 마이데이터 API 호출 → card_transactions, bank_transactions 적재
    # TODO: 두 테이블 병합 + 취소/수입 제거 + 중복 제거 → transactions upsert
    raise NotImplementedError("sync_transactions: 마이데이터 API 연동 후 구현")

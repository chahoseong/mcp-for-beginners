"""우리 재고 조회 코드와 실제 DummyJSON API의 통합을 검증한다."""

import json
from datetime import UTC, datetime, timedelta

import pytest

from app.tools.stock import check_stock


@pytest.mark.anyio
async def test_should_return_stock_result_when_dummyjson_responds() -> None:
    """
    Given: 실제 DummyJSON API와 상품 ID 1, 요청 수량 1.
    When: check_stock이 네트워크로 상품을 조회한다.
    Then: 성공 필드·재고 판단·UTC 확인 시각이 유효하며 재고 숫자는 고정하지 않는다.
    """
    before = datetime.now(UTC)
    result = await check_stock(product_id=1, quantity=1)
    after = datetime.now(UTC)

    assert set(result) == {
        "status", "product_id", "requested_quantity", "stock", "in_stock",
        "checked_at",
    }
    assert result["status"] == "ok"
    assert result["product_id"] == 1
    assert result["requested_quantity"] == 1
    assert type(result["stock"]) is int and result["stock"] >= 0
    assert result["in_stock"] is (result["stock"] >= 1)
    checked_at = datetime.fromisoformat(result["checked_at"])
    assert checked_at.utcoffset() == timedelta(0)
    assert before <= checked_at <= after
    print("DummyJSON result:", json.dumps(result, ensure_ascii=False))

"""우리 재고·검색·견적 코드와 실제 DummyJSON API의 통합을 검증한다."""

import json
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from app.tools.stock import check_stock
from app.tools.search import search_products
from app.tools.quote import calculate_quote
from tests.integration.assertions import assert_quote_result, assert_search_result


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


@pytest.mark.anyio
async def test_should_return_search_candidates_when_dummyjson_category_responds(
    dummyjson_category_products: list[dict[str, Any]],
) -> None:
    """
    Given: limit=0으로 별도 조회한 smartphones 카테고리의 현재 전체 원본.
    When: search_products를 직접 호출해 카테고리의 모든 페이지를 조회한다.
    Then: 후보 필드·순서·전체 목록과 count가 원본의 현재 상품 목록과 일치한다.
    """
    result = await search_products(category="smartphones")
    assert_search_result(result, dummyjson_category_products)


@pytest.mark.anyio
async def test_should_return_quote_result_when_dummyjson_product_responds(
    dummyjson_product: dict[str, Any],
) -> None:
    """
    Given: 별도 조회한 상품 ID 1의 현재 원본과 수량 3·예산 2000.
    When: calculate_quote를 직접 호출해 상품을 조회하고 견적을 계산한다.
    Then: 원본 상품 정보·단계별 계산 금액·예산 판단·UTC 안내기간이 유효하다.
    """
    before = datetime.now(UTC)
    result = await calculate_quote(product_id=1, quantity=3, budget=2000)
    after = datetime.now(UTC)
    assert_quote_result(
        result, dummyjson_product, quantity=3, budget=2000,
        before=before, after=after,
    )

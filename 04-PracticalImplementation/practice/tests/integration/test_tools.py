"""Client에서 실제 stdio 서버로 보낸 Tool 요청의 응답을 검증한다."""

import json
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from mcp import Client

from tests.integration.assertions import (
    assert_quote_result, assert_search_result, assert_tool_error,
)


pytestmark = pytest.mark.anyio


async def test_should_list_registered_tools_when_tools_are_requested(
    mcp_client: Client,
) -> None:
    """
    Given: 실제 앱 서버에 stdio로 연결한 MCP Client.
    When: tools/list를 요청한다.
    Then: 재고·검색·견적 도구와 각 도구의 필수·선택 인자 및 입력 제약을 받는다.
    """
    result = await mcp_client.list_tools()
    tools = {tool.name: tool for tool in result.tools}
    assert set(tools) == {"check_stock", "search_products", "calculate_quote"}
    assert len(result.tools) == 3
    schema = tools["check_stock"].input_schema
    assert set(schema["required"]) == {"product_id", "quantity"}
    for field in ("product_id", "quantity"):
        assert schema["properties"][field]["type"] == "integer"
        assert schema["properties"][field]["minimum"] == 1
    search_schema = tools["search_products"].input_schema
    assert search_schema["required"] == ["category"]
    assert search_schema["properties"]["category"]["type"] == "string"
    assert search_schema["properties"]["category"]["minLength"] == 1
    assert search_schema["properties"]["keyword"]["type"] == "string"
    assert search_schema["properties"]["keyword"]["default"] == ""
    quote_schema = tools["calculate_quote"].input_schema
    assert set(quote_schema["required"]) == {"product_id", "quantity", "budget"}
    for field in ("product_id", "quantity"):
        assert quote_schema["properties"][field]["type"] == "integer"
        assert quote_schema["properties"][field]["minimum"] == 1
    budget_schema = quote_schema["properties"]["budget"]
    assert budget_schema["multipleOf"] == 0.01
    budget_types = {branch["type"] for branch in budget_schema["anyOf"]}
    assert budget_types == {"integer", "number"}
    for branch in budget_schema["anyOf"]:
        if branch["type"] == "integer":
            assert branch["minimum"] == 1
        else:
            assert branch["exclusiveMinimum"] == 0


async def test_should_return_stock_result_when_stock_is_requested(
    mcp_client: Client,
) -> None:
    """
    Given: 실제 DummyJSON에 접근하는 앱 서버와 상품 ID 1·수량 1.
    When: Client가 check_stock의 tools/call을 요청한다.
    Then: 성공 필드·재고 판단식·요청 사이의 UTC 확인 시각을 받는다.
    """
    before = datetime.now(UTC)
    response = await mcp_client.call_tool(
        "check_stock", {"product_id": 1, "quantity": 1}
    )
    after = datetime.now(UTC)
    assert response.is_error is False
    result = response.structured_content
    assert isinstance(result, dict)
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


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param(field, value, id=f"{field}-{label}")
        for field in ("product_id", "quantity")
        for label, value in (
            ("zero", 0), ("negative", -1), ("string", "1"),
            ("decimal", 1.5), ("boolean", True), ("missing", None),
        )
    ],
)
async def test_should_return_tool_error_when_stock_arguments_are_invalid(
    mcp_client: Client, field: str, value: object,
) -> None:
    """
    Given: product_id 또는 quantity가 범위·타입을 벗어나거나 누락된 요청.
    When: Client가 check_stock의 tools/call을 요청한다.
    Then: is_error=True와 해당 인자의 오류 설명을 받고 성공 데이터는 없다.
    """
    arguments: dict[str, object] = {"product_id": 1, "quantity": 1}
    if value is None:
        del arguments[field]
    else:
        arguments[field] = value
    response = await mcp_client.call_tool("check_stock", arguments)
    text = assert_tool_error(response)
    assert field in text


async def test_should_return_tool_error_when_product_is_not_found(
    mcp_client: Client,
) -> None:
    """
    Given: 실제 DummyJSON에 없는 상품 ID 2147483647과 수량 1.
    When: Client가 check_stock의 tools/call을 요청한다.
    Then: PRODUCT_NOT_FOUND·retryable=False 오류 결과를 받고 성공 데이터는 없다.
    """
    response = await mcp_client.call_tool(
        "check_stock", {"product_id": 2147483647, "quantity": 1}
    )
    text = assert_tool_error(response)
    error = json.loads(text[text.index("{"):])
    assert error["code"] == "PRODUCT_NOT_FOUND"
    assert error["retryable"] is False
    assert "2147483647" in error["message"]
    assert "HTTP 404" in error["message"]


async def test_should_return_search_candidates_when_category_is_requested(
    mcp_client: Client, dummyjson_category_products: list[dict[str, Any]],
) -> None:
    """
    Given: 실제 stdio 서버와 smartphones 카테고리의 현재 전체 원본.
    When: keyword를 생략한 search_products의 tools/call을 요청한다.
    Then: is_error=False이며 전체 후보 목록·순서·count가 원본과 일치한다.
    """
    response = await mcp_client.call_tool(
        "search_products", {"category": "smartphones"},
    )
    assert response.is_error is False
    assert_search_result(response.structured_content, dummyjson_category_products)


async def test_should_return_matching_candidates_when_keyword_is_supplied(
    mcp_client: Client, dummyjson_category_products: list[dict[str, Any]],
) -> None:
    """
    Given: 실제 smartphones 원본과 공백·대문자가 포함된 검색어 '  PHONE  '.
    When: Client가 해당 검색어로 search_products의 tools/call을 요청한다.
    Then: 공백·대소문자를 무시한 상품명 또는 설명의 일치 후보만 순서대로 받는다.
    """
    keyword = "  PHONE  "
    response = await mcp_client.call_tool(
        "search_products", {"category": "smartphones", "keyword": keyword},
    )
    assert response.is_error is False
    assert_search_result(
        response.structured_content, dummyjson_category_products, keyword=keyword,
    )
    result = response.structured_content
    assert isinstance(result, dict)
    assert result["count"] > 0


async def test_should_return_empty_candidates_when_keyword_matches_no_products(
    mcp_client: Client, dummyjson_category_products: list[dict[str, Any]],
) -> None:
    """
    Given: 현재 원본의 상품명·설명에 없는 검색어와 실제 stdio 서버.
    When: Client가 search_products의 tools/call을 요청한다.
    Then: is_error=False인 정상 빈 목록과 count=0을 받는다.
    """
    keyword = "no-matching-product-01a115bc-6932-74a2-b04f-eb164c8eee1e"
    assert all(
        keyword not in product["title"].casefold()
        and keyword not in product["description"].casefold()
        for product in dummyjson_category_products
    ), "테스트 검색어가 원본과 일치하여 빈 결과 시나리오를 검증할 수 없습니다."
    response = await mcp_client.call_tool(
        "search_products", {"category": "smartphones", "keyword": keyword},
    )
    assert response.is_error is False
    assert_search_result(
        response.structured_content, dummyjson_category_products, keyword=keyword,
    )


@pytest.mark.parametrize("budget", [2000, 0.01], ids=["regular", "below-shipping"])
async def test_should_return_quote_result_when_quote_is_requested(
    mcp_client: Client, dummyjson_product: dict[str, Any], budget: int | float,
) -> None:
    """
    Given: 실제 상품 ID 1의 원본과 수량 3·예산 2000 또는 0.01.
    When: Client가 calculate_quote의 tools/call을 요청한다.
    Then: 원본 기반 계산 금액·예산 판단·UTC 안내기간을 받고 예산 초과도 성공이다.
    """
    before = datetime.now(UTC)
    response = await mcp_client.call_tool(
        "calculate_quote", {"product_id": 1, "quantity": 3, "budget": budget},
    )
    after = datetime.now(UTC)
    assert response.is_error is False
    assert_quote_result(
        response.structured_content, dummyjson_product, quantity=3, budget=budget,
        before=before, after=after,
    )


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        pytest.param({}, "category", id="missing-category"),
        pytest.param({"category": "   "}, "category", id="blank-category"),
        pytest.param({"category": 3}, "category", id="number-category"),
        pytest.param(
            {"category": "smartphones", "keyword": 3}, "keyword",
            id="number-keyword",
        ),
    ],
)
async def test_should_return_tool_error_when_search_arguments_are_invalid(
    mcp_client: Client, arguments: dict[str, object], field: str,
) -> None:
    """
    Given: 누락·공백·잘못된 타입의 category 또는 잘못된 타입의 keyword.
    When: Client가 search_products의 tools/call을 요청한다.
    Then: SDK 입력 오류 설명과 is_error=True를 받고 성공 데이터는 없다.
    """
    response = await mcp_client.call_tool("search_products", arguments)
    text = assert_tool_error(response)
    assert field in text
    assert "validation error" in text.lower()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("product_id", 0, id="zero-product-id"),
        pytest.param("product_id", "1", id="string-product-id"),
        pytest.param("quantity", 0, id="zero-quantity"),
        pytest.param("quantity", True, id="boolean-quantity"),
        pytest.param("budget", "2000", id="string-budget"),
        pytest.param("budget", 1.001, id="third-decimal-budget"),
        pytest.param("budget", None, id="missing-budget"),
    ],
)
async def test_should_return_tool_error_when_quote_arguments_are_invalid(
    mcp_client: Client, field: str, value: object,
) -> None:
    """
    Given: 범위·타입을 벗어난 ID·수량, 문자열·소수 셋째 자리·누락 예산.
    When: Client가 calculate_quote의 tools/call을 요청한다.
    Then: SDK 입력 오류 설명과 is_error=True를 받고 성공 데이터는 없다.
    """
    arguments: dict[str, object] = {"product_id": 1, "quantity": 3, "budget": 2000}
    if value is None:
        del arguments[field]
    else:
        arguments[field] = value
    response = await mcp_client.call_tool("calculate_quote", arguments)
    text = assert_tool_error(response)
    assert field in text
    assert "validation error" in text.lower()


async def test_should_return_tool_error_when_category_is_unknown(
    mcp_client: Client,
) -> None:
    """
    Given: DummyJSON에 존재하지 않는 카테고리 식별자.
    When: Client가 search_products의 tools/call을 요청한다.
    Then: INVALID_INPUT·retryable=False 오류 설명을 받고 성공 데이터는 없다.
    """
    category = "unknown-category-01a115bc"
    response = await mcp_client.call_tool("search_products", {"category": category})
    text = assert_tool_error(response)
    error = json.loads(text[text.index("{"):])
    assert set(error) == {"code", "message", "retryable"}
    assert error["code"] == "INVALID_INPUT"
    assert error["retryable"] is False
    assert category in error["message"]


async def test_should_return_tool_error_when_quote_product_is_not_found(
    mcp_client: Client,
) -> None:
    """
    Given: 실제 DummyJSON에 없는 상품 ID 2147483647과 수량 3·예산 2000.
    When: Client가 calculate_quote의 tools/call을 요청한다.
    Then: PRODUCT_NOT_FOUND·retryable=False 오류 설명을 받고 성공 데이터는 없다.
    """
    response = await mcp_client.call_tool(
        "calculate_quote",
        {"product_id": 2147483647, "quantity": 3, "budget": 2000},
    )
    text = assert_tool_error(response)
    error = json.loads(text[text.index("{"):])
    assert set(error) == {"code", "message", "retryable"}
    assert error["code"] == "PRODUCT_NOT_FOUND"
    assert error["retryable"] is False
    assert "2147483647" in error["message"]
    assert "HTTP 404" in error["message"]

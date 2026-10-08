"""Client에서 실제 stdio 서버로 보낸 Tool 요청의 응답을 검증한다."""

import json
from datetime import UTC, datetime, timedelta

import pytest
from mcp import Client


pytestmark = pytest.mark.anyio


async def test_should_list_stock_tool_when_tools_are_requested(
    mcp_client: Client,
) -> None:
    """
    Given: 실제 앱 서버에 stdio로 연결한 MCP Client.
    When: tools/list를 요청한다.
    Then: check_stock 하나와 필수 정수 입력 2개·최솟값 1을 받는다.
    """
    result = await mcp_client.list_tools()
    assert [tool.name for tool in result.tools] == ["check_stock"]
    schema = result.tools[0].input_schema
    assert set(schema["required"]) == {"product_id", "quantity"}
    for field in ("product_id", "quantity"):
        assert schema["properties"][field]["type"] == "integer"
        assert schema["properties"][field]["minimum"] == 1


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
    assert response.is_error is True
    assert response.structured_content is None
    text = "\n".join(
        block.text for block in response.content if block.type == "text"
    )
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
    assert response.is_error is True
    assert response.structured_content is None
    text = "\n".join(
        block.text for block in response.content if block.type == "text"
    )
    error = json.loads(text[text.index("{"):])
    assert error["code"] == "PRODUCT_NOT_FOUND"
    assert error["retryable"] is False
    assert "2147483647" in error["message"]
    assert "HTTP 404" in error["message"]

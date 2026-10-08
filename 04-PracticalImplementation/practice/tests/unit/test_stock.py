"""check_stock의 입력 제약, 재고 결과와 예상 오류를 외부 통신 없이 검증한다."""

import json
from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock

import pytest
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.mcpserver.tools.base import Tool
from pydantic import TypeAdapter

from app.tools import stock as stock_module
from app.tools.stock import PositiveInteger, build_stock_result
from tests.fixtures.stock_http import ERROR_CASES, mock_stock_http


@pytest.mark.parametrize("value", [1, 7])
def test_should_accept_value_when_input_is_positive_integer(value: int) -> None:
    """
    Given: 양의 정수 1 또는 7.
    When: 공통 입력 타입 PositiveInteger를 TypeAdapter로 검증한다.
    Then: 검증 오류 없이 입력값을 그대로 반환한다.
    """
    assert TypeAdapter(PositiveInteger).validate_python(value) == value


INVALID_INPUT_CASES = [
    pytest.param(
        {"product_id": 1, "quantity": 1, field: value}, field,
        id=f"{field}-{label}",
    )
    for field in ("product_id", "quantity")
    for label, value in (
        ("zero", 0), ("negative", -1), ("string", "3"),
        ("integer-float", 3.0), ("fraction", 3.5),
        ("true", True), ("false", False), ("null", None), ("empty", ""),
    )
] + [
    pytest.param({"quantity": 1}, "product_id", id="missing-product-id"),
    pytest.param({"product_id": 1}, "quantity", id="missing-quantity"),
]


@pytest.mark.anyio
@pytest.mark.parametrize(("arguments", "invalid_field"), INVALID_INPUT_CASES)
async def test_check_stock_invalid_arguments_raises_tool_error(
    arguments: dict[str, object], invalid_field: str,
) -> None:
    """
    Given: 잘못된 자료형·범위 또는 필수 인자가 누락된 요청.
    When: check_stock으로 생성한 SDK Tool에 원본 인자를 전달하여 실행한다.
    Then: 해당 인자의 ToolError가 발생하고 HTTP 요청은 0회다.
    """
    tool = Tool.from_function(stock_module.check_stock)
    requests = []
    with mock_stock_http("stock_five", requests.append):
        with pytest.raises(ToolError, match=invalid_field):
            await tool.run(arguments, context=Mock())
    assert requests == []


@pytest.mark.parametrize(
    ("stock", "quantity", "expected_in_stock"),
    [
        pytest.param(5, 1, True, id="sufficient"),
        pytest.param(5, 5, True, id="equal"),
        pytest.param(5, 6, False, id="insufficient"),
        pytest.param(0, 1, False, id="zero-stock"),
    ],
)
def test_build_stock_result_stock_boundaries_returns_expected_fields(
    stock: int, quantity: int, expected_in_stock: bool
) -> None:
    """
    Given: 재고 충분·동일·부족·0 조건과 고정된 UTC 확인 시각.
    When: build_stock_result로 성공 결과를 구성한다.
    Then: 재고 판단과 상품 ID·수량·재고·시각을 포함한 전체 필드가 기대값과 같다.
    """
    checked_at = datetime(2026, 10, 8, 0, 0, tzinfo=UTC)
    result = build_stock_result(7, quantity, stock, checked_at)
    assert result == {
        "status": "ok",
        "product_id": 7,
        "requested_quantity": quantity,
        "stock": stock,
        "in_stock": expected_in_stock,
        "checked_at": "2026-10-08T00:00:00+00:00",
    }


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("scenario", "quantity", "expected_stock", "expected_in_stock"),
    [
        ("stock_five", 1, 5, True),
        ("stock_five", 5, 5, True),
        ("stock_five", 6, 5, False),
        ("stock_zero", 1, 0, False),
    ],
)
async def test_check_stock_valid_response_returns_stock_result(
    scenario: str, quantity: int, expected_stock: int, expected_in_stock: bool
) -> None:
    """
    Given: 재고가 5 또는 0인 정상 상품 응답과 네 가지 재고·수량 조건.
    When: 모의 HTTP 응답을 사용하여 check_stock을 실행한다.
    Then: status는 ok이고 재고·요청 수량·in_stock이 기대값과 같다.
    """
    with mock_stock_http(scenario):
        result = await stock_module.check_stock(1, quantity)

    assert result["status"] == "ok"
    assert result["stock"] == expected_stock
    assert result["in_stock"] is expected_in_stock
    assert result["requested_quantity"] == quantity


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("scenario", "expected_code", "retryable", "message_fragment"),
    ERROR_CASES,
    ids=[case[0] for case in ERROR_CASES],
)
async def test_check_stock_lookup_failure_raises_tool_error(
    scenario: str, expected_code: str, retryable: bool, message_fragment: str
) -> None:
    """
    Given: HTTP 오류·통신 예외·잘못된 상품 응답 중 하나인 실패 시나리오.
    When: 모의 HTTP 응답 또는 예외를 사용하여 check_stock을 실행한다.
    Then: ToolError의 코드·메시지·재시도 정보가 기대값과 같고 상품 조회는 1회다.
    """
    requests = []
    with mock_stock_http(scenario, requests.append):
        with pytest.raises(ToolError) as raised:
            await stock_module.check_stock(1, 1)

    error = json.loads(str(raised.value))
    assert set(error) == {"code", "message", "retryable"}
    assert error["code"] == expected_code
    assert error["retryable"] is retryable
    assert message_fragment in error["message"]
    # 재시도 가능한 오류도 이번 단위에서는 요청을 한 번만 수행한다.
    assert len(requests) == 1
    assert str(requests[0].url) == "https://dummyjson.com/products/1"


def test_build_stock_result_non_utc_time_returns_utc_timestamp() -> None:
    """
    Given: UTC+9 시간대의 확인 시각.
    When: build_stock_result로 성공 결과를 구성한다.
    Then: checked_at은 같은 순간을 나타내는 UTC ISO 8601 문자열이다.
    """
    checked_at = datetime(
        2026, 10, 8, 9, 0, tzinfo=timezone(timedelta(hours=9))
    )
    result = build_stock_result(7, 1, 5, checked_at)
    assert result["checked_at"] == "2026-10-08T00:00:00+00:00"


@pytest.mark.anyio
async def test_check_stock_successful_lookup_returns_expected_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Given: 조회 재고 5와 현재 시각을 반환하는 모의 객체, 상품 ID 7과 수량 6.
    When: 조회 함수와 시각을 대체한 check_stock을 실행한다.
    Then: 상품 ID 7로 한 번 조회하고 모든 성공 필드와 재고 부족 판단이 기대값과 같다.
    """
    lookup = AsyncMock(return_value=5)
    clock = Mock()
    clock.now.return_value = datetime(2026, 10, 8, 0, 0, tzinfo=UTC)
    monkeypatch.setattr(stock_module, "fetch_product_stock", lookup)
    monkeypatch.setattr(stock_module, "datetime", clock)

    result = await stock_module.check_stock(product_id=7, quantity=6)

    lookup.assert_awaited_once_with(7)
    assert result == {
        "status": "ok",
        "product_id": 7,
        "requested_quantity": 6,
        "stock": 5,
        "in_stock": False,
        "checked_at": "2026-10-08T00:00:00+00:00",
    }

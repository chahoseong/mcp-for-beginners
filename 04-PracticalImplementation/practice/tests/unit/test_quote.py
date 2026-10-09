"""견적 계산 순서·단계별 반올림·예산 경계·정책 원본 반영을 검증한다."""

import json
from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_EVEN, Decimal
from unittest.mock import Mock

import httpx
import pytest
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.mcpserver.tools.base import Tool

from app import policy
from app.tools import quote as quote_module
from app.tools.quote import QuoteAmounts, calculate_quote, calculate_quote_amounts
from tests.fixtures.quote_http import mock_quote_http


def test_calculate_quote_amounts_candidate_a_returns_expected_amounts() -> None:
    """
    Given: 후보 A의 단가 600, 수량 3, 할인율 10%, 예산 2000과 v1 정책.
    When: calculate_quote_amounts를 실행한다.
    Then: 할인 180·상품 금액 1620·배송비 20·세금 162·총액 1802와 예산 충족을 반환한다.
    """
    result = calculate_quote_amounts(
        unit_price=Decimal("600"), discount_percentage=Decimal("10"),
        quantity=3, budget=Decimal("2000"),
    )
    assert result == QuoteAmounts(
        discount_amount=Decimal("180.00"), subtotal=Decimal("1620.00"),
        shipping_fee=Decimal("20.00"), tax=Decimal("162.00"),
        total=Decimal("1802.00"), within_budget=True,
    )


@pytest.mark.parametrize(
    ("budget", "expected_within_budget"),
    [
        pytest.param("1802", True, id="equal-to-total"),
        pytest.param("1801.99", False, id="one-cent-below-total"),
    ],
)
def test_calculate_quote_amounts_budget_boundary_returns_expected_budget_result(
    budget: str, expected_within_budget: bool,
) -> None:
    """
    Given: 최종 금액 1802인 후보 A와 총액과 같거나 0.01 부족한 예산.
    When: calculate_quote_amounts로 계산하고 예산과 비교한다.
    Then: 총액은 그대로이며 동일 예산은 True, 0.01 부족한 예산은 False다.
    """
    result = calculate_quote_amounts(
        unit_price=Decimal("600"), discount_percentage=Decimal("10"),
        quantity=3, budget=Decimal(budget),
    )
    assert result.total == Decimal("1802.00")
    assert result.within_budget is expected_within_budget


def test_calculate_quote_amounts_fractional_price_returns_stepwise_rounded_amounts() -> None:
    """
    Given: 단가 0.335, 수량 3, 할인율 50%, 예산 30.
    When: calculate_quote_amounts로 금액을 단계별 반올림한다.
    Then: 단가를 먼저 반올림하지 않고 1.005를 1.01로 만든 뒤 할인을 계산한다.
          할인 0.51·상품 금액 0.50·세금 0.05·총액 20.55를 반환한다.
    """
    result = calculate_quote_amounts(
        unit_price=Decimal("0.335"), discount_percentage=Decimal("50"),
        quantity=3, budget=Decimal("30"),
    )
    assert result == QuoteAmounts(
        discount_amount=Decimal("0.51"), subtotal=Decimal("0.50"),
        shipping_fee=Decimal("20.00"), tax=Decimal("0.05"),
        total=Decimal("20.55"), within_budget=True,
    )


def test_calculate_quote_amounts_half_cent_tax_returns_half_up_rounded_tax() -> None:
    """
    Given: 단가 0.05, 수량 1, 할인율 0%, 예산 20.06.
    When: calculate_quote_amounts로 세금과 총액을 계산한다.
    Then: 세금 0.005를 HALF_UP으로 0.01로 반올림하여 총액 20.06을 반환한다.
          배송비에는 세금을 적용하지 않으며 총액과 같은 예산을 충족한다.
    """
    result = calculate_quote_amounts(
        unit_price=Decimal("0.05"), discount_percentage=Decimal("0"),
        quantity=1, budget=Decimal("20.06"),
    )
    assert result == QuoteAmounts(
        discount_amount=Decimal("0.00"), subtotal=Decimal("0.05"),
        shipping_fee=Decimal("20.00"), tax=Decimal("0.01"),
        total=Decimal("20.06"), within_budget=True,
    )


@pytest.mark.parametrize(
    ("unit_price", "discount_percentage", "expected_discount"),
    [
        pytest.param("0", "10", "0.00", id="zero-price"),
        pytest.param("600", "100", "1800.00", id="full-discount"),
    ],
)
def test_calculate_quote_amounts_zero_subtotal_returns_shipping_only_total(
    unit_price: str, discount_percentage: str, expected_discount: str,
) -> None:
    """
    Given: 단가가 0이거나 할인율이 100%인 상품, 수량 3, 예산 10.
    When: calculate_quote_amounts를 실행한다.
    Then: 상품 금액과 세금은 0이지만 배송비 20은 부과하며 예산 초과를 정상 반환한다.
    """
    result = calculate_quote_amounts(
        unit_price=Decimal(unit_price),
        discount_percentage=Decimal(discount_percentage),
        quantity=3, budget=Decimal("10"),
    )
    assert result == QuoteAmounts(
        discount_amount=Decimal(expected_discount), subtotal=Decimal("0.00"),
        shipping_fee=Decimal("20.00"), tax=Decimal("0.00"),
        total=Decimal("20.00"), within_budget=False,
    )


@pytest.mark.parametrize(
    ("quantity", "expected_subtotal", "expected_tax", "expected_total"),
    [(1, "600.00", "60.00", "680.00"), (3, "1800.00", "180.00", "2000.00")],
)
def test_calculate_quote_amounts_no_discount_returns_single_shipping_charge(
    quantity: int, expected_subtotal: str, expected_tax: str, expected_total: str,
) -> None:
    """
    Given: 단가 600, 할인율 0%, 수량 1 또는 3, 예산 2000.
    When: calculate_quote_amounts를 실행한다.
    Then: 할인은 0이며 수량에 따른 상품 금액·세금과 후보당 배송비 20을 반환한다.
    """
    result = calculate_quote_amounts(
        unit_price=Decimal("600"), discount_percentage=Decimal("0"),
        quantity=quantity, budget=Decimal("2000"),
    )
    assert result == QuoteAmounts(
        discount_amount=Decimal("0.00"), subtotal=Decimal(expected_subtotal),
        shipping_fee=Decimal("20.00"), tax=Decimal(expected_tax),
        total=Decimal(expected_total), within_budget=True,
    )


def test_calculate_quote_amounts_updated_policy_returns_updated_amounts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Given: 정책 원본의 배송비를 35.50, 세율을 7.5%로 변경한 후보 A.
    When: calculate_quote_amounts를 실행한다.
    Then: 변경한 원본을 읽어 배송비 35.50·세금 121.50·총액 1777을 반환한다.
    """
    monkeypatch.setattr(policy, "SHIPPING_FEE", Decimal("35.50"))
    monkeypatch.setattr(policy, "TAX_RATE", Decimal("0.075"))
    result = calculate_quote_amounts(
        unit_price=Decimal("600"), discount_percentage=Decimal("10"),
        quantity=3, budget=Decimal("2000"),
    )
    assert result == QuoteAmounts(
        discount_amount=Decimal("180.00"), subtotal=Decimal("1620.00"),
        shipping_fee=Decimal("35.50"), tax=Decimal("121.50"),
        total=Decimal("1777.00"), within_budget=True,
    )


def test_calculate_quote_amounts_updated_decimal_places_returns_policy_precision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Given: 정책 원본의 금액 소수 자릿수를 3으로 변경하고 단가 0.335·수량 3·할인율 50%.
    When: calculate_quote_amounts를 실행한다.
    Then: 할인 0.503·상품 금액 0.502·세금 0.050·총액 20.552를 반환한다.
    """
    monkeypatch.setattr(policy, "MONEY_DECIMAL_PLACES", 3)
    result = calculate_quote_amounts(
        unit_price=Decimal("0.335"), discount_percentage=Decimal("50"),
        quantity=3, budget=Decimal("30"),
    )
    assert result == QuoteAmounts(
        discount_amount=Decimal("0.503"), subtotal=Decimal("0.502"),
        shipping_fee=Decimal("20.00"), tax=Decimal("0.050"),
        total=Decimal("20.552"), within_budget=True,
    )


def test_calculate_quote_amounts_updated_rounding_returns_policy_rounded_tax(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Given: 정책 원본의 반올림 방식을 HALF_EVEN으로 변경한 단가 0.05·수량 1 상품.
    When: calculate_quote_amounts를 실행한다.
    Then: 변경한 방식을 읽어 세금 0.005를 0.00으로 반올림하고 총액 20.05를 반환한다.
    """
    monkeypatch.setattr(policy, "ROUNDING", ROUND_HALF_EVEN)
    result = calculate_quote_amounts(
        unit_price=Decimal("0.05"), discount_percentage=Decimal("0"),
        quantity=1, budget=Decimal("30"),
    )
    assert result.tax == Decimal("0.00")
    assert result.total == Decimal("20.05")


def test_calculate_quote_amounts_valid_inputs_returns_decimal_amounts() -> None:
    """
    Given: Decimal로 표현한 정상 단가·할인율·예산과 정수 수량.
    When: calculate_quote_amounts를 실행한다.
    Then: 금액 5개 필드는 모두 Decimal이고 within_budget은 bool이다.
    """
    result = calculate_quote_amounts(
        unit_price=Decimal("600"), discount_percentage=Decimal("10"),
        quantity=3, budget=Decimal("2000"),
    )
    for amount in (
        result.discount_amount, result.subtotal, result.shipping_fee,
        result.tax, result.total,
    ):
        assert isinstance(amount, Decimal)
    assert type(result.within_budget) is bool


def _quote_product() -> dict[str, object]:
    """설계의 후보 A를 원본 API 필드로 표현한다."""
    return {"id": 1, "title": "Candidate A", "price": 600, "discountPercentage": 10}


def _response(payload: object) -> httpx.Response:
    """null·NaN 같은 잘못된 원본도 검증할 수 있게 JSON 본문을 구성한다."""
    return httpx.Response(200, content=json.dumps(payload).encode())


@pytest.mark.anyio
async def test_calculate_quote_candidate_a_returns_complete_quote(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Given: 후보 A의 정상 모의 상품 응답과 UTC 생성 시각 2026-10-08 00:00.
    When: 상품 ID 1·수량 3·예산 2000으로 calculate_quote를 실행한다.
    Then: 총액 1802와 상품·금액·예산·정책·생성 시각·7일 후 종료 시각을 반환한다.
    """
    clock = Mock()
    clock.now.return_value = datetime(2026, 10, 8, tzinfo=UTC)
    monkeypatch.setattr(quote_module, "datetime", clock)
    with mock_quote_http(lambda request: _response(_quote_product())):
        result = await calculate_quote(1, 3, 2000)
    assert result == {
        "status": "ok", "product_id": 1, "name": "Candidate A", "quantity": 3,
        "currency": "USD", "unit_price": 600, "discount_percentage": 10,
        "discount_amount": 180.0, "subtotal": 1620.0, "shipping_fee": 20.0,
        "tax": 162.0, "total": 1802.0, "within_budget": True,
        "policy_version": "v1", "generated_at": "2026-10-08T00:00:00+00:00",
        "valid_until": "2026-10-15T00:00:00+00:00",
    }


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("budget", "within_budget"), [(1802, True), (1802.0, True), (1801.99, False)],
)
async def test_calculate_quote_budget_boundary_returns_expected_budget_result(
    budget: int | float, within_budget: bool,
) -> None:
    """
    Given: 모의 후보 A와 정수·실수로 표현한 같은 예산 또는 0.01 부족한 예산.
    When: 등록에 사용하는 SDK Tool로 calculate_quote를 실행한다.
    Then: 정상 견적 총액 1802를 반환하며 같으면 포함, 부족하면 제외한다.
    """
    tool = Tool.from_function(calculate_quote)
    with mock_quote_http(lambda request: _response(_quote_product())):
        result = await tool.run(
            {"product_id": 1, "quantity": 3, "budget": budget}, context=Mock(),
        )
    assert result["status"] == "ok"
    assert result["total"] == 1802.0
    assert result["within_budget"] is within_budget


@pytest.mark.anyio
@pytest.mark.parametrize("discount", [50, 50.123])
async def test_calculate_quote_fractional_source_returns_original_precision(
    discount: int | float,
) -> None:
    """
    Given: 원본 단가 0.335와 할인율 50 또는 50.123인 모의 상품.
    When: 수량 3·예산 30으로 calculate_quote를 실행한다.
    Then: 원본 단가·할인율은 유지하며 할인 0.51·상품 금액 0.50·세금 0.05·총액 20.55다.
    """
    product = _quote_product()
    product.update(price=0.335, discountPercentage=discount)
    with mock_quote_http(lambda request: _response(product)):
        result = await calculate_quote(1, 3, 30)
    assert result["unit_price"] == 0.335
    assert result["discount_percentage"] == discount
    assert result["discount_amount"] == 0.51
    assert result["subtotal"] == 0.50
    assert result["tax"] == 0.05
    assert result["total"] == 20.55
    assert result["within_budget"] is True


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("price", "discount", "total"),
    [(0, 0, 20.0), (600.0, 100.0, 20.0), (600, 0, 2000.0)],
)
async def test_calculate_quote_source_boundaries_returns_expected_total(
    price: int | float, discount: int | float, total: float,
) -> None:
    """
    Given: 단가 0·할인율 100%·할인율 0%와 정수·실수 원본 숫자 조건.
    When: 수량 3·예산 2000으로 calculate_quote를 실행한다.
    Then: 정상 결과와 각 조건의 기대 총액을 반환한다.
    """
    product = _quote_product()
    product.update(price=price, discountPercentage=discount)
    with mock_quote_http(lambda request: _response(product)):
        result = await calculate_quote(1, 3, 2000)
    assert result["status"] == "ok"
    assert result["total"] == total
    assert result["within_budget"] is True


@pytest.mark.anyio
async def test_calculate_quote_updated_policy_returns_policy_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Given: 버전 v2·통화 EUR·배송비 35.50·세율 7.5%·안내기간 3일인 정책 원본.
    When: 모의 후보 A로 calculate_quote를 실행한다.
    Then: 정책의 금액·통화·버전을 반영하고 종료 시각은 생성 시각에서 3일 뒤다.
    """
    monkeypatch.setattr(policy, "POLICY_VERSION", "v2")
    monkeypatch.setattr(policy, "CURRENCY", "EUR")
    monkeypatch.setattr(policy, "SHIPPING_FEE", Decimal("35.50"))
    monkeypatch.setattr(policy, "TAX_RATE", Decimal("0.075"))
    monkeypatch.setattr(policy, "VALIDITY_DAYS", 3)
    with mock_quote_http(lambda request: _response(_quote_product())):
        result = await calculate_quote(1, 3, 2000)
    assert result["currency"] == "EUR"
    assert result["policy_version"] == "v2"
    assert result["shipping_fee"] == 35.50
    assert result["tax"] == 121.50
    assert result["total"] == 1777.00
    start = datetime.fromisoformat(result["generated_at"])
    end = datetime.fromisoformat(result["valid_until"])
    assert start.utcoffset() == timedelta(0)
    assert end - start == timedelta(days=3)


@pytest.mark.anyio
async def test_calculate_quote_successful_lookup_sends_expected_http_request() -> None:
    """
    Given: 정상 모의 상품 응답.
    When: calculate_quote를 실행한다.
    Then: 상품 ID의 정확한 GET URL로 한 번 요청하며 HTTPX의 제한 시간은 각각 10초다.
    """
    with mock_quote_http(lambda request: _response(_quote_product())) as requests:
        await calculate_quote(1, 3, 2000)
    assert len(requests) == 1
    assert requests[0].method == "GET"
    assert str(requests[0].url) == "https://dummyjson.com/products/1"
    assert requests[0].extensions["timeout"] == {
        "connect": 10.0, "read": 10.0, "write": 10.0, "pool": 10.0,
    }


VALID_QUOTE_ARGUMENTS = {"product_id": 1, "quantity": 3, "budget": 2000}
INVALID_QUOTE_INPUTS = [
    pytest.param(
        {**VALID_QUOTE_ARGUMENTS, field: value}, field,
        id=f"{field}-{label}",
    )
    for field in ("product_id", "quantity")
    for label, value in (
        ("zero", 0), ("negative", -1), ("string", "3"), ("float", 3.0),
        ("fraction", 3.5), ("boolean", True), ("null", None),
    )
] + [
    pytest.param(
        {**VALID_QUOTE_ARGUMENTS, "budget": value}, "budget", id=f"budget-{label}",
    )
    for label, value in (
        ("zero", 0), ("negative", -1), ("string", "2000"), ("boolean", True),
        ("null", None), ("list", []), ("object", {}), ("fraction", 1.001),
        ("nan", float("nan")), ("infinity", float("inf")),
        ("negative-infinity", float("-inf")),
    )
] + [
    pytest.param(
        {key: value for key, value in VALID_QUOTE_ARGUMENTS.items() if key != field},
        field, id=f"missing-{field}",
    )
    for field in ("product_id", "quantity", "budget")
]


@pytest.mark.anyio
@pytest.mark.parametrize(("arguments", "field"), INVALID_QUOTE_INPUTS)
async def test_calculate_quote_invalid_arguments_raises_tool_error(
    arguments: dict[str, object], field: str,
) -> None:
    """
    Given: 타입·범위·예산 소수 자릿수·필수 인자 조건을 위반한 입력.
    When: SDK Tool로 calculate_quote를 실행한다.
    Then: 입력 필드의 ToolError가 발생하고 HTTP 요청은 보내지 않는다.
    """
    tool = Tool.from_function(calculate_quote)
    with mock_quote_http(lambda request: _response(_quote_product())) as requests:
        with pytest.raises(ToolError, match=field):
            await tool.run(arguments, context=Mock())
    assert requests == []


INVALID_PRODUCT_CASES = [
    pytest.param(field, value, id=f"{field}-{label}")
    for field in ("price", "discountPercentage")
    for label, value in (
        ("negative", -1), ("string", "10"), ("boolean", True), ("null", None),
        ("nan", float("nan")), ("infinity", float("inf")), ("list", []),
    )
] + [
    pytest.param("discountPercentage", 100.01, id="discount-above-100"),
    pytest.param("id", 2, id="id-mismatch"),
    pytest.param("id", "1", id="id-string"),
    pytest.param("id", True, id="id-boolean"),
    pytest.param("id", 1.0, id="id-float"),
    pytest.param("id", 0, id="id-zero"),
    pytest.param("title", "", id="name-empty"),
    pytest.param("title", "  ", id="name-blank"),
    pytest.param("title", 3, id="name-number"),
]


@pytest.mark.anyio
@pytest.mark.parametrize(("field", "value"), INVALID_PRODUCT_CASES)
async def test_calculate_quote_invalid_product_response_raises_tool_error(
    field: str, value: object,
) -> None:
    """
    Given: 가격·할인·ID·이름이 잘못된 모의 상품 응답.
    When: calculate_quote를 실행한다.
    Then: INVALID_RESPONSE의 ToolError를 발생시키며 성공 견적을 반환하지 않는다.
    """
    product = _quote_product()
    product[field] = value
    with mock_quote_http(lambda request: _response(product)):
        with pytest.raises(ToolError) as raised:
            await calculate_quote(1, 3, 2000)
    error = json.loads(str(raised.value))
    assert error["code"] == "INVALID_RESPONSE"
    assert error["retryable"] is False


@pytest.mark.anyio
@pytest.mark.parametrize("field", ["id", "title", "price", "discountPercentage"])
async def test_calculate_quote_missing_product_field_raises_tool_error(
    field: str,
) -> None:
    """
    Given: 견적에 필요한 원본 상품 필드 중 하나가 누락된 응답.
    When: calculate_quote를 실행한다.
    Then: 기본값을 추측하지 않고 INVALID_RESPONSE로 실패한다.
    """
    product = _quote_product()
    del product[field]
    with mock_quote_http(lambda request: _response(product)):
        with pytest.raises(ToolError) as raised:
            await calculate_quote(1, 3, 2000)
    assert json.loads(str(raised.value))["code"] == "INVALID_RESPONSE"


@pytest.mark.anyio
@pytest.mark.parametrize("payload", [None, [], "invalid"])
async def test_calculate_quote_non_object_response_raises_tool_error(
    payload: object,
) -> None:
    """
    Given: JSON 최상위 값이 상품 객체가 아닌 응답.
    When: calculate_quote를 실행한다.
    Then: INVALID_RESPONSE로 실패한다.
    """
    with mock_quote_http(lambda request: _response(payload)):
        with pytest.raises(ToolError) as raised:
            await calculate_quote(1, 3, 2000)
    assert json.loads(str(raised.value))["code"] == "INVALID_RESPONSE"


QUOTE_HTTP_FAILURES = [
    (404, "PRODUCT_NOT_FOUND", False), (429, "UPSTREAM_UNAVAILABLE", True),
    (500, "UPSTREAM_UNAVAILABLE", True), (503, "UPSTREAM_UNAVAILABLE", True),
    (400, "INVALID_RESPONSE", False), (302, "INVALID_RESPONSE", False),
    (httpx.ReadTimeout, "UPSTREAM_TIMEOUT", True),
    (httpx.ConnectTimeout, "UPSTREAM_TIMEOUT", True),
    (httpx.WriteTimeout, "UPSTREAM_TIMEOUT", True),
    (httpx.PoolTimeout, "UPSTREAM_TIMEOUT", True),
    (httpx.ConnectError, "UPSTREAM_UNAVAILABLE", True),
    (httpx.ReadError, "UPSTREAM_UNAVAILABLE", True),
    ("invalid-json", "INVALID_RESPONSE", False),
]


@pytest.mark.anyio
@pytest.mark.parametrize(("failure", "code", "retryable"), QUOTE_HTTP_FAILURES)
async def test_calculate_quote_lookup_failure_raises_tool_error(
    failure: object, code: str, retryable: bool,
) -> None:
    """
    Given: 상품 조회의 HTTP 오류·통신 예외·잘못된 JSON 응답.
    When: calculate_quote를 실행한다.
    Then: 앱 오류 코드·설명·재시도 정보가 담긴 ToolError를 발생시키고 재시도하지 않는다.
    """
    def handler(request: httpx.Request) -> httpx.Response:
        if isinstance(failure, type):
            raise failure("모의 통신 오류", request=request)
        if failure == "invalid-json":
            return httpx.Response(200, content=b"{invalid")
        return httpx.Response(failure, json={"error": "test"})

    with mock_quote_http(handler) as requests:
        with pytest.raises(ToolError) as raised:
            await calculate_quote(1, 3, 2000)
    error = json.loads(str(raised.value))
    assert set(error) == {"code", "message", "retryable"}
    assert error["code"] == code
    assert error["retryable"] is retryable
    assert error["message"]
    assert len(requests) == 1


INVALID_POLICY_CASES = [
    ("POLICY_VERSION", ""), ("CURRENCY", " "),
    ("SHIPPING_FEE", Decimal("-1")), ("SHIPPING_FEE", "20.00"),
    ("SHIPPING_FEE", Decimal("NaN")), ("SHIPPING_FEE", Decimal("Infinity")),
    ("SHIPPING_FEE", Decimal("20.001")),
    ("TAX_RATE", Decimal("-0.1")), ("TAX_RATE", 0.1),
    ("TAX_RATE", Decimal("Infinity")),
    ("MONEY_DECIMAL_PLACES", -1), ("MONEY_DECIMAL_PLACES", True),
    ("ROUNDING", "invalid"), ("VALIDITY_DAYS", 0), ("VALIDITY_DAYS", True),
    ("VALIDITY_DAYS", 10**10), ("DISCOUNT_FIELD", "other"),
]


@pytest.mark.anyio
@pytest.mark.parametrize(("field", "value"), INVALID_POLICY_CASES)
async def test_calculate_quote_invalid_policy_raises_tool_error(
    monkeypatch: pytest.MonkeyPatch, field: str, value: object,
) -> None:
    """
    Given: 정책 원본의 필수 값 중 하나가 타입·범위·설정에 위배된다.
    When: calculate_quote를 실행한다.
    Then: POLICY_UNAVAILABLE로 실패하고 HTTP 요청은 보내지 않는다.
    """
    monkeypatch.setattr(policy, field, value)
    with mock_quote_http(lambda request: _response(_quote_product())) as requests:
        with pytest.raises(ToolError) as raised:
            await calculate_quote(1, 3, 2000)
    error = json.loads(str(raised.value))
    assert error["code"] == "POLICY_UNAVAILABLE"
    assert error["retryable"] is False
    assert requests == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    "field", ["POLICY_VERSION", "CURRENCY", "SHIPPING_FEE", "TAX_RATE",
              "MONEY_DECIMAL_PLACES", "ROUNDING", "VALIDITY_DAYS", "DISCOUNT_FIELD"],
)
async def test_calculate_quote_missing_policy_raises_tool_error(
    monkeypatch: pytest.MonkeyPatch, field: str,
) -> None:
    """
    Given: 정책 원본의 필수 값 중 하나가 누락되어 있다.
    When: calculate_quote를 실행한다.
    Then: POLICY_UNAVAILABLE로 실패하고 HTTP 요청은 보내지 않는다.
    """
    monkeypatch.delattr(policy, field)
    with mock_quote_http(lambda request: _response(_quote_product())) as requests:
        with pytest.raises(ToolError) as raised:
            await calculate_quote(1, 3, 2000)
    error = json.loads(str(raised.value))
    assert error["code"] == "POLICY_UNAVAILABLE"
    assert error["retryable"] is False
    assert requests == []


@pytest.mark.anyio
@pytest.mark.parametrize(("price", "quantity"), [(1e308, 1), (600, 10**30)])
async def test_calculate_quote_unrepresentable_amount_raises_tool_error(
    price: int | float, quantity: int,
) -> None:
    """
    Given: 현재 Decimal 계산에서 금액을 구성할 수 없는 큰 단가 또는 수량.
    When: calculate_quote를 실행한다.
    Then: 내부 예외를 그대로 내보내지 않고 INVALID_RESPONSE의 ToolError로 전달한다.
    """
    product = _quote_product()
    product["price"] = price
    with mock_quote_http(lambda request: _response(product)):
        with pytest.raises(ToolError) as raised:
            await calculate_quote(1, quantity, 2000)
    assert json.loads(str(raised.value))["code"] == "INVALID_RESPONSE"


@pytest.mark.anyio
async def test_calculate_quote_overflowing_validity_raises_tool_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Given: 안내기간 999999999일은 timedelta로 표현되지만 실제 종료 날짜 범위를 넘는다.
    When: calculate_quote를 실행한다.
    Then: POLICY_UNAVAILABLE의 ToolError로 전달한다.
    """
    monkeypatch.setattr(policy, "VALIDITY_DAYS", 999999999)
    with mock_quote_http(lambda request: _response(_quote_product())):
        with pytest.raises(ToolError) as raised:
            await calculate_quote(1, 3, 2000)
    assert json.loads(str(raised.value))["code"] == "POLICY_UNAVAILABLE"


@pytest.mark.anyio
async def test_calculate_quote_unrepresentable_result_raises_tool_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Given: 계산 함수가 반환한 Decimal 금액이 JSON 변환 시 무한대가 되는 경우.
    When: 모의 계산 결과와 정상 상품 응답으로 calculate_quote를 실행한다.
    Then: 무한대 숫자를 반환하지 않고 INVALID_RESPONSE의 ToolError로 전달한다.
    """
    amounts = QuoteAmounts(
        discount_amount=Decimal("0"), subtotal=Decimal("1e400"),
        shipping_fee=Decimal("20"), tax=Decimal("0"), total=Decimal("1e400"),
        within_budget=False,
    )
    monkeypatch.setattr(
        quote_module, "calculate_quote_amounts", Mock(return_value=amounts),
    )
    with mock_quote_http(lambda request: _response(_quote_product())):
        with pytest.raises(ToolError) as raised:
            await calculate_quote(1, 3, 2000)
    error = json.loads(str(raised.value))
    assert error["code"] == "INVALID_RESPONSE"
    assert error["retryable"] is False

"""실제 API·MCP 경계에서 사용하는 성공 결과 계약 검사."""

from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from mcp.types import CallToolResult


def assert_search_result(
    result: object, source_products: list[dict[str, Any]], *, keyword: str = "",
) -> None:
    """현재 원본에서 선택한 후보와 반환 필드·타입·순서·개수를 비교한다."""
    assert isinstance(result, dict)
    assert set(result) == {"status", "products", "count"}
    assert result["status"] == "ok"
    assert type(result["count"]) is int
    assert isinstance(result["products"], list)
    normalized_keyword = keyword.strip().casefold()
    expected = [
        {"product_id": product["id"], "name": product["title"],
         "category": product["category"]}
        for product in source_products
        if not normalized_keyword
        or normalized_keyword in product["title"].casefold()
        or normalized_keyword in product["description"].casefold()
    ]
    assert result["products"] == expected
    for candidate in result["products"]:
        assert type(candidate["product_id"]) is int
    assert result["count"] == len(expected)


def assert_quote_result(
    result: object, source_product: dict[str, Any], *, quantity: int,
    budget: int | float, before: datetime, after: datetime,
) -> None:
    """현재 원본으로 기대 금액을 계산하고 견적 필드·UTC 안내기간을 검사한다."""
    assert isinstance(result, dict)
    assert set(result) == {
        "status", "product_id", "name", "quantity", "currency", "unit_price",
        "discount_percentage", "discount_amount", "subtotal", "shipping_fee",
        "tax", "total", "within_budget", "policy_version", "generated_at",
        "valid_until",
    }
    assert result["status"] == "ok"
    assert type(result["product_id"]) is int
    assert result["product_id"] == source_product["id"]
    assert result["name"] == source_product["title"].strip()
    assert type(result["quantity"]) is int and result["quantity"] == quantity
    assert result["currency"] == "USD"
    assert result["policy_version"] == "v1"
    for field, source_field in (
        ("unit_price", "price"), ("discount_percentage", "discountPercentage"),
    ):
        value = result[field]
        assert type(value) in (int, float)
        assert value == source_product[source_field]
    amounts: dict[str, Decimal] = {}
    for field in ("discount_amount", "subtotal", "shipping_fee", "tax", "total"):
        value = result[field]
        assert type(value) in (int, float)
        amounts[field] = Decimal(str(value))
    # 운영 계산 함수를 호출하지 않고 문서의 v1 정책과 현재 원본을 기준으로 삼는다.
    cents = Decimal("0.01")
    base = (Decimal(str(source_product["price"])) * quantity).quantize(
        cents, rounding=ROUND_HALF_UP,
    )
    discount = (
        base * Decimal(str(source_product["discountPercentage"])) / Decimal(100)
    ).quantize(cents, rounding=ROUND_HALF_UP)
    subtotal = base - discount
    tax = (subtotal * Decimal("0.10")).quantize(cents, rounding=ROUND_HALF_UP)
    shipping = Decimal("20.00")
    assert amounts == {
        "discount_amount": discount, "subtotal": subtotal,
        "shipping_fee": shipping, "tax": tax,
        "total": subtotal + shipping + tax,
    }
    assert type(result["within_budget"]) is bool
    assert result["within_budget"] is (amounts["total"] <= Decimal(str(budget)))
    assert isinstance(result["generated_at"], str)
    assert isinstance(result["valid_until"], str)
    generated_at = datetime.fromisoformat(result["generated_at"])
    valid_until = datetime.fromisoformat(result["valid_until"])
    assert generated_at.utcoffset() == timedelta(0)
    assert valid_until.utcoffset() == timedelta(0)
    assert before <= generated_at <= after
    assert valid_until - generated_at == timedelta(days=7)


def assert_tool_error(response: CallToolResult) -> str:
    """공통 Tool 실패 응답을 검사하고 시나리오별 검사에 사용할 설명을 반환한다."""
    assert response.is_error is True
    assert response.structured_content is None
    return "\n".join(
        block.text for block in response.content if block.type == "text"
    )

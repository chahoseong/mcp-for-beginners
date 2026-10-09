"""견적 계산 순서·단계별 반올림·예산 경계·정책 원본 반영을 검증한다."""

from decimal import ROUND_HALF_EVEN, Decimal

import pytest

from app import policy
from app.tools.quote import QuoteAmounts, calculate_quote_amounts


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

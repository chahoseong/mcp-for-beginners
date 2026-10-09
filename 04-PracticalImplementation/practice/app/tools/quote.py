"""검증된 상품 값과 서버 정책으로 견적 금액을 계산한다."""

from dataclasses import dataclass
from decimal import Decimal

from app import policy


@dataclass(frozen=True)
class QuoteAmounts:
    """JSON 변환 전에 Decimal로 유지하는 견적 금액 내역과 예산 판단."""

    discount_amount: Decimal
    subtotal: Decimal
    shipping_fee: Decimal
    tax: Decimal
    total: Decimal
    within_budget: bool


def calculate_quote_amounts(
    *,
    unit_price: Decimal,
    discount_percentage: Decimal,
    quantity: int,
    budget: Decimal,
) -> QuoteAmounts:
    """검증된 입력으로 계산한다. 외부 조회·입력 검증·JSON 변환은 하지 않는다."""
    money_unit = Decimal(1).scaleb(-policy.MONEY_DECIMAL_PLACES)
    base_amount = (unit_price * quantity).quantize(
        money_unit, rounding=policy.ROUNDING,
    )
    discount_amount = (base_amount * discount_percentage / Decimal(100)).quantize(
        money_unit, rounding=policy.ROUNDING,
    )
    subtotal = base_amount - discount_amount
    tax = (subtotal * policy.TAX_RATE).quantize(
        money_unit, rounding=policy.ROUNDING,
    )
    shipping_fee = policy.SHIPPING_FEE
    total = subtotal + shipping_fee + tax
    return QuoteAmounts(
        discount_amount=discount_amount,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        tax=tax,
        total=total,
        within_budget=total <= budget,
    )

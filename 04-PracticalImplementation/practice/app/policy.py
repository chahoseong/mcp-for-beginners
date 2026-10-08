"""견적 정책의 단일 원본과 Resource에 제공할 Markdown 생성."""

from decimal import ROUND_HALF_UP, Decimal


POLICY_VERSION = "v1"
CURRENCY = "USD"
SHIPPING_FEE = Decimal("20.00")
TAX_RATE = Decimal("0.10")
DISCOUNT_FIELD = "discountPercentage"
MONEY_DECIMAL_PLACES = 2
ROUNDING = ROUND_HALF_UP
VALIDITY_DAYS = 7


def render_quote_policy() -> str:
    """정책 원본의 값과 규칙을 사람이 읽을 Markdown으로 표현한다."""
    shipping_fee = f"{SHIPPING_FEE:.{MONEY_DECIMAL_PLACES}f}"
    tax_percent = format((TAX_RATE * 100).normalize(), "f")
    return f"""# 견적 정책

- 정책 버전: `{POLICY_VERSION}`
- 통화: {CURRENCY}
- 배송비: 후보 견적당 {shipping_fee} {CURRENCY}
- 세율: 할인 후 상품 금액의 {tax_percent}%
- 반올림: 금액을 소수 {MONEY_DECIMAL_PLACES}자리까지 `{ROUNDING}`으로 반올림
- 견적 안내기간: 생성 시각부터 {VALIDITY_DAYS}일

## 적용 규칙

이 정책은 승인된 과제용 가정이며 실제 상거래·세법을 나타내지 않는다.
DummyJSON의 가격 숫자를 {CURRENCY}로 해석하며 환율 변환은 하지 않는다.
상품의 `{DISCOUNT_FIELD}`를 상품 금액에 한 번 적용한다.
배송비는 요청 수량과 관계없이 후보 견적마다 한 번 부과한다.
후보별 견적은 서로 독립된 대안이므로 후보 사이의 금액이나 배송비를 합산하지 않는다.
배송비에는 세금을 적용하지 않는다.

## 계산 순서

1. 할인 전 상품 금액 = 단가 × 수량을 소수 {MONEY_DECIMAL_PLACES}자리로 반올림
2. 할인 금액 = 할인 전 상품 금액 × 할인율 / 100을 소수 {MONEY_DECIMAL_PLACES}자리로 반올림
3. 할인 후 상품 금액(`subtotal`) = 할인 전 상품 금액 − 할인 금액
4. 세금(`tax`) = (할인 후 상품 금액 × {TAX_RATE})를 소수 {MONEY_DECIMAL_PLACES}자리로 반올림
5. 최종 금액(`total`) = 할인 후 상품 금액 + {shipping_fee} + 세금
6. 예산 충족(`within_budget`) = 최종 금액이 입력 예산 이하인지

## 견적 안내기간

`generated_at`은 견적 계산 완료 시각이며 `valid_until`은 그 시각부터 {VALIDITY_DAYS}일 뒤다.
시간은 시간대가 포함된 ISO 8601 형식으로 표현한다.
견적은 가격·재고를 예약하거나 보장하지 않으며 실제 주문 단계에서는 재확인한다.
견적에는 적용한 정책 버전을 `policy_version`으로 표시한다.
"""

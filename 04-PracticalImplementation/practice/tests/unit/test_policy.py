"""정책 문서의 설계 일치와 단일 원본 반영을 검증한다."""

from decimal import Decimal

import pytest

from app import policy
from app.resources.policy import get_quote_policy


def test_render_quote_policy_v1_policy_returns_expected_markdown() -> None:
    """
    Given: 설계에서 승인한 v1 견적 정책.
    When: render_quote_policy로 Markdown을 생성한다.
    Then: 정책 값·계산 순서·안내기간·보장하지 않는다는 안내가 설계와 일치한다.
    """
    text = policy.render_quote_policy()
    assert text.startswith("# 견적 정책\n")
    expected_rules = [
        "정책 버전: `v1`",
        "통화: USD",
        "배송비: 후보 견적당 20.00 USD",
        "세율: 할인 후 상품 금액의 10%",
        "금액을 소수 2자리까지 `ROUND_HALF_UP`으로 반올림",
        "견적 안내기간: 생성 시각부터 7일",
        "승인된 과제용 가정이며 실제 상거래·세법을 나타내지 않는다",
        "DummyJSON의 가격 숫자를 USD로 해석하며 환율 변환은 하지 않는다",
        "상품의 `discountPercentage`를 상품 금액에 한 번 적용한다",
        "배송비는 요청 수량과 관계없이 후보 견적마다 한 번 부과한다",
        "후보 사이의 금액이나 배송비를 합산하지 않는다",
        "배송비에는 세금을 적용하지 않는다",
        "`valid_until`은 그 시각부터 7일 뒤다",
        "시간대가 포함된 ISO 8601 형식",
        "가격·재고를 예약하거나 보장하지 않으며 실제 주문 단계에서는 재확인한다",
        "정책 버전을 `policy_version`으로 표시한다",
    ]
    for rule in expected_rules:
        assert rule in text

    calculation_steps = [
        line for line in text.splitlines()
        if line[:1].isdigit() and line[1:3] == ". "
    ]
    assert calculation_steps == [
        "1. 할인 전 상품 금액 = 단가 × 수량을 소수 2자리로 반올림",
        "2. 할인 금액 = 할인 전 상품 금액 × 할인율 / 100을 소수 2자리로 반올림",
        "3. 할인 후 상품 금액(`subtotal`) = 할인 전 상품 금액 − 할인 금액",
        "4. 세금(`tax`) = (할인 후 상품 금액 × 0.10)를 소수 2자리로 반올림",
        "5. 최종 금액(`total`) = 할인 후 상품 금액 + 20.00 + 세금",
        "6. 예산 충족(`within_budget`) = 최종 금액이 입력 예산 이하인지",
    ]


def test_get_quote_policy_updated_policy_returns_updated_markdown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Given: 정책 원본의 버전·통화·배송비·세율·안내기간을 테스트에서 변경한 상태.
    When: get_quote_policy로 Resource 내용을 읽는다.
    Then: 요약과 계산·안내 규칙에 같은 원본 값이 반영된다.
    """
    monkeypatch.setattr(policy, "POLICY_VERSION", "v2")
    monkeypatch.setattr(policy, "CURRENCY", "EUR")
    monkeypatch.setattr(policy, "SHIPPING_FEE", Decimal("35.50"))
    monkeypatch.setattr(policy, "TAX_RATE", Decimal("0.075"))
    monkeypatch.setattr(policy, "VALIDITY_DAYS", 3)

    text = get_quote_policy()
    assert "정책 버전: `v2`" in text
    assert "통화: EUR" in text
    assert "후보 견적당 35.50 EUR" in text
    assert "DummyJSON의 가격 숫자를 EUR로 해석" in text
    assert "할인 후 상품 금액의 7.5%" in text
    assert "할인 후 상품 금액 × 0.075" in text
    assert "할인 후 상품 금액 + 35.50 + 세금" in text
    assert "견적 안내기간: 생성 시각부터 3일" in text
    assert "valid_until`은 그 시각부터 3일 뒤" in text

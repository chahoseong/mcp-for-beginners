"""견적 Prompt 함수의 메시지 생성과 입력 검증을 검사한다."""

import pytest
from mcp.shared.exceptions import MCPError
from mcp_types import INVALID_PARAMS

from app.prompts.quote import prepare_quote


@pytest.mark.parametrize(
    ("quantity", "budget", "keyword"),
    [("3", "2000.00", "Samsung"), ("1", "0.01", "")],
)
def test_prepare_quote_valid_arguments_returns_user_message(
    quantity: str, budget: str, keyword: str,
) -> None:
    """
    Given: 문자열 구매 조건과 지정한 검색어, 최소 수량·예산을 포함한 정상 입력.
    When: prepare_quote를 호출한다.
    Then: 조건을 채운 role=user, type=text 메시지 한 개를 반환한다.
    """
    messages = prepare_quote("smartphones", quantity, budget, keyword)
    assert len(messages) == 1
    message = messages[0]
    assert message.role == "user"
    assert message.content.type == "text"
    text = message.content.text
    assert "상품 카테고리: smartphones" in text
    assert f"추가 검색어: {keyword} (비어 있으면 추가 조건 없음)" in text
    assert f"동일 모델의 요청 수량: {quantity}개" in text
    assert f"총 예산: {budget} USD" in text


def test_prepare_quote_omitted_keyword_returns_default_search_instruction() -> None:
    """
    Given: 카테고리·수량·예산만 있고 keyword는 생략한 입력.
    When: prepare_quote를 호출한다.
    Then: 빈 검색어와 추가 조건이 없다는 안내를 포함한 메시지를 반환한다.
    """
    messages = prepare_quote("smartphones", "3", "2000.00")
    assert "추가 검색어:  (비어 있으면 추가 조건 없음)" in messages[0].content.text


def test_prepare_quote_valid_arguments_preserves_quote_workflow() -> None:
    """
    Given: 유효한 구매 조건과 설계에서 승인한 전체 견적 작업 지시.
    When: prepare_quote로 메시지를 생성한다.
    Then: 정책 확인·후보 검색·재고·견적·비교표·실패 보고·담당자 선택 지시를 유지한다.
    """
    text = prepare_quote("smartphones", "3", "2000.00")[0].content.text
    expected_steps = [
        "1. search_products로 카테고리와 검색어에 맞는 후보를 조회해주세요.",
        "2. 각 후보의 product_id와 요청 수량으로 check_stock을 호출해주세요.",
        "3. 재고가 충분한 후보마다 calculate_quote를 호출해주세요.",
        "4. 재고가 충분하고 within_budget이 true인 후보들을 모두 보여주세요.",
        "5. 상품 ID, 상품명, 수량, 단가, 할인 금액, 할인 후 상품 금액,",
        "6. 재고 부족·예산 초과로 제외된 후보와 조회에 실패한 후보를 구분해 안내해주세요.",
    ]
    positions = [text.index(step) for step in expected_steps]
    assert positions == sorted(positions)
    instructions = [
        "Host가 제공한 quote://policy를 확인하고 해당 정책을 적용해주세요.",
        "정책을 읽지 못했다면 금액을 추측하지 말고 작업을 중단해주세요.",
        "product_id, quantity, budget을 전달하며 가격·할인율은 직접 입력하지 마세요.",
        "서로 다른 후보의 금액이나 배송비를 합산하지 마세요.",
        "배송비, 세금, 최종 금액, 재고 확인 시각, 견적 안내기간을 비교표로 작성해주세요.",
        "적용한 정책 버전과 가격·재고를 예약하지 않았다는 점도 표시해주세요.",
        "조건을 만족하는 후보가 없다면 그 이유를 설명하고 조건 변경을 요청해주세요.",
        "조회 실패가 남아 있다면 전체 후보 검증을 완료했다고 표현하지 마세요.",
        "최종 상품은 영업 담당자가 선택합니다. 상품을 자동 선택하거나 주문하지 마세요.",
    ]
    for instruction in instructions:
        assert instruction in text


INVALID_VALUES = [
    pytest.param(field, value, id=f"{field}-{label}")
    for field, cases in (
        ("category", [("empty", ""), ("blank", " \t")]),
        ("quantity", [
            ("empty", ""), ("zero", "0"), ("negative", "-1"),
            ("decimal", "3.0"), ("fraction", "1.5"), ("boolean", "true"),
            ("text", "abc"), ("exponent", "1e3"), ("nan", "NaN"),
            ("infinity", "Infinity"), ("unicode", "１２"),
        ]),
        ("budget", [
            ("empty", ""), ("zero", "0"), ("decimal-zero", "0.00"),
            ("negative", "-1"), ("precision", "1.001"), ("nan", "NaN"),
            ("infinity", "Infinity"), ("exponent", "1e3"),
            ("text", "abc"), ("separator", "1,000.00"),
        ]),
    )
    for label, value in cases
]


@pytest.mark.parametrize(("field", "value"), INVALID_VALUES)
def test_prepare_quote_invalid_argument_raises_input_error(
    field: str, value: str,
) -> None:
    """
    Given: 카테고리·수량·예산 중 하나가 형식 또는 범위를 벗어난 문자열.
    When: prepare_quote를 호출한다.
    Then: 메시지를 반환하지 않고 수정할 인자를 명시한 MCP 입력 오류를 발생시킨다.
    """
    arguments = {"category": "smartphones", "quantity": "3", "budget": "2000.00"}
    arguments[field] = value
    with pytest.raises(MCPError) as raised:
        prepare_quote(**arguments)
    assert raised.value.code == INVALID_PARAMS
    assert raised.value.message.startswith(f"{field}:")


def test_prepare_quote_surrounding_whitespace_returns_trimmed_conditions() -> None:
    """
    Given: 네 인자 모두 앞뒤 공백이 포함된 정상 구매 조건.
    When: prepare_quote를 호출한다.
    Then: 공백을 제거한 카테고리·수량·예산·검색어로 메시지를 생성한다.
    """
    messages = prepare_quote(" smartphones ", " 3 ", " 2000.00 ", " Samsung ")
    text = messages[0].content.text
    assert "상품 카테고리: smartphones\n" in text
    assert "추가 검색어: Samsung (비어 있으면 추가 조건 없음)" in text
    assert "동일 모델의 요청 수량: 3개\n" in text
    assert "총 예산: 2000.00 USD\n" in text


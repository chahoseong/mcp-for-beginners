"""영업 담당자의 구매 조건으로 견적 작업 지시 메시지를 만든다."""

import re
from decimal import Decimal
from typing import Annotated

from mcp.server.mcpserver.prompts.base import Message, UserMessage
from mcp.shared.exceptions import MCPError
from mcp_types import INVALID_PARAMS
from pydantic import Field


PREPARE_QUOTE_TEMPLATE = """영업 담당자가 고객에게 보낼 상품 견적 후보를 준비해주세요.

구매 조건:
- 상품 카테고리: {category}
- 추가 검색어: {keyword} (비어 있으면 추가 조건 없음)
- 동일 모델의 요청 수량: {quantity}개
- 배송비와 세금까지 포함한 총 예산: {budget} USD

Host가 제공한 quote://policy를 확인하고 해당 정책을 적용해주세요.
정책을 읽지 못했다면 금액을 추측하지 말고 작업을 중단해주세요.

1. search_products로 카테고리와 검색어에 맞는 후보를 조회해주세요.
2. 각 후보의 product_id와 요청 수량으로 check_stock을 호출해주세요.
3. 재고가 충분한 후보마다 calculate_quote를 호출해주세요.
   product_id, quantity, budget을 전달하며 가격·할인율은 직접 입력하지 마세요.
4. 재고가 충분하고 within_budget이 true인 후보들을 모두 보여주세요.
   한 후보는 하나의 모델을 요청 수량만큼 구매하는 독립된 견적입니다.
   서로 다른 후보의 금액이나 배송비를 합산하지 마세요.
5. 상품 ID, 상품명, 수량, 단가, 할인 금액, 할인 후 상품 금액,
   배송비, 세금, 최종 금액, 재고 확인 시각, 견적 안내기간을 비교표로 작성해주세요.
   적용한 정책 버전과 가격·재고를 예약하지 않았다는 점도 표시해주세요.
6. 재고 부족·예산 초과로 제외된 후보와 조회에 실패한 후보를 구분해 안내해주세요.
   조건을 만족하는 후보가 없다면 그 이유를 설명하고 조건 변경을 요청해주세요.
   조회 실패가 남아 있다면 전체 후보 검증을 완료했다고 표현하지 마세요.

최종 상품은 영업 담당자가 선택합니다. 상품을 자동 선택하거나 주문하지 마세요.
"""


def prepare_quote(
    category: Annotated[
        str, Field(strict=True, description="상품 카테고리 식별자. 예: smartphones")
    ],
    quantity: Annotated[
        str, Field(strict=True, description="1 이상의 정수를 표현한 문자열. 예: 3")
    ],
    budget: Annotated[
        str, Field(strict=True, description="0 초과, 소수 2자리까지의 USD 금액 문자열")
    ],
    keyword: Annotated[
        str, Field(strict=True, description="추가 검색어. 생략하면 빈 문자열")
    ] = "",
) -> list[Message]:
    """영업 담당자의 구매 조건으로 견적 후보 준비 지시를 제공한다."""
    category = category.strip()
    quantity = quantity.strip()
    budget = budget.strip()
    keyword = keyword.strip()

    if not category:
        raise MCPError(INVALID_PARAMS, "category: 상품 카테고리를 입력해주세요.")
    if not re.fullmatch(r"[0-9]+", quantity) or not quantity.lstrip("0"):
        raise MCPError(
            INVALID_PARAMS, "quantity: 1 이상의 정수를 문자열로 입력해주세요."
        )
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})?", budget):
        raise MCPError(
            INVALID_PARAMS,
            "budget: 0보다 큰 USD 금액을 소수 둘째 자리까지 문자열로 입력해주세요.",
        )
    amount = Decimal(budget)
    if not amount.is_finite() or amount <= 0:
        raise MCPError(
            INVALID_PARAMS, "budget: 0보다 큰 유한한 USD 금액을 입력해주세요."
        )

    return [
        UserMessage(
            PREPARE_QUOTE_TEMPLATE.format(
                category=category,
                quantity=quantity,
                budget=budget,
                keyword=keyword,
            )
        )
    ]

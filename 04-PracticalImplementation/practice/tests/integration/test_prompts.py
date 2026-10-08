"""Client에서 실제 stdio 서버로 보낸 Prompt 요청의 응답을 검증한다."""

import pytest
from mcp import Client
from mcp.shared.exceptions import MCPError
from mcp_types import INVALID_PARAMS


pytestmark = pytest.mark.anyio


async def test_should_list_quote_prompt_when_prompts_are_requested(
    mcp_client: Client,
) -> None:
    """
    Given: 실제 앱 서버에 stdio로 연결한 MCP Client.
    When: prompts/list를 요청한다.
    Then: prepare_quote 하나와 필수 인자 3개·선택 keyword를 받는다.
    """
    result = await mcp_client.list_prompts()
    assert [prompt.name for prompt in result.prompts] == ["prepare_quote"]
    arguments = result.prompts[0].arguments
    assert arguments is not None
    assert {argument.name: argument.required for argument in arguments} == {
        "category": True, "quantity": True, "budget": True, "keyword": False,
    }


@pytest.mark.parametrize("keyword", [None, "Samsung"], ids=["omitted", "set"])
async def test_should_return_quote_instruction_when_prompt_arguments_are_valid(
    mcp_client: Client, keyword: str | None,
) -> None:
    """
    Given: 유효한 문자열 구매 조건과 생략하거나 지정한 keyword.
    When: Client가 prepare_quote의 prompts/get을 요청한다.
    Then: 구매 조건·검색어·견적 작업 지시를 담은 user 텍스트 메시지 하나를 받는다.
    """
    arguments = {"category": "smartphones", "quantity": "3", "budget": "2000.00"}
    if keyword is not None:
        arguments["keyword"] = keyword
    result = await mcp_client.get_prompt("prepare_quote", arguments)
    assert len(result.messages) == 1
    message = result.messages[0]
    assert message.role == "user"
    assert message.content.type == "text"
    text = message.content.text
    for expected in (
        "상품 카테고리: smartphones", "동일 모델의 요청 수량: 3개",
        "총 예산: 2000.00 USD",
        f"추가 검색어: {keyword or ''} (비어 있으면 추가 조건 없음)",
        "quote://policy", "1. search_products", "2. 각 후보의 product_id",
        "3. 재고가 충분한 후보마다 calculate_quote",
        "최종 상품은 영업 담당자가 선택합니다.",
    ):
        assert expected in text


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("category", ""), ("quantity", "0"), ("quantity", "3.0"),
        ("budget", "NaN"), ("budget", "1.001"),
    ],
)
async def test_should_return_prompt_error_when_argument_values_are_invalid(
    mcp_client: Client, field: str, value: str,
) -> None:
    """
    Given: 빈 category 또는 형식·범위를 벗어난 quantity·budget 문자열.
    When: Client가 prepare_quote의 prompts/get을 요청한다.
    Then: 메시지 대신 INVALID_PARAMS 코드와 해당 인자를 명시한 MCPError를 받는다.
    """
    arguments = {"category": "smartphones", "quantity": "3", "budget": "2000.00"}
    arguments[field] = value
    with pytest.raises(MCPError) as raised:
        await mcp_client.get_prompt("prepare_quote", arguments)
    assert raised.value.code == INVALID_PARAMS
    assert raised.value.message.startswith(f"{field}:")


@pytest.mark.parametrize(
    "missing_fields",
    [
        pytest.param(("category",), id="category"),
        pytest.param(("quantity",), id="quantity"),
        pytest.param(("budget",), id="budget"),
        pytest.param(("category", "quantity", "budget"), id="all-required"),
    ],
)
async def test_should_return_prompt_error_when_required_argument_is_missing(
    mcp_client: Client, missing_fields: tuple[str, ...],
) -> None:
    """
    Given: category·quantity·budget 중 하나 또는 모두를 생략한 요청.
    When: Client가 prepare_quote의 prompts/get을 요청한다.
    Then: INVALID_PARAMS·누락 인자·입력 안내를 받고 이후 정상 요청도 성공한다.
    """
    arguments = {"category": "smartphones", "quantity": "3", "budget": "2000.00"}
    for field in missing_fields:
        del arguments[field]
    with pytest.raises(MCPError) as raised:
        await mcp_client.get_prompt("prepare_quote", arguments)
    assert raised.value.code == INVALID_PARAMS
    assert "필수" in raised.value.message
    for field in missing_fields:
        assert field in raised.value.message
    assert "입력해주세요" in raised.value.message

    result = await mcp_client.get_prompt(
        "prepare_quote",
        {"category": "smartphones", "quantity": "3", "budget": "2000.00"},
    )
    assert len(result.messages) == 1
    assert result.messages[0].role == "user"


async def test_should_return_prompt_error_when_prompt_is_unknown(
    mcp_client: Client,
) -> None:
    """
    Given: 등록되지 않은 Prompt 이름 missing_prompt.
    When: Client가 해당 이름으로 prompts/get을 요청한다.
    Then: INVALID_PARAMS·없는 이름·목록 조회 안내를 받고 이후 정상 요청도 성공한다.
    """
    with pytest.raises(MCPError) as raised:
        await mcp_client.get_prompt("missing_prompt", {})
    assert raised.value.code == INVALID_PARAMS
    assert "missing_prompt" in raised.value.message
    assert "등록되지 않은" in raised.value.message
    assert "prompts/list" in raised.value.message

    result = await mcp_client.get_prompt(
        "prepare_quote",
        {"category": "smartphones", "quantity": "3", "budget": "2000.00"},
    )
    assert len(result.messages) == 1
    assert result.messages[0].role == "user"


async def test_should_return_prompt_error_when_argument_name_is_unknown(
    mcp_client: Client,
) -> None:
    """
    Given: 정상 필수 인자와 등록되지 않은 추가 인자 typo.
    When: Client가 prepare_quote의 prompts/get을 요청한다.
    Then: INVALID_PARAMS·추가 인자·수정 안내를 받고 이후 정상 요청도 성공한다.
    """
    arguments = {
        "category": "smartphones", "quantity": "3", "budget": "2000.00",
        "typo": "x",
    }
    with pytest.raises(MCPError) as raised:
        await mcp_client.get_prompt("prepare_quote", arguments)
    assert raised.value.code == INVALID_PARAMS
    assert "typo" in raised.value.message
    assert "등록되지 않은" in raised.value.message
    assert "삭제하거나 수정해주세요" in raised.value.message

    del arguments["typo"]
    result = await mcp_client.get_prompt("prepare_quote", arguments)
    assert len(result.messages) == 1
    assert result.messages[0].role == "user"

"""Client에서 실제 stdio 서버로 보낸 Resource 요청의 응답을 검증한다."""

import pytest
from mcp import Client
from mcp.shared.exceptions import MCPError


pytestmark = pytest.mark.anyio


async def test_should_list_quote_policy_when_resources_are_requested(
    mcp_client: Client,
) -> None:
    """
    Given: 실제 앱 서버에 stdio로 연결한 MCP Client.
    When: resources/list를 요청한다.
    Then: quote://policy 하나와 text/markdown MIME type을 받는다.
    """
    result = await mcp_client.list_resources()
    assert len(result.resources) == 1
    resource = result.resources[0]
    assert resource.name == "quote_policy"
    assert str(resource.uri) == "quote://policy"
    assert resource.mime_type == "text/markdown"


async def test_should_return_quote_policy_when_policy_is_requested(
    mcp_client: Client,
) -> None:
    """
    Given: 등록된 정책 URI quote://policy.
    When: Client가 resources/read를 요청한다.
    Then: URI·MIME type과 승인한 v1 정책 내용을 받는다.
    """
    result = await mcp_client.read_resource("quote://policy")
    assert len(result.contents) == 1
    content = result.contents[0]
    assert str(content.uri) == "quote://policy"
    assert content.mime_type == "text/markdown"
    text = content.text
    for expected in (
        "정책 버전: `v1`", "통화: USD", "후보 견적당 20.00 USD",
        "할인 후 상품 금액의 10%", "`discountPercentage`",
        "소수 2자리", "`ROUND_HALF_UP`", "생성 시각부터 7일",
        "배송비에는 세금을 적용하지 않는다.",
        "가격·재고를 예약하거나 보장하지 않으며",
    ):
        assert expected in text


async def test_should_return_resource_error_when_uri_is_unknown(
    mcp_client: Client,
) -> None:
    """
    Given: 등록되지 않은 URI quote://missing.
    When: Client가 resources/read를 요청한다.
    Then: 정상 내용 대신 해당 URI를 명시한 MCPError를 받는다.
    """
    with pytest.raises(MCPError) as raised:
        await mcp_client.read_resource("quote://missing")
    assert "Unknown resource" in raised.value.message
    assert "quote://missing" in raised.value.message

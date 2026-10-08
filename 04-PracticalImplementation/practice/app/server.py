"""상품 견적 과제의 stdio MCP 서버. Tool·Resource·Prompt를 등록한다."""

import logging
import sys

from mcp.server import MCPServer

from app.middleware import create_prompt_validation_middleware
from app.prompts.quote import prepare_quote
from app.resources.policy import get_quote_policy
from app.tools.stock import check_stock

mcp = MCPServer("product-quote-practice")
mcp.middleware.append(create_prompt_validation_middleware(mcp))
mcp.tool()(check_stock)
mcp.resource(
    "quote://policy",
    name="quote_policy",
    title="견적 정책",
    mime_type="text/markdown",
)(get_quote_policy)
mcp.prompt(title="견적 후보 준비")(prepare_quote)


def main() -> None:
    """표준 출력은 MCP 통신에 사용하고 서버 로그는 표준 오류로 보낸다."""
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    logger = logging.getLogger(__name__)
    logger.info("MCP server starting with stdio.")

    mcp.run(transport="stdio")

    # run()이 예외 없이 반환했을 때만 정상 종료 메시지를 남긴다.
    logger.info("MCP server stopped normally.")

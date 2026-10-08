"""상품 견적 과제의 stdio MCP 서버. Tool·Resource·Prompt를 등록한다."""

import logging
import sys
from typing import Any

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.shared.exceptions import MCPError
from mcp_types import INVALID_PARAMS, GetPromptResult, InputRequiredResult

from app.prompts.quote import prepare_quote
from app.resources.policy import get_quote_policy
from app.tools.stock import check_stock

class QuoteMCPServer(MCPServer):
    """Prompt 요청의 수정 가능한 오류를 명시적인 MCP 입력 오류로 전달한다."""

    async def get_prompt(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
        context: Context[Any, Any] | None = None,
    ) -> GetPromptResult | InputRequiredResult:
        """등록 정보로 이름·필수 인자를 검사한 뒤 SDK에 메시지 생성을 맡긴다."""
        prompts = await self.list_prompts()
        prompt = next((item for item in prompts if item.name == name), None)
        if prompt is None:
            raise MCPError(
                INVALID_PARAMS,
                f"등록되지 않은 Prompt 이름입니다: {name}. "
                "prompts/list에서 사용 가능한 이름을 확인해주세요.",
            )

        provided = arguments or {}
        missing = sorted(
            argument.name
            for argument in (prompt.arguments or [])
            if argument.required and argument.name not in provided
        )
        if missing:
            raise MCPError(
                INVALID_PARAMS,
                f"필수 Prompt 인자가 누락되었습니다: {', '.join(missing)}. "
                "누락된 인자를 입력해주세요.",
            )

        allowed = {argument.name for argument in (prompt.arguments or [])}
        unexpected = sorted(set(provided) - allowed)
        if unexpected:
            raise MCPError(
                INVALID_PARAMS,
                f"등록되지 않은 Prompt 인자입니다: {', '.join(unexpected)}. "
                "해당 인자를 삭제하거나 수정해주세요. "
                "prompts/list에서 사용 가능한 인자를 확인할 수 있습니다.",
            )

        return await super().get_prompt(name, arguments, context)


mcp = QuoteMCPServer("product-quote-practice")
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

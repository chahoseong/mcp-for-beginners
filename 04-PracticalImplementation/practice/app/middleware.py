"""Prompt 조회 요청을 검사하고 수정 가능한 MCP 입력 오류를 전달한다."""

from typing import Any

from mcp.server import MCPServer, ServerRequestContext
from mcp.server.context import CallNext, HandlerResult, ServerMiddleware
from mcp.shared.exceptions import MCPError
from mcp_types import INVALID_PARAMS, GetPromptRequestParams
from mcp_types.methods import validate_client_request


def create_prompt_validation_middleware(server: MCPServer) -> ServerMiddleware[Any]:
    """서버의 Prompt 등록 정보를 사용하는 요청 검사 middleware를 만든다."""

    async def validate_prompt_request(
        ctx: ServerRequestContext[Any], call_next: CallNext,
    ) -> HandlerResult:
        """Prompt 이름·필수 인자·추가 인자를 확인한 뒤 요청을 전달한다."""
        if ctx.method != "prompts/get" or ctx.request_id is None:
            return await call_next(ctx)

        try:
            validate_client_request(ctx.method, ctx.protocol_version, ctx.params)
            params = GetPromptRequestParams.model_validate(
                ctx.params or {}, by_name=False,
            )
        except (KeyError, ValueError):
            # 버전·요청 형식 오류는 SDK의 기본 검증과 오류 처리에 맡긴다.
            return await call_next(ctx)

        prompts = await server.list_prompts()
        prompt = next((item for item in prompts if item.name == params.name), None)
        if prompt is None:
            raise MCPError(
                INVALID_PARAMS,
                f"등록되지 않은 Prompt 이름입니다: {params.name}. "
                "prompts/list에서 사용 가능한 이름을 확인해주세요.",
            )

        provided = params.arguments or {}
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

        return await call_next(ctx)

    return validate_prompt_request

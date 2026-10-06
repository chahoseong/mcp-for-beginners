from mcp import MCPError
import mcp.types as types


async def build_explanation(arguments: dict[str, str]) -> str:
    expression = arguments.get("expression", "").strip()

    if not expression:
        raise MCPError(
            types.INVALID_PARAMS,
            "expression is required and must not be blank.",
        )

    return (
        "다음 계산식의 결과와 계산 과정을 한국어로 설명해주세요.\n"
        f"계산식: {expression}"
    )


prompt_explain = {
    "name": "explain_calculation",
    "description": "계산 결과와 과정을 설명하도록 요청합니다.",
    "arguments": [
        {
            "name": "expression",
            "description": "설명할 계산식",
            "required": True,
        }
    ],
    "handler": build_explanation,
}
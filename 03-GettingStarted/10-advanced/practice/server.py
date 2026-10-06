import asyncio
import json

from mcp import MCPError
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types
from pydantic import ValidationError

from tools import tools
from resources import resources
from prompts import prompts


async def handle_list_tools(ctx, params) -> types.ListToolsResult:
    """Return tool definitions from the registry."""
    return types.ListToolsResult(
        tools=[
            types.Tool(
                name=tool["name"],
                description=tool["description"],
                input_schema=tool["input_model"].model_json_schema(),
            )
            for tool in tools.values()
        ]
    )


async def handle_call_tool(
    ctx, params: types.CallToolRequestParams
) -> types.CallToolResult:
    """Validate arguments and dispatch to the selected tool."""
    if params.name not in tools:
        raise MCPError(
            types.INVALID_PARAMS,
            f"Unknown tool: {params.name}",
        )

    tool = tools[params.name]

    try:
        validated = tool["input_model"].model_validate(
            params.arguments or {}
        )
    except ValidationError as exc:
        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"Invalid arguments: {exc}",
                )
            ],
            is_error=True,
        )

    value = await tool["handler"](validated)
    payload = {"result": value}

    return types.CallToolResult(
        content=[
            types.TextContent(
                type="text",
                text=json.dumps(payload),
            )
        ],
        structured_content=payload,
        is_error=False,
    )


async def handle_list_resources(ctx, params) -> types.ListResourcesResult:
    return types.ListResourcesResult(
        resources=[
            types.Resource(
                uri=resource["uri"],
                name=resource["name"],
                description=resource["description"],
                mime_type=resource["mime_type"],
            )
            for resource in resources.values()
        ]
    )


async def handle_read_resource(
    ctx, params: types.ReadResourceRequestParams
) -> types.ReadResourceResult:
    uri = str(params.uri)

    if uri not in resources:
        raise MCPError(
            types.INVALID_PARAMS,
            f"Unknown resource: {uri}",
        )

    resource = resources[uri]
    text = await resource["handler"]()

    return types.ReadResourceResult(
        contents=[
            types.TextResourceContents(
                uri=uri,
                mime_type=resource["mime_type"],
                text=text,
            )
        ]
    )


async def handle_list_prompts(ctx, params) -> types.ListPromptsResult:
    return types.ListPromptsResult(
        prompts=[
            types.Prompt(
                name=prompt["name"],
                description=prompt["description"],
                arguments=[
                    types.PromptArgument(**argument)
                    for argument in prompt["arguments"]
                ],
            )
            for prompt in prompts.values()
        ]
    )


async def handle_get_prompt(
    ctx, params: types.GetPromptRequestParams
) -> types.GetPromptResult:
    if params.name not in prompts:
        raise MCPError(
            types.INVALID_PARAMS,
            f"Unknown prompt: {params.name}",
        )

    prompt = prompts[params.name]
    text = await prompt["handler"](params.arguments or {})

    return types.GetPromptResult(
        description=prompt["description"],
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=text),
            )
        ],
    )


server = Server(
    "advanced-practice",
    on_list_tools=handle_list_tools,
    on_call_tool=handle_call_tool,
    on_list_resources=handle_list_resources,
    on_read_resource=handle_read_resource,
    on_list_prompts=handle_list_prompts,
    on_get_prompt=handle_get_prompt,
)


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
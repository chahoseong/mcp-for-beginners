import asyncio
import sys
from pathlib import Path

from mcp import Client, MCPError, StdioServerParameters


async def main() -> None:
    server_path = Path(__file__).resolve().with_name("server.py")
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
    )

    async with Client(
        server_params, mode="2026-07-28"
    ) as client:
        print("Connected")

        listed = await client.list_tools()
        for tool in listed.tools:
            print("Tool:", tool.name)
            print("Input schema:", tool.input_schema)

        print("Use add tool")
        result = await client.call_tool(
            "add", arguments={"a": 5, "b": 3}
        )
        print("is_error:", result.is_error)
        print("structured_content:", result.structured_content)

        print("Use multiply tool")
        result = await client.call_tool(
            "multiply", arguments={"a": 2.5, "b": 4}
        )
        print("is_error:", result.is_error)
        print("structured_content:", result.structured_content)


        invalid_cases = [
            ("Missing a", {"b": 3}),
            ("String a", {"a": "5", "b": 3}),
        ]

        for label, arguments in invalid_cases:
            print(f"\nCase: {label}")
            result = await client.call_tool(
                "add", arguments=arguments
            )
            print("is_error:", result.is_error)
            print("content:", result.content)

        print("\nCase: Unknown tool")
        try:
            await client.call_tool(
                "unknown_tool", arguments={"a": 5, "b": 3}
            )
        except MCPError as exc:
            print("Error code:", exc.code)
            print("Error message:", exc.message)

        print("\nResources")
        listed_resources = await client.list_resources()
        for resource in listed_resources.resources:
            print("Resource:", resource.uri, resource.name)

        read_result = await client.read_resource(
            "guide://calculator"
        )
        for content in read_result.contents:
            print("Resource text:", content.text)


        print("\nPrompts")
        listed_prompts = await client.list_prompts()
        for prompt in listed_prompts.prompts:
            print("Prompt:", prompt.name)
            print("Arguments:", prompt.arguments)

        prompt_result = await client.get_prompt(
            "explain_calculation",
            arguments={"expression": "2.5 * 4"},
        )
        for message in prompt_result.messages:
            print("Role:", message.role)
            print("Prompt text:", message.content.text)


if __name__ == "__main__":
    asyncio.run(main())
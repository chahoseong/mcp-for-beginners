"""
Complete Python MCP Client Example

This client demonstrates how to:
1. Connect to an MCP server using stdio transport
2. List available tools and resources
3. Call calculator tools
4. Handle responses from the server
"""

import asyncio
import sys
from pathlib import Path

from mcp import Client, MCPError, StdioServerParameters



class MCPCalculatorClient:
    def __init__(self):
        server_path = (
            Path(__file__).resolve().parent
            / "solution"
            / "python"
            / "server.py"
        )

        self.server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(server_path)]
        )

    async def run(self):
        """Connect to the server and list its tools"""
        async with Client(self.server_params) as session:
            print("Connected")
            print("Protocol:", session.protocol_version)

            await self.list_tools(session)
            # await self.test_calculator_operations(session)
            #await self.list_and_test_resources(session)
            # await self.test_errors(session)
            await self.run_custom_requests(session)

    async def list_tools(self, session: Client):
        """List all available tools on the server"""
        print("\n📋 Listing available tools:")
        try:
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
        except Exception as e:
            print(f"  Error listing tools: {e}")

    async def test_calculator_operations(self, session: Client):
        """Call add and inspect its result."""
        result = await session.call_tool(
            "add",
            arguments={"a": 5, "b": 3},
        )

        print("content:", result.content)
        print("structured_content:", result.structured_content)
        print("is_error:", result.is_error)

    async def list_and_test_resources(self, session: Client):
        """List resources and templates, then read a greeting."""
        resources = await session.list_resources()
        print("Resource count:", len(resources.resources))

        templates = await session.list_resource_templates()
        print("Resource templates:")
        for template in templates.resource_templates:
            print("  -", template.uri_template)

        result = await session.read_resource("greeting://Mina")
        print("Resource contents:", result.contents)

    def extract_text_result(self, result) -> str:
        """
        Extract text content from a tool result object.

        This method attempts to extract the text content from the `content` attribute
        of the result object. If no text content is found, it falls back to converting
        the result to a string. If an error occurs during extraction, it returns "No result".

        Args:
            result: The result object returned by a tool, which may contain a `content` attribute
                    with text or other types of data.

        Returns:
            A string representing the extracted text content, or a fallback string if no text is found.
        """
        try:
            if hasattr(result, 'content') and result.content:
                for content_item in result.content:
                    if hasattr(content_item, 'text') and content_item.text:
                        return content_item.text
                    elif hasattr(content_item, 'type') and content_item.type == "text":
                        return getattr(content_item, 'text', str(content_item))
            
            # Fallback: try to convert to string
            return str(result)
        except Exception:
            return "No result"

    async def test_errors(self, session: Client):
        """Compare an error result with a raised exception."""

        # 필수 인자 a를 누락한 Tool 호출
        result = await session.call_tool(
            "add",
            arguments={"b": 7},
        )

        if result.is_error:
            print("Tool failure:", result.content)
        else:
            print("Tool success:", result.structured_content)

        # 등록되지 않은 URI의 Resource 읽기
        try:
            await session.read_resource("unknown://Mina")
        except MCPError as error:
            print("Resource exception:", error)
            print("Error code:", error.code)

    async def run_custom_requests(self, session: Client):
        x = 5
        y = 3

        try:
            result = await session.call_tool(
                "add",
                arguments={"a": x, "b": y},
            )

            expected = 8

            if result.is_error:
                print("Tool failure:", result.content)
            else:
                actual = result.structured_content["result"]
                print(actual == expected)

            result = await session.read_resource(f"greeting://Mina")
            print(result.contents)
        except MCPError as error:
            print("Resource exception:", error)
            print("Error code:", error.code)


async def main():
    """Entry point for the client"""
    client = MCPCalculatorClient()
    await client.run()


if __name__ == "__main__":
    asyncio.run(main())

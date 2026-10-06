import asyncio
import os

import httpx2
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

URL = "http://127.0.0.1:8000/mcp"


async def main() -> None:
    token = os.environ["MCP_ACCESS_TOKEN"]

    async with httpx2.AsyncClient(
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0,
    ) as http_client:
        transport = streamable_http_client(
            URL,
            http_client=http_client,
        )

        async with Client(
            transport,
            mode="2026-07-28",
        ) as client:
            tools = await client.list_tools()
            print("Tools:", [tool.name for tool in tools.tools])

            for tool_name, arguments in [
                ("get_time", {}),
                ("set_message", {"message": "hello from client"}),
            ]:
                result = await client.call_tool(
                    tool_name,
                    arguments=arguments,
                )

                print("\nTool:", tool_name)
                print("is_error:", result.is_error)

                if result.is_error:
                    print("content:", result.content)
                else:
                    print("structured_content:", result.structured_content)


if __name__ == "__main__":
    asyncio.run(main())
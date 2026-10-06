import asyncio

from server import UI_URI, mcp


async def main():
    tools = await mcp.list_tools()
    for tool in tools:
        print("Tool:", tool.name)
        print("UI metadata:", tool.meta)

    contents = await mcp.read_resource(UI_URI)
    for content in contents:
        print("MIME:", content.mime_type)


if __name__ == "__main__":
    asyncio.run(main())
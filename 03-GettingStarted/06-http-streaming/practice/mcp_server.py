import asyncio

from mcp.server import MCPServer
from mcp.server.mcpserver import Context

server = MCPServer("http-practice")


@server.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@server.tool()
async def process_files(files: list[str], ctx: Context) -> str:
    """Simulate file processing and report progress."""

    for index, filename in enumerate(files, start=1):
        await asyncio.sleep(1)
        await ctx.report_progress(
            progress=index,
            total=len(files),
            message=f"Completed: {filename}",
        )

    handled_files = ", ".join(files)

    return f"Processed {handled_files} files"


if __name__ == "__main__":
    server.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000,
    )
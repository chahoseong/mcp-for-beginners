import os

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

server = MCPServer("deployment-practice-v2")


@server.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


@server.tool()
def divide(a: int, b: int) -> float:
    """Divide a by b. The divisor must not be zero."""
    if b == 0:
        raise ToolError("Cannot divide by zero.")

    return a / b


if __name__ == "__main__":
    server.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        json_response=True,
    )
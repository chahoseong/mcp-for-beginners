# server.py
import logging
from pathlib import Path

from mcp.server import MCPServer

call_logger = logging.getLogger("calculator.calls")
call_logger.setLevel(logging.INFO)
call_logger.propagate = False
call_handler = logging.FileHandler(
    Path(__file__).with_name("tool_calls.log"), encoding="utf-8"
)
call_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
call_logger.addHandler(call_handler)

# Create an MCP server
mcp = MCPServer("Demo")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    result = a + b
    call_logger.info("add a=%s b=%s result=%s", a, b, result)
    return result


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    result = a - b
    call_logger.info("subtract a=%s b=%s result=%s", a, b, result)
    return result


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run()

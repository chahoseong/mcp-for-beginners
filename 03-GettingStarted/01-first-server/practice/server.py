from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalaized greeting"""
    return f"Hello, {name}!"


@mcp.tool()
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    return a / b


if __name__ == "__main__":
    mcp.run()
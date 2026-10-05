import logging
import sys

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

import json
from urllib.error import URLError
from urllib.request import Request, urlopen


logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

server = MCPServer("stdio-practice", version="1.0.0")


@server.tool()
def get_greeting(name: str) -> str:
    """Return a greeting for the given name."""
    return f"Hello, {name}!"


@server.tool()
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two integers."""
    result = a + b
    logger.info("calculate_sum: a=%s b=%s result=%s", a, b, result)
    return result


@server.tool()
def calculate_product(a: int, b: int) -> int:
    """Calculate the product of two integers."""
    return a * b


@server.tool()
def get_server_info() -> dict[str, object]:
    """Return descriptive information about this example server."""
    return {
        "name": "stdio-practice",
        "version": "1.0.0",
        "transport": "stdio",
        "capabilities": ["tools"],
    }


@server.tool()
def get_random_joke() -> str:
    """Fetch a random Chuck Norris joke from the external API."""
    request = Request(
        "https://api.chucknorris.io/jokes/random",
        headers={
            "User-Agent": "mcp-stdio-practice/1.0",
            "Accept": "application/json",
        }
    )
    
    logger.info("Fetching a random joke")

    try:
        with urlopen(request, timeout=10) as response:
            data = json.load(response)
    except (URLError, TimeoutError) as exc:
        logger.warning("Joke API request failed: %s", exc)
        raise ToolError("외부 API에서 농담을 가져오지 못했습니다.") from exc

    return data["value"]


if __name__ == "__main__":
    logger.info("Starting stdio-practice")
    server.run(transport="stdio")
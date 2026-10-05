import pytest

from mcp import Client
from practice.server import server

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def test_registered_tools():
    async with Client(server, mode="2026-07-28") as client:
        result = await client.list_tools()

        names = {tool.name for tool in result.tools}
        assert names == {"add", "divide"}


async def test_divide_success():
    async with Client(server, mode="2026-07-28") as client:
        result = await client.call_tool(
            "divide", arguments={"a": 5, "b": 2}
        )

        assert result.is_error is False
        assert result.structured_content == {"result": 2.5}


async def test_divide_missing_argument():
    async with Client(server, mode="2026-07-28") as client:
        result = await client.call_tool(
            "divide", arguments={"b": 2}
        )

        assert result.is_error is True


async def test_divide_zero_denominator():
    async with Client(server, mode="2026-07-28") as client:
        result = await client.call_tool(
            "divide", arguments={"a": 3, "b": 0}
        )

        assert result.is_error is True
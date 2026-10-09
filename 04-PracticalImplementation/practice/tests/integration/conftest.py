"""실제 API 원본과 앱 서버의 stdio 연결을 제공하는 공통 fixture."""

import math
import sys
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import anyio
import httpx
import pytest
from mcp import Client
from mcp.client import Transport
from mcp.client.stdio import StdioServerParameters, stdio_client


@pytest.fixture
async def dummyjson_category_products() -> list[dict[str, Any]]:
    """운영 검색 코드와 독립적으로 smartphones 전체 원본을 한 번 조회한다."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            "https://dummyjson.com/products/category/smartphones",
            params={"limit": 0},
        )
        response.raise_for_status()
    payload = response.json()
    assert isinstance(payload, dict), "카테고리 원본이 JSON 객체가 아닙니다."
    products = payload["products"]
    assert isinstance(products, list)
    assert type(payload["total"]) is int and payload["total"] >= 0
    assert type(payload["skip"]) is int and payload["skip"] == 0
    assert type(payload["limit"]) is int and payload["limit"] >= 0
    assert len(products) == payload["total"], "전체 상품을 받지 못했습니다."
    ids: set[int] = set()
    for product in products:
        assert isinstance(product, dict)
        assert type(product["id"]) is int and product["id"] > 0
        assert isinstance(product["title"], str) and product["title"]
        assert isinstance(product["description"], str)
        assert product["category"] == "smartphones"
        assert product["id"] not in ids, "원본 상품 ID가 중복되었습니다."
        ids.add(product["id"])
    return products


@pytest.fixture
async def dummyjson_product() -> dict[str, Any]:
    """운영 조회·계산 코드를 호출하지 않고 상품 ID 1의 현재 원본을 읽는다."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("https://dummyjson.com/products/1")
        response.raise_for_status()
    product = response.json()
    assert isinstance(product, dict), "상품 원본이 JSON 객체가 아닙니다."
    assert type(product["id"]) is int and product["id"] == 1
    assert isinstance(product["title"], str) and product["title"].strip()
    for field in ("price", "discountPercentage"):
        value = product[field]
        assert type(value) in (int, float)
        assert math.isfinite(value) and value >= 0
    assert product["discountPercentage"] <= 100
    return product


@pytest.fixture
def mcp_server_log(tmp_path: Path) -> Path:
    """서버 로그를 요청 응답과 구분하여 읽을 수 있는 임시 파일 경로."""
    return tmp_path / "server.stderr.log"


@pytest.fixture
async def mcp_transport(mcp_server_log: Path) -> AsyncIterator[Transport]:
    """서버용 stdio transport를 제공하고 사용 후 정상 종료 로그를 확인한다."""
    practice_dir = Path(__file__).resolve().parents[2]
    server = StdioServerParameters(
        command=str(Path(sys.executable).resolve()),
        args=["-m", "app"],
        cwd=practice_dir,
        env={"PYTHONIOENCODING": "utf-8"},
    )
    with mcp_server_log.open("w", encoding="utf-8") as errlog:
        with anyio.fail_after(120):
            yield stdio_client(server, errlog=errlog)
    stderr = mcp_server_log.read_text(encoding="utf-8")
    assert "MCP server stopped normally." in stderr, stderr


@pytest.fixture
async def mcp_client(mcp_transport: Transport) -> AsyncIterator[Client]:
    """실제 서버 프로세스에 stdio로 연결한 SDK Client를 제공한다."""
    async with Client(
        mcp_transport, read_timeout_seconds=60, cache=None,
    ) as client:
        yield client

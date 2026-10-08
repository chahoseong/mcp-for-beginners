"""실제 앱 서버 프로세스와 stdio로 연결하는 공통 fixture."""

import sys
from collections.abc import AsyncIterator
from pathlib import Path

import anyio
import pytest
from mcp import Client
from mcp.client.stdio import StdioServerParameters, stdio_client


@pytest.fixture
def mcp_server_log(tmp_path: Path) -> Path:
    """서버 로그를 요청 응답과 구분하여 읽을 수 있는 임시 파일 경로."""
    return tmp_path / "server.stderr.log"


@pytest.fixture
async def mcp_client(mcp_server_log: Path) -> AsyncIterator[Client]:
    """테스트마다 서버를 실행하고 연결 해제 후 정상 종료 로그를 확인한다."""
    practice_dir = Path(__file__).resolve().parents[2]
    server = StdioServerParameters(
        command=str(Path(sys.executable).resolve()),
        args=["-m", "app"],
        cwd=practice_dir,
        env={"PYTHONIOENCODING": "utf-8"},
    )
    with mcp_server_log.open("w", encoding="utf-8") as errlog:
        with anyio.fail_after(30):
            transport = stdio_client(server, errlog=errlog)
            async with Client(
                transport, read_timeout_seconds=15, cache=None
            ) as client:
                yield client
    stderr = mcp_server_log.read_text(encoding="utf-8")
    assert "MCP server stopped normally." in stderr, stderr

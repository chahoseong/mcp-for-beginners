"""TokenVerifier를 주입받아 보호된 MCP 서버를 구성하는 부분 예제.

실제 토큰 검증기와 HTTP 서비스 시작 코드는 포함하지 않는다.
"""

from pydantic import AnyHttpUrl

from mcp.server import MCPServer
from mcp.server.auth.provider import TokenVerifier
from mcp.server.auth.settings import AuthSettings


def build_server(verifier: TokenVerifier) -> MCPServer:
    """검증기를 연결하고 보호된 예제 도구를 등록한다."""
    server = MCPServer(
        "보고 요약",
        token_verifier=verifier,
        auth=AuthSettings(
            issuer_url=AnyHttpUrl("https://login.example.com"),
            resource_server_url=AnyHttpUrl("https://reports.example.com/mcp"),
            required_scopes=["reports:read"],
            validate_token_resource=True,
        ),
    )

    @server.tool()
    def report_summary() -> dict[str, int]:
        """예제 보고서 집계 값을 반환한다."""
        return {"completed": 9, "queued": 3}

    return server

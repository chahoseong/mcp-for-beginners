"""Client Credentials로 보호된 MCP 서버를 호출하는 클라이언트 예제.

실제 인가 서버와 MCP 서버, 사전에 허용된 클라이언트 자격이 필요하다.
예제 주소를 실제 서비스 주소로 바꾸고 REPORT_CLIENT_SECRET을 제공해야 한다.
"""

import asyncio
import os
from dataclasses import dataclass

import httpx2

from mcp import Client
from mcp.client import advertise
from mcp.client.auth.extensions.client_credentials import (
    ClientCredentialsOAuthProvider,
)
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken


@dataclass
class MemoryStorage:
    """토큰과 클라이언트 정보를 실행 중 메모리에만 보관한다."""

    tokens: OAuthToken | None = None
    client_info: OAuthClientInformationFull | None = None

    async def get_tokens(self) -> OAuthToken | None:
        return self.tokens

    async def set_tokens(self, tokens: OAuthToken) -> None:
        self.tokens = tokens

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        return self.client_info

    async def set_client_info(self, info: OAuthClientInformationFull) -> None:
        self.client_info = info


async def main() -> None:
    mcp_url = "https://reports.example.com/mcp"
    as_issuer = "https://login.example.com"
    oauth = ClientCredentialsOAuthProvider(
        server_url=mcp_url,
        storage=MemoryStorage(),
        client_id="report-reader",
        client_secret=os.environ["REPORT_CLIENT_SECRET"],
        token_endpoint_auth_method="client_secret_basic",
        scope="reports:read",
        issuer=as_issuer,
    )

    async with httpx2.AsyncClient(
        auth=oauth,
        timeout=httpx2.Timeout(30.0, read=300.0),
    ) as http_client:
        transport = streamable_http_client(mcp_url, http_client=http_client)
        async with Client(
            transport,
            mode="2026-07-28",
            extensions=[
                advertise("io.modelcontextprotocol/oauth-client-credentials")
            ],
        ) as client:
            result = await client.call_tool("report_summary", {})
            if result.is_error:
                raise RuntimeError("보고 도구 업무 실패")
            print(result.structured_content)  # 예제의 도구 결과만 출력한다.


if __name__ == "__main__":
    asyncio.run(main())

"""JWT 접근 토큰을 Introspection으로 확인하는 MCP 서버 예제."""

from __future__ import annotations

import base64
import logging
import os
import re
import time
from dataclasses import dataclass
from urllib.parse import quote_plus

import httpx2 as httpx
from mcp.server import MCPServer
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl


ISSUER = "https://login.example.com/"
RESOURCE = "http://127.0.0.1:8101/mcp"
INTROSPECTION_ENDPOINT = "http://127.0.0.1:9101/oauth/introspect"
INTROSPECTION_CLIENT_ID = "reports-mcp"
REQUIRED_SCOPES = ["reports:read"]
SCOPE_PATTERN = r"[\x21\x23-\x5B\x5D-\x7E]+(?: [\x21\x23-\x5B\x5D-\x7E]+)*"
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IntrospectionConfig:
    """조회용 자격과 응답에서 확인할 발급자·대상을 보관한다."""

    client_secret: str
    client_id: str = INTROSPECTION_CLIENT_ID
    endpoint: str = INTROSPECTION_ENDPOINT
    issuer: str = ISSUER
    resource: str = RESOURCE

    def __post_init__(self) -> None:
        if not self.client_id or not self.client_secret:
            raise ValueError("토큰 조회 요청을 인증할 자격이 필요합니다.")


def oauth_basic_header(client_id: str, client_secret: str) -> str:
    """ID와 비밀값을 각각 폼 인코딩한 뒤 OAuth Basic 헤더를 만든다."""
    credentials = f"{quote_plus(client_id, safe='')}:{quote_plus(client_secret, safe='')}"
    encoded = base64.b64encode(credentials.encode("ascii")).decode("ascii")
    return f"Basic {encoded}"


class IntrospectionTokenVerifier(TokenVerifier):
    """JWT 서명 검증 대신 조회 결과와 이 서버의 수신 정책을 확인한다."""

    def __init__(
        self,
        config: IntrospectionConfig,
        *,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.config = config
        self.http_client = http_client

    async def request_introspection(
        self, http_client: httpx.AsyncClient, token: str,
    ) -> httpx.Response:
        """조회용 자격은 헤더에, 조회 대상 토큰은 본문에 보낸다."""
        return await http_client.post(
            self.config.endpoint,
            headers={"Authorization": oauth_basic_header(self.config.client_id, self.config.client_secret)},
            data={"token": token, "token_type_hint": "access_token"},
        )

    def access_token_from_response(self, token: str, payload: object) -> AccessToken | None:
        """조회 응답의 구조와 발급자·대상·유효 시간을 확인한다."""
        if not isinstance(payload, dict) or type(payload.get("active")) is not bool:
            logger.warning("토큰 조회 실패: 응답 구조 오류")
            return None
        if payload["active"] is not True:
            return None
        if payload.get("iss") != self.config.issuer:
            logger.warning("토큰 조회 실패: 응답 발급자 불일치")
            return None
        audience = payload.get("aud")
        if isinstance(audience, str):
            resource = audience if audience == self.config.resource else None
        elif isinstance(audience, list) and all(isinstance(item, str) for item in audience):
            resource = self.config.resource if self.config.resource in audience else None
        else:
            resource = None
        if resource is None:
            logger.warning("토큰 조회 실패: 응답 사용 대상 불일치")
            return None
        expires_at = payload.get("exp")
        client_id = payload.get("client_id")
        subject = payload.get("sub")
        scope = payload.get("scope")
        if (
            type(expires_at) is not int or expires_at <= int(time.time())
            or not isinstance(client_id, str) or not client_id
            or not isinstance(subject, str) or not subject
            or not isinstance(scope, str)
            or (scope and re.fullmatch(SCOPE_PATTERN, scope) is None)
        ):
            logger.warning("토큰 조회 실패: 응답 필드 또는 유효 시간 오류")
            return None
        scopes = scope.split(" ") if scope else []
        return AccessToken(
            token=token,
            client_id=client_id,
            scopes=scopes,
            expires_at=expires_at,
            resource=resource,
            subject=subject,
            claims=payload,
        )

    async def verify_token(self, token: str) -> AccessToken | None:
        """조회 실패와 inactive를 구분하되, 어느 경우에도 접근을 허용하지 않는다."""
        try:
            if self.http_client is None:
                async with httpx.AsyncClient(timeout=5, trust_env=False) as http_client:
                    response = await self.request_introspection(http_client, token)
            else:
                response = await self.request_introspection(self.http_client, token)
        except httpx.HTTPError:
            logger.warning("토큰 조회 실패: 연결 또는 HTTP 요청 오류")
            return None
        if response.status_code != 200:
            if response.status_code == 401:
                logger.warning("토큰 조회 실패: 조회용 인증 자격 거부")
            else:
                logger.warning("토큰 조회 실패: 조회 서비스의 비정상 HTTP 응답")
            return None
        try:
            payload = response.json()
        except ValueError:
            logger.warning("토큰 조회 실패: JSON 응답 오류")
            return None
        return self.access_token_from_response(token, payload)


def build_server(verifier: IntrospectionTokenVerifier) -> MCPServer:
    """조회 검증기와 필요한 권한을 연결하고 예제 도구를 등록한다."""
    server = MCPServer(
        "토큰 조회 보고서",
        token_verifier=verifier,
        auth=AuthSettings(
            issuer_url=AnyHttpUrl(verifier.config.issuer),
            resource_server_url=AnyHttpUrl(verifier.config.resource),
            required_scopes=REQUIRED_SCOPES,
            validate_token_resource=True,
        ),
    )

    @server.tool()
    def report_summary() -> dict[str, int]:
        """보호된 요청이 허용되면 무해한 예제 집계 결과를 반환한다."""
        return {"completed": 9, "queued": 3}

    return server


if __name__ == "__main__":
    import uvicorn

    config = IntrospectionConfig(
        client_secret=os.environ["INTROSPECTION_CLIENT_SECRET"],
        client_id=os.environ.get("INTROSPECTION_CLIENT_ID", INTROSPECTION_CLIENT_ID),
        endpoint=os.environ.get("INTROSPECTION_ENDPOINT", INTROSPECTION_ENDPOINT),
        issuer=os.environ.get("JWT_ISSUER", ISSUER),
        resource=os.environ.get("MCP_RESOURCE", RESOURCE),
    )
    server = build_server(IntrospectionTokenVerifier(config))
    app = server.streamable_http_app(stateless_http=True, json_response=True)
    uvicorn.run(app, host="127.0.0.1", port=8101, access_log=False)

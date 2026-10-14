"""JWT 접근 토큰을 MCP 서버에서 직접 검증하는 보충 예제."""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from urllib.parse import urlsplit

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from mcp.server import MCPServer
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl


ISSUER = "https://login.example.com/"
RESOURCE = "http://127.0.0.1:8101/mcp"
REQUIRED_SCOPES = ["reports:read"]
REQUIRED_CLAIMS = ["iss", "sub", "aud", "exp", "iat", "jti", "client_id"]
SCOPE_PATTERN = r"[\x21\x23-\x5B\x5D-\x7E]+(?: [\x21\x23-\x5B\x5D-\x7E]+)*"


@dataclass(frozen=True)
class JWTVerificationConfig:
    """토큰 내용과 독립적으로 신뢰할 공개키와 발급자·대상을 설정한다."""

    public_key: rsa.RSAPublicKey
    issuer: str = ISSUER
    resource: str = RESOURCE

    def __post_init__(self) -> None:
        if not isinstance(self.public_key, rsa.RSAPublicKey):
            raise ValueError("신뢰할 RSA 공개키를 설정해야 합니다.")
        if not isinstance(self.issuer, str) or not isinstance(self.resource, str):
            raise ValueError("발급자와 MCP 서버 식별자는 URL 문자열이어야 합니다.")
        issuer = urlsplit(self.issuer)
        resource = urlsplit(self.resource)
        if issuer.scheme != "https" or not issuer.netloc or issuer.query or issuer.fragment:
            raise ValueError("발급자 식별자는 쿼리와 조각이 없는 HTTPS URL이어야 합니다.")
        if resource.scheme not in {"http", "https"} or not resource.netloc or resource.fragment:
            raise ValueError("MCP 서버 식별자는 조각이 없는 HTTP 또는 HTTPS URL이어야 합니다.")
        AnyHttpUrl(self.issuer)
        AnyHttpUrl(self.resource)


class JWTTokenVerifier(TokenVerifier):
    """신뢰한 공개키와 이 서버의 정책으로 JWT를 검사한다."""

    def __init__(self, config: JWTVerificationConfig) -> None:
        self.config = config

    async def verify_token(self, token: str) -> AccessToken | None:
        """토큰 오류는 거부하고, 설정·프로그램 오류는 토큰 오류로 숨기지 않는다."""
        try:
            claims = jwt.decode(
                token,
                self.config.public_key,
                algorithms=["RS256"],
                issuer=self.config.issuer,
                audience=self.config.resource,
                options={
                    "require": REQUIRED_CLAIMS,
                    "verify_exp": False,
                    "verify_iat": False,
                    "verify_nbf": False,
                },
            )
            header = jwt.get_unverified_header(token)
        except jwt.InvalidTokenError:
            return None

        # 위 서명 검사가 끝난 JWT의 헤더만 접근 토큰 유형 확인에 사용한다.
        if str(header.get("typ", "")).lower() not in {"at+jwt", "application/at+jwt"}:
            return None
        if any(not isinstance(claims[name], str) or not claims[name] for name in ("sub", "client_id", "jti")):
            return None

        # 예제는 시간을 정수로 받은 뒤 직접 검사한다. JWT 일반의 숫자 형식보다 좁은 정책이다.
        if type(claims["exp"]) is not int or type(claims["iat"]) is not int:
            return None
        if "nbf" in claims and type(claims["nbf"]) is not int:
            return None
        now = int(time.time())
        if claims["exp"] <= now or claims["iat"] > now:
            return None
        if "nbf" in claims and claims["nbf"] > now:
            return None

        audience = claims["aud"]
        if isinstance(audience, str):
            resource = audience if audience == self.config.resource else None
        elif isinstance(audience, list) and audience and all(isinstance(item, str) and item for item in audience):
            resource = self.config.resource if self.config.resource in audience else None
        else:
            resource = None
        if resource is None:
            return None

        scope = claims.get("scope", "")
        if not isinstance(scope, str) or (scope and re.fullmatch(SCOPE_PATTERN, scope) is None):
            return None
        scopes = scope.split(" ") if scope else []
        return AccessToken(
            token=token,
            client_id=claims["client_id"],
            scopes=scopes,
            expires_at=claims["exp"],
            resource=resource,
            subject=claims["sub"],
            claims=claims,
        )


def build_server(verifier: JWTTokenVerifier) -> MCPServer:
    """JWT 검증기·요청 권한·도구를 MCP SDK에 연결한다."""
    server = MCPServer(
        "JWT 검증 보고서",
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
        """토큰 검증과 권한 검사를 통과하면 예제 집계 결과를 반환한다."""
        return {"completed": 9, "queued": 3}

    return server


if __name__ == "__main__":
    import uvicorn

    public_key = serialization.load_pem_public_key(os.environ["JWT_PUBLIC_KEY_PEM"].encode("utf-8"))
    config = JWTVerificationConfig(
        public_key=public_key,
        issuer=os.environ.get("JWT_ISSUER", ISSUER),
        resource=os.environ.get("MCP_RESOURCE", RESOURCE),
    )
    server = build_server(JWTTokenVerifier(config))
    app = server.streamable_http_app(stateless_http=True, json_response=True)
    uvicorn.run(app, host="127.0.0.1", port=8101, access_log=False)

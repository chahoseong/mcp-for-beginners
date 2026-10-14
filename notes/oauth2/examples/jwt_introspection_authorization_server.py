"""JWT 접근 토큰의 Introspection을 설명하는 인가 서버 예제."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import os
import re
import secrets
import time
from dataclasses import dataclass
from collections.abc import Mapping
from urllib.parse import parse_qs, unquote_plus

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


ISSUER = "https://login.example.com/"
RESOURCE = "http://127.0.0.1:8101/mcp"
INTROSPECTION_CLIENT_ID = "reports-mcp"
CACHE_HEADERS = {"Cache-Control": "no-store", "Pragma": "no-cache"}
SCOPE_PATTERN = r"[\x21\x23-\x5B\x5D-\x7E]+(?: [\x21\x23-\x5B\x5D-\x7E]+)*"


@dataclass(frozen=True)
class AuthorizationServerConfig:
    """조회 자격과 신뢰할 JWT 검증 설정을 외부에서 공급받는다."""

    public_key: rsa.RSAPublicKey
    introspection_client_secret: str
    introspection_client_id: str = INTROSPECTION_CLIENT_ID
    issuer: str = ISSUER
    resource: str = RESOURCE
    inactive_jtis: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not isinstance(self.public_key, rsa.RSAPublicKey):
            raise ValueError("JWT 검증에 사용할 RSA 공개키가 필요합니다.")
        if not self.introspection_client_id or not self.introspection_client_secret:
            raise ValueError("조회 요청의 인증 자격이 필요합니다.")


class RequestError(Exception):
    """잘못된 조회 요청과 조회 자격 실패를 구분한다."""

    def __init__(self, error: str, status_code: int = 400) -> None:
        super().__init__(error)
        self.error = error
        self.status_code = status_code


def authenticate_request(request: Request, config: AuthorizationServerConfig) -> None:
    """OAuth Basic 자격을 디코딩하고 등록한 조회자의 자격과 비교한다."""
    try:
        headers = request.headers.getlist("authorization")
        if len(headers) != 1:
            raise ValueError
        scheme, encoded = headers[0].split()
        if scheme.lower() != "basic":
            raise ValueError
        decoded = base64.b64decode(encoded, validate=True).decode("ascii")
        client_part, separator, secret_part = decoded.partition(":")
        if not separator or re.search(r"%(?![0-9A-Fa-f]{2})", decoded):
            raise ValueError
        client_id = unquote_plus(client_part, encoding="utf-8", errors="strict")
        secret = unquote_plus(secret_part, encoding="utf-8", errors="strict")
    except (ValueError, UnicodeError, binascii.Error) as error:
        raise RequestError("invalid_client", 401) from error
    supplied = hashlib.sha256(secret.encode("utf-8")).digest()
    expected = hashlib.sha256(config.introspection_client_secret.encode("utf-8")).digest()
    if client_id != config.introspection_client_id or not hmac.compare_digest(supplied, expected):
        raise RequestError("invalid_client", 401)


async def read_introspection_form(request: Request) -> dict[str, str]:
    """조회할 토큰을 폼 본문에서 읽는다. 힌트는 조회 자격으로 사용하지 않는다."""
    media_type = request.headers.get("content-type", "").split(";", 1)[0]
    if media_type.strip().lower() != "application/x-www-form-urlencoded":
        raise RequestError("invalid_request")
    try:
        body = (await request.body()).decode("utf-8")
        if re.search(r"%(?![0-9A-Fa-f]{2})", body):
            raise ValueError
        values = parse_qs(
            body, keep_blank_values=True, strict_parsing=True,
            encoding="utf-8", errors="strict",
        )
        if any(len(items) != 1 for items in values.values()):
            raise ValueError
        form = {name: items[0] for name, items in values.items()}
        if not form.get("token"):
            raise ValueError
        return form
    except (ValueError, UnicodeError) as error:
        raise RequestError("invalid_request") from error


def inspect_jwt(token: str, config: AuthorizationServerConfig) -> dict[str, object]:
    """신뢰한 키·알고리즘·발급자·대상과 현재 상태로 JWT를 검사한다."""
    try:
        claims = jwt.decode(
            token,
            config.public_key,
            algorithms=["RS256"],
            issuer=config.issuer,
            audience=config.resource,
            options={"require": ["iss", "sub", "aud", "exp", "iat", "jti", "client_id", "scope"]},
        )
        header = jwt.get_unverified_header(token)
        if str(header.get("typ", "")).lower() not in {"at+jwt", "application/at+jwt"}:
            return {"active": False}
    except jwt.InvalidTokenError:
        return {"active": False}

    now = int(time.time())
    if any(not isinstance(claims[name], str) or not claims[name] for name in ("sub", "client_id", "jti")):
        return {"active": False}
    if type(claims["exp"]) is not int or type(claims["iat"]) is not int:
        return {"active": False}
    if claims["exp"] <= now or claims["iat"] > now or claims["jti"] in config.inactive_jtis:
        return {"active": False}
    scope = claims["scope"]
    if not isinstance(scope, str) or (scope and re.fullmatch(SCOPE_PATTERN, scope) is None):
        return {"active": False}
    audience = claims["aud"]
    if not isinstance(audience, str) and (
        not isinstance(audience, list)
        or not audience
        or any(not isinstance(item, str) or not item for item in audience)
    ):
        return {"active": False}
    return {
        "active": True,
        "client_id": claims["client_id"],
        "sub": claims["sub"],
        "iss": claims["iss"],
        "aud": audience,
        "exp": claims["exp"],
        "iat": claims["iat"],
        "scope": scope,
        "token_type": "Bearer",
    }


def build_app(config: AuthorizationServerConfig) -> Starlette:
    """설정한 조회 자격과 JWT 검사를 실제 HTTP 경로에 연결한다."""
    async def introspect(request: Request) -> JSONResponse:
        """조회자를 인증한 뒤 JWT의 현재 상태를 응답한다."""
        try:
            authenticate_request(request, config)
            form = await read_introspection_form(request)
        except RequestError as error:
            headers = dict(CACHE_HEADERS)
            if error.status_code == 401:
                headers["WWW-Authenticate"] = 'Basic realm="introspection"'
            return JSONResponse(
                {"error": error.error}, status_code=error.status_code, headers=headers,
            )
        result = inspect_jwt(form["token"], config)
        return JSONResponse(result, headers=CACHE_HEADERS)

    return Starlette(routes=[Route("/oauth/introspect", introspect, methods=["POST"])])


def inspect_opaque(
    token: str,
    records: Mapping[str, dict[str, object]],
    *,
    resource: str = RESOURCE,
) -> dict[str, object]:
    """비교용으로, 조회 응답 필드를 저장한 발급 기록에서 불투명 토큰을 찾는다."""
    record = records.get(token)
    if record is None or record.get("active") is not True:
        return {"active": False}
    expires_at = record.get("exp")
    audience = record.get("aud")
    matches_resource = audience == resource or (
        isinstance(audience, list) and resource in audience
    )
    if type(expires_at) is not int or expires_at <= int(time.time()) or not matches_resource:
        return {"active": False}
    return dict(record)


def issue_example_token(
    private_key: rsa.RSAPrivateKey,
    *,
    issuer: str = ISSUER,
    resource: str | list[str] = RESOURCE,
    client_id: str = "report-reader",
    subject: str = "demo-user",
    scopes: tuple[str, ...] = ("reports:read",),
    lifetime: int = 300,
    jti: str | None = None,
) -> str:
    """메모리에서 공급한 개인키로 설명용 입력 JWT를 생성한다. 출력하지 않는다."""
    issued_at = int(time.time())
    return jwt.encode(
        {
            "iss": issuer, "sub": subject, "aud": resource,
            "exp": issued_at + lifetime, "iat": issued_at,
            "jti": jti or secrets.token_urlsafe(16),
            "client_id": client_id, "scope": " ".join(scopes),
        },
        private_key,
        algorithm="RS256",
        headers={"typ": "at+jwt"},
    )


if __name__ == "__main__":
    import uvicorn

    public_key = serialization.load_pem_public_key(os.environ["JWT_PUBLIC_KEY_PEM"].encode("utf-8"))
    config = AuthorizationServerConfig(
        public_key=public_key,
        introspection_client_secret=os.environ["INTROSPECTION_CLIENT_SECRET"],
        introspection_client_id=os.environ.get("INTROSPECTION_CLIENT_ID", INTROSPECTION_CLIENT_ID),
        issuer=os.environ.get("JWT_ISSUER", ISSUER),
        resource=os.environ.get("MCP_RESOURCE", RESOURCE),
    )
    uvicorn.run(build_app(config), host="127.0.0.1", port=9101, access_log=False)

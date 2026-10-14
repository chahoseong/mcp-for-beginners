"""Authorization Code + PKCE 토큰 발급을 설명하는 loopback 교육 예제."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import re
import secrets
import time
from dataclasses import dataclass
from html import escape
from urllib.parse import parse_qs, urlencode

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.routing import Route


ISSUER = "http://127.0.0.1:9001"
CLIENT_ID = "report-reader"
REDIRECT_URI = "http://127.0.0.1:9002/callback"
RESOURCE = "https://reports.example.com/mcp"
SCOPES = frozenset({"reports:read"})
CODE_LIFETIME = 120
TOKEN_LIFETIME = 300
CACHE_HEADERS = {"Cache-Control": "no-store", "Pragma": "no-cache"}
PAGE_HEADERS = {**CACHE_HEADERS, "Referrer-Policy": "no-referrer"}


@dataclass(frozen=True)
class RegisteredClient:
    client_id: str
    redirect_uri: str
    resource: str
    scopes: frozenset[str]


@dataclass(frozen=True)
class ConsentRequest:
    client_id: str
    user_id: str
    redirect_uri: str
    state: str
    resource: str
    scopes: frozenset[str]
    code_challenge: str
    code_challenge_method: str
    expires_at: int
    browser_session: str


@dataclass
class AuthorizationCode:
    client_id: str
    user_id: str
    redirect_uri: str
    resource: str
    scopes: frozenset[str]
    code_challenge: str
    code_challenge_method: str
    expires_at: int
    used: bool = False
    access_token: str | None = None


@dataclass(frozen=True)
class IssuedToken:
    client_id: str
    user_id: str
    issuer: str
    resource: str
    scopes: frozenset[str]
    issued_at: int
    expires_at: int


class OAuthError(Exception):
    """OAuth 오류 코드를 HTTP 처리 함수로 전달한다."""

    def __init__(self, error: str) -> None:
        super().__init__(error)
        self.error = error


clients = {CLIENT_ID: RegisteredClient(CLIENT_ID, REDIRECT_URI, RESOURCE, SCOPES)}
consent_requests: dict[str, ConsentRequest] = {}
code_records: dict[str, AuthorizationCode] = {}
token_records: dict[str, IssuedToken] = {}
issuance_lock = asyncio.Lock()


def read_parameters(encoded: str) -> dict[str, str]:
    """URL 인코딩된 입력을 읽고 잘못된 인코딩과 중복 값을 거부한다."""
    try:
        if re.search(r"%(?![0-9A-Fa-f]{2})", encoded):
            raise ValueError
        values = parse_qs(
            encoded, keep_blank_values=True, strict_parsing=True,
            encoding="utf-8", errors="strict",
        )
        if any(len(items) != 1 for items in values.values()):
            raise ValueError
        return {key: items[0] for key, items in values.items()}
    except (ValueError, UnicodeError) as error:
        raise OAuthError("invalid_request") from error


async def read_form(request: Request) -> dict[str, str]:
    """토큰 요청과 동의 폼의 본문을 읽는다."""
    media_type = request.headers.get("content-type", "").split(";", 1)[0]
    if media_type.strip().lower() != "application/x-www-form-urlencoded":
        raise OAuthError("invalid_request")
    try:
        encoded = (await request.body()).decode("utf-8")
    except UnicodeError as error:
        raise OAuthError("invalid_request") from error
    return read_parameters(encoded)


def error_response(error: OAuthError) -> JSONResponse:
    """토큰을 포함하지 않는 OAuth 오류 응답을 만든다."""
    return JSONResponse({"error": error.error}, status_code=400, headers=CACHE_HEADERS)


def authorization_response(
    redirect_uri: str, state: str, **parameters: str,
) -> RedirectResponse:
    """검증된 콜백 주소로 코드 또는 오류를 보낸다."""
    query = urlencode({**parameters, "state": state, "iss": ISSUER})
    return RedirectResponse(
        f"{redirect_uri}?{query}", status_code=303, headers=PAGE_HEADERS,
    )


def mock_login() -> str:
    """실제 로그인 시스템을 대신해 고정된 예제 사용자를 반환한다."""
    return "demo-user"


async def authorize(request: Request) -> HTMLResponse | JSONResponse | RedirectResponse:
    """등록 주소와 인가 요청을 확인하고 모의 사용자의 동의 화면을 만든다."""
    try:
        parameters = read_parameters(request.url.query)
    except OAuthError as error:
        return error_response(error)
    client = clients.get(parameters.get("client_id", ""))
    redirect_uri = parameters.get("redirect_uri", "")
    if client is None or redirect_uri != client.redirect_uri:
        return error_response(OAuthError("invalid_request"))
    state = parameters.get("state", "")
    try:
        if not state:
            raise OAuthError("invalid_request")
        if parameters.get("response_type") != "code":
            raise OAuthError("unsupported_response_type")
        if parameters.get("resource") != client.resource:
            raise OAuthError("invalid_target")
        scopes = frozenset(parameters.get("scope", "").split(" "))
        if "" in scopes or not scopes <= client.scopes:
            raise OAuthError("invalid_scope")
        challenge = parameters.get("code_challenge", "")
        if parameters.get("code_challenge_method") != "S256":
            raise OAuthError("invalid_request")
        if re.fullmatch(r"[A-Za-z0-9_-]{43}", challenge) is None:
            raise OAuthError("invalid_request")
    except OAuthError as error:
        return authorization_response(redirect_uri, state, error=error.error)

    user_id = mock_login()
    browser_session = request.cookies.get("pkce_as_browser") or secrets.token_urlsafe(32)
    ticket = secrets.token_urlsafe(32)
    consent_requests[ticket] = ConsentRequest(
        client_id=client.client_id, user_id=user_id,
        redirect_uri=redirect_uri, state=state, resource=client.resource,
        scopes=scopes, code_challenge=challenge, code_challenge_method="S256",
        expires_at=int(time.time()) + 300, browser_session=browser_session,
    )
    page = f"""<!doctype html><html lang="ko"><meta charset="utf-8">
    <title>예제 사용자 동의</title><h1>접근 권한 허용</h1>
    <p>모의 로그인으로 확인한 사용자: {escape(user_id)}</p>
    <p>실제 비밀번호나 사용자 인증 서비스를 사용하지 않습니다.</p>
    <p>애플리케이션: {escape(client.client_id)}</p>
    <p>MCP 서버 식별자: {escape(client.resource)}</p>
    <p>요청 권한: {escape(' '.join(sorted(scopes)))}</p>
    <form method="post" action="/oauth/consent">
    <input type="hidden" name="ticket" value="{escape(ticket, quote=True)}">
    <button name="decision" value="allow">허용</button>
    <button name="decision" value="deny">거부</button></form></html>"""
    response = HTMLResponse(page, headers=PAGE_HEADERS)
    response.set_cookie(
        "pkce_as_browser", browser_session, httponly=True, samesite="lax", max_age=300,
    )
    return response


def create_authorization_code(consent: ConsentRequest) -> str:
    """동의한 사용자·요청 정보에 연결된 일회용 인가 코드를 저장한다."""
    code = secrets.token_urlsafe(32)
    code_records[code] = AuthorizationCode(
        client_id=consent.client_id, user_id=consent.user_id,
        redirect_uri=consent.redirect_uri, resource=consent.resource,
        scopes=consent.scopes, code_challenge=consent.code_challenge,
        code_challenge_method=consent.code_challenge_method,
        expires_at=int(time.time()) + CODE_LIFETIME,
    )
    return code


async def consent_handler(request: Request) -> JSONResponse | RedirectResponse:
    """브라우저의 허용·거부 선택을 처리한다."""
    try:
        form = await read_form(request)
        ticket = form.get("ticket", "")
        consent = consent_requests.get(ticket)
        browser_session = request.cookies.get("pkce_as_browser", "")
        if (
            consent is None or consent.expires_at <= int(time.time())
            or not hmac.compare_digest(
                consent.browser_session.encode("utf-8"), browser_session.encode("utf-8"),
            )
            or form.get("decision") not in {"allow", "deny"}
        ):
            raise OAuthError("invalid_request")
        del consent_requests[ticket]
        if form["decision"] == "deny":
            return authorization_response(
                consent.redirect_uri, consent.state, error="access_denied",
            )
        code = create_authorization_code(consent)
        return authorization_response(consent.redirect_uri, consent.state, code=code)
    except OAuthError as error:
        return error_response(error)


def validate_code(form: dict[str, str]) -> AuthorizationCode:
    """코드에 저장한 발급 조건과 토큰 요청을 비교한다."""
    for name in ("grant_type", "client_id", "code", "redirect_uri", "code_verifier"):
        if not form.get(name):
            raise OAuthError("invalid_request")
    if form["grant_type"] != "authorization_code":
        raise OAuthError("unsupported_grant_type")
    if form["client_id"] not in clients:
        raise OAuthError("invalid_client")
    record = code_records.get(form["code"])
    if record is None or record.expires_at <= int(time.time()):
        raise OAuthError("invalid_grant")
    if record.used:
        if record.access_token is not None:
            token_records.pop(record.access_token, None)
        raise OAuthError("invalid_grant")
    if form["client_id"] != record.client_id or form["redirect_uri"] != record.redirect_uri:
        raise OAuthError("invalid_grant")
    if form.get("resource") != record.resource:
        raise OAuthError("invalid_target")
    verifier = form["code_verifier"]
    if re.fullmatch(r"[A-Za-z0-9._~-]{43,128}", verifier) is None:
        raise OAuthError("invalid_grant")
    calculated = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest(),
    ).rstrip(b"=").decode("ascii")
    if record.code_challenge_method != "S256" or not hmac.compare_digest(
        calculated, record.code_challenge,
    ):
        raise OAuthError("invalid_grant")
    return record


def create_and_store_token(record: AuthorizationCode) -> tuple[str, IssuedToken]:
    """검증한 코드의 사용자·권한으로 토큰과 발급 기록을 저장한다."""
    token = secrets.token_urlsafe(32)
    issued_at = int(time.time())
    token_record = IssuedToken(
        client_id=record.client_id, user_id=record.user_id, issuer=ISSUER,
        resource=record.resource, scopes=record.scopes, issued_at=issued_at,
        expires_at=issued_at + TOKEN_LIFETIME,
    )
    token_records[token] = token_record
    record.used = True
    record.access_token = token
    return token, token_record


async def issue_token(request: Request) -> JSONResponse:
    """인가 코드를 검사하고 불투명 접근 토큰을 발급한다."""
    try:
        form = await read_form(request)
        if request.headers.get("authorization") or "client_secret" in form:
            raise OAuthError("invalid_request")
        async with issuance_lock:
            record = validate_code(form)
            token, token_record = create_and_store_token(record)
        return JSONResponse(
            {
                "access_token": token, "token_type": "Bearer",
                "expires_in": max(0, token_record.expires_at - int(time.time())),
                "scope": " ".join(sorted(token_record.scopes)),
            },
            headers=CACHE_HEADERS,
        )
    except OAuthError as error:
        return error_response(error)


app = Starlette(routes=[
    Route("/oauth/authorize", authorize, methods=["GET"]),
    Route("/oauth/consent", consent_handler, methods=["POST"]),
    Route("/oauth/token", issue_token, methods=["POST"]),
])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=9001, access_log=False)

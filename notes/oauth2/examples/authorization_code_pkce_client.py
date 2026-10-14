"""Authorization Code + PKCE 콜백과 토큰 요청을 설명하는 loopback 교육 예제."""

from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets
import time
from dataclasses import dataclass
from html import escape
from urllib.parse import parse_qs, urlencode

import httpx2 as httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Route


ISSUER = "http://127.0.0.1:9001"
AUTHORIZATION_ENDPOINT = f"{ISSUER}/oauth/authorize"
TOKEN_ENDPOINT = f"{ISSUER}/oauth/token"
CLIENT_ID = "report-reader"
REDIRECT_URI = "http://127.0.0.1:9002/callback"
RESOURCE = "https://reports.example.com/mcp"
SCOPE = "reports:read"
PAGE_HEADERS = {"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"}


@dataclass(frozen=True)
class PendingAuthorization:
    state: str
    code_verifier: str
    issuer: str
    token_endpoint: str
    redirect_uri: str
    resource: str
    browser_session: str
    expires_at: int


@dataclass(frozen=True)
class SavedToken:
    access_token: str
    scope: str
    expires_at: int


class CallbackError(Exception):
    """클라이언트가 콜백 또는 토큰 응답을 거부한 이유를 전달한다."""


pending_requests: dict[str, PendingAuthorization] = {}
saved_tokens: dict[str, SavedToken] = {}


def page(message: str, status_code: int = 200) -> HTMLResponse:
    """코드와 토큰 문자열을 포함하지 않는 결과 화면을 만든다."""
    return HTMLResponse(
        f'<!doctype html><html lang="ko"><meta charset="utf-8">'
        f"<title>토큰 발급 예제</title><p>{escape(message)}</p>"
        '<a href="/start">새 인가 요청</a></html>',
        status_code=status_code, headers=PAGE_HEADERS,
    )


async def index(request: Request) -> HTMLResponse:
    """브라우저에서 시작할 수 있는 인가 요청 링크를 보여준다."""
    return page("Authorization Code + PKCE 토큰 발급 예제입니다.")


def s256(code_verifier: str) -> str:
    """검증값을 SHA-256과 패딩 없는 Base64url로 변환한다."""
    return base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode("ascii")).digest(),
    ).rstrip(b"=").decode("ascii")


async def start_authorization(request: Request) -> RedirectResponse:
    """요청별 state와 PKCE 정보를 보관하고 브라우저를 인가 서버로 보낸다."""
    state = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(32)
    browser_session = request.cookies.get("pkce_client_browser") or secrets.token_urlsafe(32)
    pending_requests[state] = PendingAuthorization(
        state=state, code_verifier=code_verifier, issuer=ISSUER,
        token_endpoint=TOKEN_ENDPOINT, redirect_uri=REDIRECT_URI,
        resource=RESOURCE, browser_session=browser_session,
        expires_at=int(time.time()) + 300,
    )
    parameters = {
        "response_type": "code", "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI, "state": state,
        "resource": RESOURCE, "scope": SCOPE,
        "code_challenge": s256(code_verifier), "code_challenge_method": "S256",
    }
    response = RedirectResponse(
        f"{AUTHORIZATION_ENDPOINT}?{urlencode(parameters)}", status_code=303,
        headers=PAGE_HEADERS,
    )
    response.set_cookie(
        "pkce_client_browser", browser_session,
        httponly=True, samesite="lax", max_age=300,
    )
    return response


def callback_parameters(request: Request) -> dict[str, str]:
    """콜백 쿼리에서 잘못된 인코딩과 중복 값을 거부한다."""
    try:
        encoded = request.url.query
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
        raise CallbackError("콜백 파라미터가 올바르지 않습니다.") from error


def validate_callback(
    request: Request, parameters: dict[str, str],
) -> PendingAuthorization:
    """응답을 처리하기 전에 요청별 state·브라우저·발급자를 확인한다."""
    state = parameters.get("state", "")
    pending = pending_requests.get(state)
    browser_session = request.cookies.get("pkce_client_browser", "")
    if (
        pending is None or pending.expires_at <= int(time.time())
        or not hmac.compare_digest(pending.state, state)
        or not hmac.compare_digest(
            pending.browser_session.encode("utf-8"), browser_session.encode("utf-8"),
        )
    ):
        raise CallbackError("시작한 인가 요청과 콜백이 일치하지 않습니다.")
    if parameters.get("iss") != pending.issuer:
        raise CallbackError("인가 응답의 발급자 식별자가 일치하지 않습니다.")
    del pending_requests[state]
    return pending


async def request_token(code: str, pending: PendingAuthorization) -> SavedToken:
    """미리 선택한 토큰 발급 주소로 코드와 검증값을 보낸다."""
    async with httpx.AsyncClient(timeout=10, trust_env=False) as http_client:
        response = await http_client.post(
            pending.token_endpoint,
            data={
                "grant_type": "authorization_code", "client_id": CLIENT_ID,
                "code": code, "redirect_uri": pending.redirect_uri,
                "code_verifier": pending.code_verifier, "resource": pending.resource,
            },
        )
    try:
        payload = response.json()
    except ValueError as error:
        raise CallbackError("토큰 응답의 JSON 형식이 올바르지 않습니다.") from error
    if not isinstance(payload, dict):
        raise CallbackError("토큰 응답 형식이 올바르지 않습니다.")
    if response.status_code != 200:
        error_code = payload.get("error", "unknown_error")
        raise CallbackError(f"인가 서버가 토큰 발급을 거부했습니다: {error_code}")
    token = payload.get("access_token")
    lifetime = payload.get("expires_in")
    scope = payload.get("scope")
    if (
        not isinstance(token, str) or not token
        or str(payload.get("token_type", "")).lower() != "bearer"
        or type(lifetime) is not int or lifetime <= 0
        or not isinstance(scope, str) or scope != SCOPE
    ):
        raise CallbackError("토큰 응답에 필요한 값이 올바르지 않습니다.")
    return SavedToken(token, scope, int(time.time()) + lifetime)


async def callback(request: Request) -> HTMLResponse | RedirectResponse:
    """인가 응답을 확인하고 코드를 토큰으로 교환한다."""
    try:
        parameters = callback_parameters(request)
        pending = validate_callback(request, parameters)
        if "error" in parameters:
            if "code" in parameters or not parameters["error"]:
                raise CallbackError("인가 응답 형식이 올바르지 않습니다.")
            if parameters["error"] == "access_denied":
                return page("사용자가 권한 요청을 거부했습니다. 토큰은 요청하지 않았습니다.")
            return page(f"인가 서버가 요청을 거부했습니다: {parameters['error']}", 400)
        code = parameters.get("code", "")
        if not code:
            raise CallbackError("인가 응답에 코드가 없습니다.")
        token = await request_token(code, pending)
        saved_tokens[pending.browser_session] = token
        return RedirectResponse("/result", status_code=303, headers=PAGE_HEADERS)
    except CallbackError as error:
        return page(str(error), 400)
    except httpx.HTTPError:
        return page("인가 서버의 토큰 요청을 완료하지 못했습니다.", 502)


async def result(request: Request) -> HTMLResponse:
    """토큰 문자열 대신 발급 완료 여부와 허용된 권한만 보여준다."""
    token = saved_tokens.get(request.cookies.get("pkce_client_browser", ""))
    if token is None or token.expires_at <= int(time.time()):
        return page("보관된 유효한 토큰이 없습니다.", 400)
    return page(f"접근 토큰을 메모리에 보관했습니다. 허용된 권한: {token.scope}")


app = Starlette(routes=[
    Route("/", index, methods=["GET"]),
    Route("/start", start_authorization, methods=["GET"]),
    Route("/callback", callback, methods=["GET"]),
    Route("/result", result, methods=["GET"]),
])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=9002, access_log=False)

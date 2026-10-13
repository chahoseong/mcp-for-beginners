"""Client Credentials 토큰 발급을 설명하는 독립 예제."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import re
import secrets
import time
from dataclasses import dataclass
from urllib.parse import parse_qs, unquote_plus

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

ISSUER = "https://login.example.com"
RESOURCE = "https://reports.example.com/mcp"
TOKEN_LIFETIME = 300


@dataclass(frozen=True)
class RegisteredApplication:
    client_id: str
    secret_digest: bytes
    grant_types: frozenset[str]
    resources: frozenset[str]
    scopes: frozenset[str]


applications = {
    "report-reader": RegisteredApplication(
        client_id="report-reader",
        secret_digest=hashlib.sha256(b"example-only-secret").digest(),
        grant_types=frozenset({"client_credentials"}),
        resources=frozenset({RESOURCE}),
        scopes=frozenset({"reports:read"}),
    )
}

class OAuthError(Exception):
    def __init__(self, error: str, status_code: int = 400) -> None:
        super().__init__(error)
        self.error = error
        self.status_code = status_code


async def issue_token(request: Request) -> JSONResponse:
    try:
        application = authenticate_client(request)
        form = await read_token_form(request)
        resource, scopes = check_issue_policy(application, form)
        token, record = create_and_store_token(application, resource, scopes)
    except OAuthError as error:
        return error_response(error)
    return success_response(token, record)

def authenticate_client(request: Request) -> RegisteredApplication:
    headers = request.headers.getlist("authorization")
    if len(headers) > 1:
        raise OAuthError("invalid_request")
    try:
        scheme, encoded = (headers[0] if headers else "").split()
        if scheme.lower() != "basic":
            raise ValueError
        decoded = base64.b64decode(encoded, validate=True).decode("ascii")
        client_part, separator, secret_part = decoded.partition(":")
        if not separator or re.search(r"%(?![0-9A-Fa-f]{2})", decoded):
            raise ValueError
        client_id = unquote_plus(client_part, encoding="utf-8", errors="strict")
        secret = unquote_plus(secret_part, encoding="utf-8", errors="strict")
    except (ValueError, binascii.Error, UnicodeError):
        raise OAuthError("invalid_client", 401) from None

    application = applications.get(client_id)
    supplied_digest = hashlib.sha256(secret.encode("utf-8")).digest()
    if application is None or not hmac.compare_digest(
        supplied_digest, application.secret_digest
    ):
        raise OAuthError("invalid_client", 401)
    return application

async def read_token_form(request: Request) -> dict[str, list[str]]:
    media_type = request.headers.get("content-type", "").split(";", 1)[0]
    if media_type.strip().lower() != "application/x-www-form-urlencoded":
        raise OAuthError("invalid_request")
    try:
        body = (await request.body()).decode("utf-8")
        if re.search(r"%(?![0-9A-Fa-f]{2})", body):
            raise ValueError
        form = parse_qs(
            body, keep_blank_values=True, strict_parsing=True,
            encoding="utf-8", errors="strict",
        )
    except (ValueError, UnicodeError):
        raise OAuthError("invalid_request") from None
    if any(len(values) != 1 for name, values in form.items() if name != "resource"):
        raise OAuthError("invalid_request")
    if "client_id" in form or "client_secret" in form:
        raise OAuthError("invalid_request")
    return form

def check_issue_policy(
    application: RegisteredApplication,
    form: dict[str, list[str]],
) -> tuple[str, frozenset[str]]:
    grant_type = form.get("grant_type", [""])[0]
    if not grant_type:
        raise OAuthError("invalid_request")
    if grant_type != "client_credentials":
        raise OAuthError("unsupported_grant_type")
    if grant_type not in application.grant_types:
        raise OAuthError("unauthorized_client")

    resources = form.get("resource", [])
    if not resources:
        raise OAuthError("invalid_request")
    if len(resources) != 1 or resources[0] not in application.resources:
        raise OAuthError("invalid_target")

    scopes = frozenset(form.get("scope", [""])[0].split(" "))
    if "" in scopes or not scopes <= application.scopes:
        raise OAuthError("invalid_scope")
    return resources[0], scopes

@dataclass(frozen=True)
class IssuedToken:
    client_id: str
    issuer: str
    resource: str
    scopes: frozenset[str]
    issued_at: int
    expires_at: int


token_records: dict[str, IssuedToken] = {}


def create_and_store_token(
    application: RegisteredApplication,
    resource: str,
    scopes: frozenset[str],
) -> tuple[str, IssuedToken]:
    token = secrets.token_urlsafe(32)
    issued_at = int(time.time())
    record = IssuedToken(
        client_id=application.client_id,
        issuer=ISSUER,
        resource=resource,
        scopes=scopes,
        issued_at=issued_at,
        expires_at=issued_at + TOKEN_LIFETIME,
    )
    token_records[token] = record
    return token, record

def success_response(token: str, record: IssuedToken) -> JSONResponse:
    return JSONResponse(
        {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": max(0, record.expires_at - int(time.time())),
            "scope": " ".join(sorted(record.scopes)),
        },
        status_code=200,
        headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
    )


def error_response(error: OAuthError) -> JSONResponse:
    headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}
    if error.error == "invalid_client":
        headers["WWW-Authenticate"] = 'Basic realm="token"'
    return JSONResponse(
        {"error": error.error},
        status_code=error.status_code,
        headers=headers,
    )


token_route = Route("/oauth/token", issue_token, methods=["POST"])


from starlette.applications import Starlette

app = Starlette(routes=[token_route])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=9000)

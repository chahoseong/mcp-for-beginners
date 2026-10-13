"""A loopback-only, in-memory OAuth service for the client-credentials lesson."""

import base64
import binascii
from dataclasses import dataclass
import secrets
import time
from urllib.parse import parse_qs, unquote

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn

from settings import (
    AUTH_PORT, HOST, INTROSPECTION_ENDPOINT, ISSUER, RESOURCE, SCOPE,
    TOKEN_ENDPOINT, required_setting, setup_logger,
)

logger = setup_logger("AS")
CLIENT_ID = required_setting("PRACTICE_CLIENT_ID")
CLIENT_SECRET = required_setting("PRACTICE_CLIENT_SECRET")
VERIFIER_ID = required_setting("PRACTICE_VERIFIER_ID")
VERIFIER_SECRET = required_setting("PRACTICE_VERIFIER_SECRET")


@dataclass(frozen=True)
class TokenRecord:
    client_id: str
    resource: str
    scope: str
    expires_at: int


tokens: dict[str, TokenRecord] = {}
NO_STORE = {"Cache-Control": "no-store", "Pragma": "no-cache"}


def authenticated_as(request: Request, client_id: str, secret: str) -> bool:
    """Check Basic credentials; never include received values in a log."""
    scheme, _, value = request.headers.get("authorization", "").partition(" ")
    if scheme.lower() != "basic":
        return False
    try:
        decoded = base64.b64decode(value, validate=True).decode("utf-8")
        provided_id, separator, provided_secret = decoded.partition(":")
        return bool(separator) and secrets.compare_digest(
            unquote(provided_id).encode(), client_id.encode()
        ) and secrets.compare_digest(unquote(provided_secret).encode(), secret.encode())
    except (ValueError, UnicodeError, binascii.Error):
        return False


async def form_values(request: Request) -> dict[str, str] | None:
    """Read the small form used in this lesson without a multipart dependency."""
    if request.headers.get("content-type", "").split(";")[0].strip() != "application/x-www-form-urlencoded":
        return None
    try:
        values = parse_qs((await request.body()).decode("utf-8"), keep_blank_values=True)
    except (ValueError, UnicodeError):
        return None
    if any(len(value) != 1 for value in values.values()):
        return None
    return {key: value[0] for key, value in values.items()}


def oauth_error(code: str, description: str, status: int = 400) -> JSONResponse:
    headers = dict(NO_STORE)
    if status == 401:
        headers["WWW-Authenticate"] = 'Basic realm="oauth-practice"'
    return JSONResponse(
        {"error": code, "error_description": description},
        status_code=status, headers=headers,
    )


async def metadata(request: Request) -> JSONResponse:
    logger.info("Metadata served: issuer=%s token_endpoint=%s", ISSUER, TOKEN_ENDPOINT)
    return JSONResponse({
        "issuer": ISSUER,
        # SDK 2.3.0 requires this field even for client-credentials-only services.
        "authorization_endpoint": ISSUER + "/oauth2/authorize",
        "token_endpoint": TOKEN_ENDPOINT,
        "introspection_endpoint": INTROSPECTION_ENDPOINT,
        "grant_types_supported": ["client_credentials"],
        "response_types_supported": [],
        "token_endpoint_auth_methods_supported": ["client_secret_basic"],
        "introspection_endpoint_auth_methods_supported": ["client_secret_basic"],
        "scopes_supported": [SCOPE],
    })


async def unsupported_authorization(request: Request) -> JSONResponse:
    """Reject browser grants without redirecting to an unvalidated callback."""
    return oauth_error("unsupported_response_type", "Browser grants are not supported by this lesson.")


async def issue_token(request: Request) -> JSONResponse:
    if not authenticated_as(request, CLIENT_ID, CLIENT_SECRET):
        logger.warning("Token request rejected: invalid_client")
        return oauth_error("invalid_client", "Client authentication failed.", 401)
    form = await form_values(request)
    if form is None:
        return oauth_error("invalid_request", "Expected a form with single-valued parameters.")
    if form.get("grant_type") != "client_credentials":
        return oauth_error("unsupported_grant_type", "Only client_credentials is supported.")
    if form.get("resource") != RESOURCE:
        logger.warning("Token request rejected: invalid_target")
        return oauth_error("invalid_target", "This service only issues tokens for the quote MCP server.")
    requested_scopes = form.get("scope", "").split()
    if requested_scopes != [SCOPE]:
        return oauth_error("invalid_scope", "Request quote:read for this registered client.")

    now = int(time.time())
    for expired in [value for value, record in tokens.items() if record.expires_at <= now]:
        del tokens[expired]
    token = secrets.token_urlsafe(32)
    tokens[token] = TokenRecord(CLIENT_ID, RESOURCE, SCOPE, now + 3600)
    logger.info("Token issued: client_id=%s resource=%s scope=%s", CLIENT_ID, RESOURCE, SCOPE)
    return JSONResponse({
        "access_token": token, "token_type": "Bearer", "expires_in": 3600, "scope": SCOPE,
    }, headers=NO_STORE)


async def introspect(request: Request) -> JSONResponse:
    if not authenticated_as(request, VERIFIER_ID, VERIFIER_SECRET):
        return oauth_error("invalid_client", "Verifier authentication failed.", 401)
    form = await form_values(request)
    if form is None:
        return oauth_error("invalid_request", "Expected a token form.")
    record = tokens.get(form.get("token", ""))
    if record is None or record.expires_at <= int(time.time()):
        logger.info("Introspection: active=False")
        return JSONResponse({"active": False}, headers=NO_STORE)
    logger.info("Introspection: active=True resource=%s", record.resource)
    return JSONResponse({
        "active": True, "client_id": record.client_id, "iss": ISSUER,
        "aud": record.resource, "scope": record.scope, "exp": record.expires_at,
    }, headers=NO_STORE)


app = Starlette(routes=[
    Route("/.well-known/oauth-authorization-server", metadata),
    Route("/oauth2/authorize", unsupported_authorization),
    Route("/oauth2/token", issue_token, methods=["POST"]),
    Route("/oauth2/introspect", introspect, methods=["POST"]),
])

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=AUTH_PORT, log_level="warning")

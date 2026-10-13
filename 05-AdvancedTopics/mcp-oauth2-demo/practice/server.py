"""Protect one MCP tool and verify opaque tokens through the local issuer."""

from contextlib import asynccontextmanager
import time

import anyio
import httpx2
from mcp.server import MCPServer
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings

from settings import (
    HOST, INTROSPECTION_ENDPOINT, ISSUER, MCP_PORT, RESOURCE, SCOPE,
    required_setting, setup_logger,
)

logger = setup_logger("MCP")


class IntrospectionVerifier(TokenVerifier):
    """Reuse the server-owned HTTP client; return validated token attributes."""
    def __init__(self) -> None:
        self.http_client: httpx2.AsyncClient | None = None
        self.credentials = httpx2.BasicAuth(
            required_setting("PRACTICE_VERIFIER_ID"),
            required_setting("PRACTICE_VERIFIER_SECRET"),
        )

    async def verify_token(self, token: str) -> AccessToken | None:
        if self.http_client is None:
            raise RuntimeError("Server lifespan has not prepared the HTTP client.")
        try:
            response = await self.http_client.post(
                INTROSPECTION_ENDPOINT, auth=self.credentials, data={"token": token},
            )
        except httpx2.RequestError as exc:
            logger.error("Introspection unavailable: exception_type=%s", type(exc).__name__)
            return None
        if response.status_code != 200:
            logger.error("Introspection rejected: HTTP %s", response.status_code)
            return None
        data = response.json()
        if not data.get("active"):
            logger.info("Token rejected: inactive")
            return None
        if data.get("iss") != ISSUER or data.get("exp", 0) <= time.time():
            logger.info("Token rejected: issuer or expiry")
            return None
        logger.info("Token verified: client_id=%s resource=%s", data["client_id"], data["aud"])
        return AccessToken(
            token=token, client_id=data["client_id"], scopes=data["scope"].split(),
            expires_at=data["exp"], resource=data["aud"], claims={"iss": data["iss"]},
        )


verifier = IntrospectionVerifier()


@asynccontextmanager
async def lifespan(server: MCPServer):
    http_client = httpx2.AsyncClient(timeout=5.0)
    verifier.http_client = http_client
    logger.info("Ready: resource=%s issuer=%s", RESOURCE, ISSUER)
    try:
        yield
    finally:
        with anyio.move_on_after(2, shield=True):
            await http_client.aclose()
        verifier.http_client = None


mcp = MCPServer(
    "oauth-practice", lifespan=lifespan,
    token_verifier=verifier,
    auth=AuthSettings(
        issuer_url=ISSUER, resource_server_url=RESOURCE,
        required_scopes=[SCOPE], validate_token_resource=True,
    ),
)


@mcp.tool()
def get_quote() -> dict[str, str | int]:
    """Read a fixed demonstration quote after the HTTP authorization check."""
    logger.info("Tool executed: get_quote")
    return {"product": "demo-product", "quantity": 2, "total": "20.00", "currency": "USD"}


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host=HOST, port=MCP_PORT)

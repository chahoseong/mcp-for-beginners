import logging
import os
import jwt
from datetime import datetime, timezone

from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver import MCPServer
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.mcpserver.exceptions import ToolError


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
)
logger = logging.getLogger("auth-practice")

ISSUER = "https://auth.example.com"
RESOURCE_URL = "http://127.0.0.1:8000/mcp"
SIGNING_KEY = os.environ["JWT_SIGNING_KEY"]

if not SIGNING_KEY:
    raise RuntimeError("JWT_SIGNING_KEY가 비어 있습니다.")


ROLE_SCOPES = {
    "reader": ["mcp:access", "time:read"],
    "admin": ["mcp:access", "time:read", "message:write"],
    "operator": ["mcp:access", "message:write"],
}


class JWTTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            claims = jwt.decode(
                token,
                SIGNING_KEY,
                algorithms=["HS256"],
                issuer=ISSUER,
                audience=RESOURCE_URL,
                options={
                    "require": ["iss", "aud", "sub", "iat", "exp", "role"],
                },
            )

            role = claims["role"]
            if not isinstance(role, str):
                raise jwt.InvalidTokenError("role must be a string")
        
        except jwt.InvalidTokenError as exc:
            logger.warning(
                "JWT rejected: %s",
                type(exc).__name__,
            )
            return None

        logger.info(
            "JWT accepted: subject=%s role=%s",
            claims["sub"],
            role,
        )
        return AccessToken(
            token=token,
            client_id="practice-client",
            scopes=ROLE_SCOPES.get(role, []),
            subject=claims["sub"],
            expires_at=int(claims["exp"]),
            resource=RESOURCE_URL,
            claims=claims,
        )


mcp = MCPServer(
    "auth-practice",
    token_verifier=JWTTokenVerifier(),
    auth=AuthSettings(
        issuer_url=ISSUER,
        resource_server_url=RESOURCE_URL,
        validate_token_resource=True,
        required_scopes=["mcp:access"],
    ),
)


def require_scope(required_scope: str) -> None:
    access_token = get_access_token()

    if access_token is None or required_scope not in access_token.scopes:
        logger.warning("Tool denied: requires %s", required_scope)
        raise ToolError(f"Missing required scope: {required_scope}")


@mcp.tool()
def get_time() -> str:
    """Return the current UTC time."""
    require_scope("time:read")
    logger.info("get_time executed")
    return datetime.now(timezone.utc).isoformat()


server_state = {"message": ""}


@mcp.tool()
def set_message(message: str) -> str:
    """Set the server's in-memory message."""
    require_scope("message:write")

    server_state["message"] = message
    logger.info("set_message executed")
    return f"Message updated: {message}"


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000,
        stateless_http=True,
        json_response=True,
    )
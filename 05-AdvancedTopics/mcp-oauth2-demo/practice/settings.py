"""Fixed loopback endpoints and separately registered learning clients."""

import logging
import os

HOST = "127.0.0.1"
AUTH_PORT = 9100
MCP_PORT = 8100
ISSUER = f"http://{HOST}:{AUTH_PORT}"
RESOURCE = f"http://{HOST}:{MCP_PORT}/mcp"
TOKEN_ENDPOINT = f"{ISSUER}/oauth2/token"
INTROSPECTION_ENDPOINT = f"{ISSUER}/oauth2/introspect"
SCOPE = "quote:read"


def required_setting(name: str) -> str:
    """Read a credential supplied by uv's --env-file option."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing {name}. Run prepare_env.py, then use uv run --env-file .env."
        )
    return value


def setup_logger(name: str) -> logging.Logger:
    """Keep observations on stderr and avoid logging credential-bearing payloads."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(f"{name} | %(message)s"))
        logger.addHandler(handler)
    return logger

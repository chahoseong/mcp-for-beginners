import os
from datetime import datetime, timedelta, timezone
from importlib.metadata import version
from pathlib import Path

import jwt

import argparse


ISSUER = "https://auth.example.com"
AUDIENCE = "http://127.0.0.1:8000/mcp"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--case",
    choices=["valid", "expired", "wrong-issuer", "wrong-audience"],
    default="valid",
)
parser.add_argument(
    "--role",
    choices=["reader", "admin", "operator", "visitor"],
    default="reader",
)
args = parser.parse_args()

now = datetime.now(timezone.utc)
expires_at = (
    now - timedelta(seconds=30)
    if args.case == "expired"
    else now + timedelta(hours=1)
)

payload = {
    "iss": ISSUER,
    "aud": AUDIENCE,
    "sub": "mina",
    "iat": now,
    "exp": expires_at,
    "role": args.role,
}

if args.case == "wrong-issuer":
    payload["iss"] = "https://other-auth.example.com"

elif args.case == "wrong-audience":
    payload["aud"] = "http://127.0.0.1:9000/mcp"

token = jwt.encode(
    payload,
    os.environ["JWT_SIGNING_KEY"],
    algorithm="HS256",
)

# Client용 .env의 토큰만 교체하고 다른 설정은 보존합니다.
env_path = Path(__file__).resolve().parent.parent / ".env"
lines = (
    env_path.read_text(encoding="utf-8-sig").splitlines()
    if env_path.exists()
    else []
)
lines = [
    line for line in lines
    if not line.startswith("MCP_ACCESS_TOKEN=")
]
lines.append(f"MCP_ACCESS_TOKEN={token}")
env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("PyJWT:", version("PyJWT"))
print("JWT saved to client .env")
print("Subject:", payload["sub"])
print("Expires at:", expires_at.isoformat())
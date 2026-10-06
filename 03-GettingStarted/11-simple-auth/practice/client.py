import json
import os
import base64

import httpx2

URL = "http://127.0.0.1:8000/mcp"

REQUEST = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "get_time",
        "arguments": {},
        "_meta": {
            "io.modelcontextprotocol/protocolVersion": "2026-07-28",
            "io.modelcontextprotocol/clientInfo": {
                "name": "auth-practice-client",
                "version": "1.0.0",
            },
            "io.modelcontextprotocol/clientCapabilities": {},
        },
    },
}

BASE_HEADERS = {
    "Accept": "application/json, text/event-stream",
    "MCP-Protocol-Version": "2026-07-28",
    "Mcp-Method": "tools/call",
    "Mcp-Name": "get_time",
}

valid_token = os.environ["MCP_ACCESS_TOKEN"]

header_part, payload_part, signature_part = valid_token.split(".")

# JWT payload는 Base64url로 표현된 JSON입니다.
# 내용을 읽는 것은 서명을 검증하는 것이 아닙니다.
padding = "=" * (-len(payload_part) % 4)
payload = json.loads(
    base64.urlsafe_b64decode(payload_part + padding)
)

payload["sub"] = "other-user"

changed_payload_part = base64.urlsafe_b64encode(
    json.dumps(payload).encode("utf-8")
).decode("ascii").rstrip("=")

tampered_token = ".".join([
    header_part,
    changed_payload_part,
    signature_part,
])

cases = [
    ("Configured JWT", valid_token),
]

with httpx2.Client(timeout=10.0) as client:
    for label, token in cases:
        headers = BASE_HEADERS.copy()

        if token is not None:
            headers["Authorization"] = f"Bearer {token}"

        response = client.post(
            URL,
            headers=headers,
            json=REQUEST,
        )

        print(f"\nCase: {label}")
        print("HTTP status:", response.status_code)
        print(
            json.dumps(
                response.json(),
                ensure_ascii=False,
                indent=2,
            )
        )
"""Show safe HTTP observations while the SDK discovers and obtains a token."""

import asyncio
from urllib.parse import parse_qs

import httpx2
from mcp import Client
from mcp.client.auth.extensions.client_credentials import ClientCredentialsOAuthProvider
from mcp.client.extension import advertise
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken

from settings import ISSUER, RESOURCE, SCOPE, TOKEN_ENDPOINT, required_setting


class InMemoryTokenStorage:
    def __init__(self) -> None:
        self.tokens: OAuthToken | None = None
        self.client_info: OAuthClientInformationFull | None = None

    async def get_tokens(self) -> OAuthToken | None:
        return self.tokens

    async def set_tokens(self, tokens: OAuthToken) -> None:
        self.tokens = tokens

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        return self.client_info

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        self.client_info = client_info


async def observe_request(request: httpx2.Request) -> None:
    print(f"CLIENT | {request.method} {request.url}")
    if str(request.url) == TOKEN_ENDPOINT and request.method == "POST":
        form = parse_qs(request.content.decode())
        for name in ("grant_type", "resource", "scope"):
            print(f"CLIENT | Token request {name}: {form.get(name, [''])[0]}")


async def observe_response(response: httpx2.Response) -> None:
    print(f"CLIENT | HTTP {response.status_code} from {response.request.url}")
    challenge = response.headers.get("www-authenticate")
    if challenge:
        print(f"CLIENT | WWW-Authenticate: {challenge}")
    if response.status_code == 200 and "/.well-known/" in response.request.url.path:
        await response.aread()
        metadata = response.json()
        for name in ("resource", "authorization_servers", "issuer", "token_endpoint"):
            if name in metadata:
                print(f"CLIENT | Metadata {name}: {metadata[name]}")
    elif response.status_code == 200 and str(response.request.url) == TOKEN_ENDPOINT:
        await response.aread()
        payload = response.json()
        print(f"CLIENT | Token received: {bool(payload.get('access_token'))} (value hidden)")
        print(f"CLIENT | Token scope: {payload.get('scope')}")


async def main() -> None:
    provider = ClientCredentialsOAuthProvider(
        server_url=RESOURCE, storage=InMemoryTokenStorage(),
        client_id=required_setting("PRACTICE_CLIENT_ID"),
        client_secret=required_setting("PRACTICE_CLIENT_SECRET"),
        issuer=ISSUER, scope=SCOPE,
    )
    async with httpx2.AsyncClient(
        auth=provider, timeout=httpx2.Timeout(10.0, read=30.0),
        event_hooks={"request": [observe_request], "response": [observe_response]},
    ) as http_client:
        transport = streamable_http_client(RESOURCE, http_client=http_client)
        async with Client(
            transport,
            extensions=[advertise("io.modelcontextprotocol/oauth-client-credentials")],
        ) as client:
            tools = await client.list_tools()
            print("CLIENT | Tools:", [tool.name for tool in tools.tools])
            result = await client.call_tool("get_quote", {})
            print("CLIENT | is_error:", result.is_error)
            print("CLIENT | structured_content:", result.structured_content)


if __name__ == "__main__":
    asyncio.run(main())

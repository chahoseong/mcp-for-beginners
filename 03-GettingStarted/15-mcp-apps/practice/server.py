from datetime import datetime, timezone
from pathlib import Path

from mcp.server.apps import Apps
from mcp.server.mcpserver import MCPServer

apps = Apps()
UI_URI = "ui://clock/app.html"

UI_HTML_PATH = Path(__file__).parent / "ui" / "dist" / "index.html"
APP_HTML = UI_HTML_PATH.read_text(encoding="utf-8")


@apps.tool(
    resource_uri=UI_URI,
    description="현재 서버 시간을 UTC로 반환합니다.",
)
def get_server_time() -> str:
    return datetime.now(timezone.utc).isoformat()


apps.add_html_resource(UI_URI, APP_HTML, title="서버 시간")


mcp = MCPServer("apps-practice", extensions=[apps])


FAQ = {
    "shipping": "배송은 영업일 기준 3~5일 걸립니다.",
    "return policy": "구매 후 30일 이내에 반품할 수 있습니다.",
    "warranty": "제조 결함에 대해 1년 보증을 제공합니다.",
}


@mcp.tool()
def get_faq(query: str = "shipping") -> str:
    """키워드로 배송, 반품, 보증 안내를 조회합니다."""
    key = query.strip().lower()
    return FAQ.get(key, "해당 항목의 안내가 없습니다.")

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=3001,
        stateless_http=True,
        json_response=True,
    )
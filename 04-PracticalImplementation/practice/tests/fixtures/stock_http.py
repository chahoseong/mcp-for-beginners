"""재고 Tool 테스트가 공유하는 모의 HTTP 응답. 운영 코드는 사용하지 않는다."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from unittest.mock import patch

import httpx

from app.tools import stock as stock_module


PRODUCT_RESPONSES = {
    "stock_five": {"id": 1, "stock": 5},
    "stock_zero": {"id": 1, "stock": 0},
    "id_missing": {"stock": 5},
    "id_string": {"id": "1", "stock": 5},
    "id_bool": {"id": True, "stock": 5},
    "id_negative": {"id": -1, "stock": 5},
    "id_float": {"id": 1.0, "stock": 5},
    "id_mismatch": {"id": 2, "stock": 5},
    "stock_missing": {"id": 1},
    "stock_string": {"id": 1, "stock": "5"},
    "stock_float": {"id": 1, "stock": 5.5},
    "stock_negative": {"id": 1, "stock": -1},
    "stock_bool": {"id": 1, "stock": True},
    "stock_null": {"id": 1, "stock": None},
    "top_list": [{"id": 1, "stock": 5}],
    "top_null": None,
}
HTTP_STATUSES = {
    "not_found": 404,
    "rate_limited": 429,
    "http_500": 500,
    "http_503": 503,
    "http_400": 400,
    "redirect": 302,
}
HTTP_EXCEPTIONS = {
    "read_timeout": httpx.ReadTimeout,
    "connect_timeout": httpx.ConnectTimeout,
    "write_timeout": httpx.WriteTimeout,
    "pool_timeout": httpx.PoolTimeout,
    "connect_failure": httpx.ConnectError,
    "read_failure": httpx.ReadError,
}

# 기대값은 설계에서 정한다. 운영 코드의 오류 분류 함수를 호출하지 않는다.
ERROR_CASES = [
    ("not_found", "PRODUCT_NOT_FOUND", False, "404"),
    ("read_timeout", "UPSTREAM_TIMEOUT", True, "제한 시간"),
    ("connect_timeout", "UPSTREAM_TIMEOUT", True, "제한 시간"),
    ("write_timeout", "UPSTREAM_TIMEOUT", True, "제한 시간"),
    ("pool_timeout", "UPSTREAM_TIMEOUT", True, "제한 시간"),
    ("connect_failure", "UPSTREAM_UNAVAILABLE", True, "통신"),
    ("read_failure", "UPSTREAM_UNAVAILABLE", True, "통신"),
    ("rate_limited", "UPSTREAM_UNAVAILABLE", True, "429"),
    ("http_500", "UPSTREAM_UNAVAILABLE", True, "500"),
    ("http_503", "UPSTREAM_UNAVAILABLE", True, "503"),
    ("http_400", "INVALID_RESPONSE", False, "400"),
    ("redirect", "INVALID_RESPONSE", False, "302"),
    ("invalid_json", "INVALID_RESPONSE", False, "JSON"),
    ("id_missing", "INVALID_RESPONSE", False, "id"),
    ("id_string", "INVALID_RESPONSE", False, "id"),
    ("id_bool", "INVALID_RESPONSE", False, "id"),
    ("id_negative", "INVALID_RESPONSE", False, "id"),
    ("id_float", "INVALID_RESPONSE", False, "id"),
    ("id_mismatch", "INVALID_RESPONSE", False, "상품"),
    ("stock_missing", "INVALID_RESPONSE", False, "stock"),
    ("stock_string", "INVALID_RESPONSE", False, "stock"),
    ("stock_float", "INVALID_RESPONSE", False, "stock"),
    ("stock_negative", "INVALID_RESPONSE", False, "stock"),
    ("stock_bool", "INVALID_RESPONSE", False, "stock"),
    ("stock_null", "INVALID_RESPONSE", False, "stock"),
    ("top_list", "INVALID_RESPONSE", False, "response"),
    ("top_null", "INVALID_RESPONSE", False, "response"),
]


@contextmanager
def mock_stock_http(
    scenario: str,
    on_request: Callable[[httpx.Request], None] | None = None,
) -> Iterator[None]:
    """실제 HTTPX 처리 경로를 사용하되 네트워크 transport만 대체한다."""
    known = (
        set(PRODUCT_RESPONSES) | set(HTTP_STATUSES) | set(HTTP_EXCEPTIONS)
        | {"invalid_json"}
    )
    if scenario not in known:
        raise ValueError(f"알 수 없는 테스트 시나리오: {scenario}")

    def handler(request: httpx.Request) -> httpx.Response:
        if on_request is not None:
            on_request(request)
        if scenario in HTTP_EXCEPTIONS:
            raise HTTP_EXCEPTIONS[scenario]("모의 통신 실패", request=request)
        if scenario in HTTP_STATUSES:
            return httpx.Response(
                HTTP_STATUSES[scenario], json={"error": "test"}
            )
        if scenario == "invalid_json":
            return httpx.Response(200, content=b"{invalid json")
        if scenario == "top_null":
            return httpx.Response(200, content=b"null")
        return httpx.Response(200, json=PRODUCT_RESPONSES[scenario])

    original_client = httpx.AsyncClient
    transport = httpx.MockTransport(handler)

    def client_factory(*args, **kwargs) -> httpx.AsyncClient:
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    with patch.object(stock_module.httpx, "AsyncClient", client_factory):
        yield

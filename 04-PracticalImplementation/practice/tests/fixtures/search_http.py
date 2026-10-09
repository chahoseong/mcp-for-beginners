"""검색 테스트의 HTTPX transport를 모의 응답으로 대체한다."""

from collections.abc import Callable, Generator
from contextlib import contextmanager
from unittest.mock import patch

import httpx

from app.tools import search as search_module


@contextmanager
def mock_search_http(
    handler: Callable[[httpx.Request], httpx.Response],
) -> Generator[list[httpx.Request], None, None]:
    """실제 HTTPX 요청 생성·응답 처리를 유지하며 요청을 기록한다."""
    requests: list[httpx.Request] = []

    def record_request(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    original_client = httpx.AsyncClient
    transport = httpx.MockTransport(record_request)

    def client_factory(*args, **kwargs) -> httpx.AsyncClient:
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    with patch.object(search_module.httpx, "AsyncClient", client_factory):
        yield requests

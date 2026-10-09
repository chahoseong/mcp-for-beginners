"""상품 검색의 결과·입력 제약·페이지 조회·실패 처리를 모의 HTTP로 검증한다."""

import json
from collections.abc import Callable
from copy import deepcopy
from unittest.mock import Mock

import httpx
import pytest
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.mcpserver.tools.base import Tool

from app.tools import search as search_module
from app.tools.search import search_products
from tests.fixtures.search_http import mock_search_http


pytestmark = pytest.mark.anyio
CATEGORY = "smartphones"


def _product(
    product_id: int = 1, title: str = "Alpha Phone", description: str = "Basic",
) -> dict[str, object]:
    """모의 API 상품을 구성한다."""
    return {
        "id": product_id, "title": title, "description": description,
        "category": CATEGORY,
    }


def _page(
    products: list[dict[str, object]], *, total: int | None = None, skip: int = 0,
) -> dict[str, object]:
    """모의 페이지의 원본 개수·위치를 구성한다."""
    return {
        "products": products,
        "total": len(products) if total is None else total,
        "skip": skip, "limit": len(products),
    }


def _handler(
    pages: dict[int, object], categories: object = None,
) -> Callable[[httpx.Request], httpx.Response]:
    """요청한 skip의 모의 페이지를 돌려주며 예상 밖 요청은 실패한다."""
    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/products/category-list":
            payload = [CATEGORY] if categories is None else categories
        else:
            assert request.url.path == f"/products/category/{CATEGORY}"
            payload = pages[int(request.url.params["skip"])]
        # HTTPX의 json=None은 null 본문을 만들지 않으므로 명시적으로 직렬화한다.
        return httpx.Response(200, content=json.dumps(payload).encode())

    return respond


async def test_search_products_keyword_omitted_returns_all_candidates() -> None:
    """
    Given: 두 상품이 있는 유효한 카테고리와 생략한 검색어.
    When: search_products를 실행한다.
    Then: API 순서와 설계 필드를 유지한 두 후보와 count 2를 반환한다.
    """
    products = [_product(2, "Beta"), _product(1, "Alpha")]
    with mock_search_http(_handler({0: _page(products)})):
        result = await search_products(CATEGORY)
    assert result == {
        "status": "ok",
        "products": [
            {"product_id": 2, "name": "Beta", "category": CATEGORY},
            {"product_id": 1, "name": "Alpha", "category": CATEGORY},
        ],
        "count": 2,
    }


@pytest.mark.parametrize(
    ("keyword", "expected_ids"),
    [
        ("", [1, 2, 3]), ("   ", [1, 2, 3]), ("  ALPHA  ", [1, 2]),
        ("strasse", [3]), ("missing", []),
    ],
)
async def test_search_products_keyword_conditions_returns_matching_candidates(
    keyword: str, expected_ids: list[int],
) -> None:
    """
    Given: 이름·설명에 일치 상품이 있으며 공백·대소문자·유니코드 검색어 조건.
    When: search_products에 검색어를 전달한다.
    Then: 두 필드의 포함 조건과 casefold 규칙으로 후보를 고르고 count를 반환한다.
    """
    products = [
        _product(1, "Alpha Phone"), _product(2, "Beta", "ALPHA camera"),
        _product(3, "Straße"),
    ]
    with mock_search_http(_handler({0: _page(products)})):
        result = await search_products(CATEGORY, keyword)
    assert result["status"] == "ok"
    assert [item["product_id"] for item in result["products"]] == expected_ids
    assert result["count"] == len(expected_ids)


async def test_search_products_category_without_products_returns_empty_result() -> None:
    """
    Given: 카테고리는 존재하지만 원본 상품의 total이 0인 정상 페이지.
    When: search_products를 실행한다.
    Then: 실패하지 않고 status ok, 빈 products, count 0을 반환한다.
    """
    with mock_search_http(_handler({0: _page([])})):
        result = await search_products(CATEGORY)
    assert result == {"status": "ok", "products": [], "count": 0}


async def test_search_products_later_page_match_returns_candidate() -> None:
    """
    Given: 현재 PAGE_SIZE만큼 채운 첫 페이지에는 일치 상품이 없다.
           다음 페이지에 검색어와 일치하는 상품 한 개가 있다.
    When: search_products로 needle을 검색한다.
    Then: 첫 페이지를 이유로 중단하지 않고 두 번째 페이지의 후보를 반환한다.
    """
    page_size = search_module.PAGE_SIZE
    matching_id = page_size + 1
    pages = {
        0: _page(
            [_product(i, "Other") for i in range(1, page_size + 1)],
            total=matching_id,
        ),
        page_size: _page(
            [_product(matching_id, "Needle")], total=matching_id, skip=page_size,
        ),
    }
    with mock_search_http(_handler(pages)):
        result = await search_products(CATEGORY, "needle")
    assert result == {
        "status": "ok",
        "products": [
            {"product_id": matching_id, "name": "Needle", "category": CATEGORY},
        ],
        "count": 1,
    }


@pytest.mark.parametrize(
    "scenario", ["last-page", "short-middle-page", "exact-multiple", "empty"],
)
async def test_search_products_paginated_response_sends_expected_http_requests(
    scenario: str,
) -> None:
    """
    Given: 현재 PAGE_SIZE를 기준으로 마지막 페이지·짧은 중간 페이지·
           정확한 페이지 배수·빈 카테고리 조건 중 하나의 응답을 제공한다.
    When: 모의 HTTP로 search_products를 실행한다.
    Then: 카테고리 목록을 먼저 GET으로 조회하고, 상품 페이지의 limit에는 설정한 크기를 전달한다.
          다음 요청의 skip은 검색어 일치 여부와 관계없이 조회한 상품 수만큼 증가한다.
          전체 상품 수에 도달하면 추가 페이지를 요청하지 않는다.
          모든 요청의 연결·읽기·쓰기·연결 풀 대기 제한 시간은 각각 10초로 설정된다.
    """
    page_size = search_module.PAGE_SIZE
    sizes = {
        "last-page": [page_size, 2],
        "short-middle-page": [2, 1],
        "exact-multiple": [page_size],
        "empty": [0],
    }[scenario]
    total = sum(sizes)
    pages = {}
    offsets = []
    offset = 0
    for size in sizes:
        offsets.append(offset)
        products = [_product(i) for i in range(offset + 1, offset + size + 1)]
        pages[offset] = _page(products, total=total, skip=offset)
        offset += size
    with mock_search_http(_handler(pages)) as requests:
        await search_products(CATEGORY, "not-found")

    assert len(requests) == 1 + len(sizes)
    assert str(requests[0].url) == "https://dummyjson.com/products/category-list"
    for request, skip in zip(requests[1:], offsets, strict=True):
        assert str(request.url.copy_with(query=None)) == (
            "https://dummyjson.com/products/category/smartphones"
        )
        assert dict(request.url.params) == {
            "limit": str(page_size), "skip": str(skip),
        }
    for request in requests:
        assert request.method == "GET"
        assert request.extensions["timeout"] == {
            "connect": 10.0, "read": 10.0, "write": 10.0, "pool": 10.0,
        }


INVALID_INPUT_CASES = [
    pytest.param({"category": CATEGORY, field: value}, field, id=f"{field}-{label}")
    for field in ("category", "keyword")
    for label, value in (
        ("integer", 3), ("float", 3.5), ("boolean", True), ("null", None),
        ("list", []), ("object", {}),
    )
] + [
    pytest.param({}, "category", id="missing-category"),
    pytest.param({"category": ""}, "category", id="empty-category"),
    pytest.param({"category": " \t\n "}, "category", id="blank-category"),
]


@pytest.mark.parametrize(("arguments", "invalid_field"), INVALID_INPUT_CASES)
async def test_search_products_invalid_arguments_raises_tool_error(
    arguments: dict[str, object], invalid_field: str,
) -> None:
    """
    Given: 잘못된 입력 타입·빈 카테고리·누락된 필수 인자.
    When: search_products로 생성한 SDK Tool에 인자를 전달한다.
    Then: 해당 인자의 ToolError를 발생시키며 HTTP 요청은 보내지 않는다.
    """
    tool = Tool.from_function(search_products)
    with mock_search_http(_handler({})) as requests:
        with pytest.raises(ToolError, match=invalid_field):
            await tool.run(arguments, context=Mock())
    assert requests == []


async def test_search_products_padded_arguments_returns_matching_candidate() -> None:
    """
    Given: 앞뒤 공백이 있는 카테고리와 검색어를 가진 정상 Tool 인자.
    When: 등록에 사용하는 SDK Tool로 search_products를 실행한다.
    Then: 공백을 제거한 조건으로 조회하고 일치 후보를 반환한다.
    """
    tool = Tool.from_function(search_products)
    with mock_search_http(_handler({0: _page([_product()])})):
        structured = await tool.run(
            {"category": " smartphones ", "keyword": " ALPHA "}, context=Mock(),
        )
    assert structured == {
        "status": "ok",
        "products": [{"product_id": 1, "name": "Alpha Phone", "category": CATEGORY}],
        "count": 1,
    }


async def test_search_products_unknown_category_raises_tool_error() -> None:
    """
    Given: 카테고리 목록에 없는 식별자.
    When: search_products로 해당 카테고리를 검색한다.
    Then: INVALID_INPUT 오류를 발생시키고 상품 페이지는 조회하지 않는다.
    """
    with mock_search_http(_handler({})) as requests:
        with pytest.raises(ToolError) as raised:
            await search_products("unknown")
    error = json.loads(str(raised.value))
    assert error["code"] == "INVALID_INPUT"
    assert error["retryable"] is False
    assert "unknown" in error["message"]
    assert len(requests) == 1


HTTP_FAILURES = [
    (httpx.ReadTimeout, "UPSTREAM_TIMEOUT", True),
    (httpx.ConnectTimeout, "UPSTREAM_TIMEOUT", True),
    (httpx.WriteTimeout, "UPSTREAM_TIMEOUT", True),
    (httpx.PoolTimeout, "UPSTREAM_TIMEOUT", True),
    (httpx.ConnectError, "UPSTREAM_UNAVAILABLE", True),
    (httpx.ReadError, "UPSTREAM_UNAVAILABLE", True),
    (429, "UPSTREAM_UNAVAILABLE", True), (500, "UPSTREAM_UNAVAILABLE", True),
    (503, "UPSTREAM_UNAVAILABLE", True), (404, "INVALID_RESPONSE", False),
    (400, "INVALID_RESPONSE", False), (302, "INVALID_RESPONSE", False),
    ("invalid-json", "INVALID_RESPONSE", False),
]


@pytest.mark.parametrize("stage", ["categories", "first-page", "second-page"])
@pytest.mark.parametrize(("failure", "expected_code", "retryable"), HTTP_FAILURES)
async def test_search_products_lookup_failure_raises_tool_error(
    stage: str, failure: object, expected_code: str, retryable: bool,
) -> None:
    """
    Given: 카테고리 목록·첫 페이지·후속 페이지 중 하나의 HTTP 실패 또는 잘못된 JSON.
    When: 앞선 단계에는 정상 응답을 제공하고 search_products를 실행한다.
    Then: 코드·메시지·재시도 정보가 있는 ToolError로 끝나며 부분 결과·재시도는 없다.
    """
    def handler(request: httpx.Request) -> httpx.Response:
        current = (
            "categories" if request.url.path.endswith("category-list")
            else "first-page" if request.url.params["skip"] == "0"
            else "second-page"
        )
        if current == stage:
            if isinstance(failure, type):
                raise failure("모의 통신 실패", request=request)
            if failure == "invalid-json":
                return httpx.Response(200, content=b"{invalid")
            return httpx.Response(failure, json={"error": "test"})
        if current == "categories":
            return httpx.Response(200, json=[CATEGORY])
        return httpx.Response(200, json=_page([_product()], total=2))

    with mock_search_http(handler) as requests:
        with pytest.raises(ToolError) as raised:
            await search_products(CATEGORY)
    error = json.loads(str(raised.value))
    assert set(error) == {"code", "message", "retryable"}
    assert error["code"] == expected_code
    assert error["retryable"] is retryable
    assert error["message"]
    expected_requests = {"categories": 1, "first-page": 2, "second-page": 3}[stage]
    assert len(requests) == expected_requests


@pytest.mark.parametrize("payload", [None, {}, "smartphones", [1], [True], [None], [""]])
async def test_search_products_invalid_category_response_raises_tool_error(
    payload: object,
) -> None:
    """
    Given: 목록이 아니거나 카테고리 식별자 타입·값이 잘못된 원본 응답.
    When: search_products를 실행한다.
    Then: INVALID_RESPONSE로 실패하고 상품 페이지는 요청하지 않는다.
    """
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=json.dumps(payload).encode())

    with mock_search_http(handler) as requests:
        with pytest.raises(ToolError) as raised:
            await search_products(CATEGORY)
    error = json.loads(str(raised.value))
    assert error["code"] == "INVALID_RESPONSE"
    assert error["retryable"] is False
    assert len(requests) == 1


INVALID_PRODUCT_FIELDS = [
    ("id", None), ("id", 0), ("id", -1), ("id", "1"), ("id", 1.0),
    ("id", True), ("title", None), ("title", ""), ("title", 3),
    ("description", None), ("description", 3), ("category", None),
    ("category", ""), ("category", 3), ("category", "laptops"),
]


@pytest.mark.parametrize(("field", "value"), INVALID_PRODUCT_FIELDS)
async def test_search_products_invalid_product_response_raises_tool_error(
    field: str, value: object,
) -> None:
    """
    Given: 필요한 상품 필드가 누락되거나 타입·범위·요청 카테고리가 잘못된 응답.
    When: search_products를 실행한다.
    Then: 후보를 반환하지 않고 INVALID_RESPONSE로 실패한다.
    """
    product = _product()
    if value is None:
        del product[field]
    else:
        product[field] = value
    with mock_search_http(_handler({0: _page([product])})):
        with pytest.raises(ToolError) as raised:
            await search_products(CATEGORY)
    error = json.loads(str(raised.value))
    assert error["code"] == "INVALID_RESPONSE"
    assert error["retryable"] is False


INVALID_PAGE_CASES = [
    pytest.param(field, value, id=f"{field}-{label}")
    for field in ("total", "skip", "limit")
    for label, value in (
        ("missing", None), ("negative", -1), ("string", "1"),
        ("float", 1.0), ("boolean", True),
    )
] + [
    pytest.param("products", None, id="missing-products"),
    pytest.param("products", {}, id="object-products"),
    pytest.param("products", [None], id="null-product"),
    pytest.param("skip", 1, id="wrong-skip"),
    pytest.param("total", 0, id="count-exceeds-total"),
    pytest.param("limit", 0, id="count-exceeds-limit"),
]


@pytest.mark.parametrize(("field", "value"), INVALID_PAGE_CASES)
async def test_search_products_invalid_page_response_raises_tool_error(
    field: str, value: object,
) -> None:
    """
    Given: 페이지 필드의 누락·타입·범위·위치·개수가 잘못된 응답.
    When: search_products를 실행한다.
    Then: INVALID_RESPONSE의 ToolError가 발생한다.
    """
    page = deepcopy(_page([_product()]))
    if value is None:
        del page[field]
    else:
        page[field] = value
    with mock_search_http(_handler({0: page})):
        with pytest.raises(ToolError) as raised:
            await search_products(CATEGORY)
    error = json.loads(str(raised.value))
    assert error["code"] == "INVALID_RESPONSE"
    assert error["retryable"] is False


async def test_search_products_page_limit_exceeds_configured_size_raises_tool_error() -> None:
    """
    Given: 응답 limit이 현재 PAGE_SIZE보다 1 크다.
    When: 상품 한 개를 포함한 페이지로 search_products를 실행한다.
    Then: 응답 limit이 요청 크기를 초과하므로 INVALID_RESPONSE로 실패한다.
    """
    page_size = search_module.PAGE_SIZE
    page = _page([_product()])
    page["limit"] = page_size + 1
    with mock_search_http(_handler({0: page})):
        with pytest.raises(ToolError) as raised:
            await search_products(CATEGORY)
    error = json.loads(str(raised.value))
    assert error["code"] == "INVALID_RESPONSE"
    assert error["retryable"] is False


@pytest.mark.parametrize("payload", [None, [], "invalid"])
async def test_search_products_non_object_page_raises_tool_error(
    payload: object,
) -> None:
    """
    Given: 상품 페이지의 최상위 값이 객체가 아닌 응답.
    When: search_products를 실행한다.
    Then: INVALID_RESPONSE로 실패한다.
    """
    with mock_search_http(_handler({0: payload})):
        with pytest.raises(ToolError) as raised:
            await search_products(CATEGORY)
    assert json.loads(str(raised.value))["code"] == "INVALID_RESPONSE"


@pytest.mark.parametrize(
    "scenario",
    ["total-changed", "empty-before-total", "duplicate-id", "invalid-product"],
)
async def test_search_products_inconsistent_later_page_raises_tool_error(
    scenario: str,
) -> None:
    """
    Given: 첫 페이지는 정상이지만 다음 페이지의 전체 개수·상품·진행 상태가 잘못됨.
    When: search_products가 두 페이지를 읽는다.
    Then: 일부 후보를 성공으로 반환하지 않고 INVALID_RESPONSE로 실패한다.
    """
    second = _page([_product(2)], total=2, skip=1)
    if scenario == "total-changed":
        second["total"] = 3
    elif scenario == "empty-before-total":
        second["products"] = []
        second["limit"] = 0
    elif scenario == "duplicate-id":
        second["products"] = [_product(1)]
    else:
        second["products"] = [{"id": 2}]
    pages = {0: _page([_product()], total=2), 1: second}
    with mock_search_http(_handler(pages)) as requests:
        with pytest.raises(ToolError) as raised:
            await search_products(CATEGORY)
    assert json.loads(str(raised.value))["code"] == "INVALID_RESPONSE"
    assert len(requests) == 3


@pytest.mark.parametrize("scenario", ["duplicate-id", "oversized-page"])
async def test_search_products_invalid_product_count_raises_tool_error(
    scenario: str,
) -> None:
    """
    Given: 한 페이지에 중복 상품 ID가 있거나 상품 수가 현재 PAGE_SIZE보다 1 많다.
    When: search_products를 실행한다.
    Then: INVALID_RESPONSE로 실패한다.
    """
    page_size = search_module.PAGE_SIZE
    products = (
        [_product(), _product()] if scenario == "duplicate-id"
        else [_product(i) for i in range(1, page_size + 2)]
    )
    with mock_search_http(_handler({0: _page(products)})):
        with pytest.raises(ToolError) as raised:
            await search_products(CATEGORY)
    assert json.loads(str(raised.value))["code"] == "INVALID_RESPONSE"

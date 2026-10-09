"""카테고리의 모든 페이지를 확인해 상품명·설명으로 후보를 검색한다."""

import json
from typing import Annotated, Literal, TypedDict
from urllib.parse import quote

import httpx
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import (
    BaseModel, Field, StringConstraints, TypeAdapter, ValidationError,
)


Category = Annotated[
    str, StringConstraints(strict=True, strip_whitespace=True, min_length=1),
]
Keyword = Annotated[str, StringConstraints(strict=True, strip_whitespace=True)]
PositiveInteger = Annotated[int, Field(strict=True, ge=1)]
NonNegativeInteger = Annotated[int, Field(strict=True, ge=0)]
NonEmptyString = Annotated[str, StringConstraints(strict=True, min_length=1)]
StrictString = Annotated[str, StringConstraints(strict=True)]
PRODUCT_API_URL = "https://dummyjson.com/products"
PAGE_SIZE = 20
HTTP_TIMEOUT_SECONDS = 10.0
SearchErrorCode = Literal[
    "INVALID_INPUT", "UPSTREAM_TIMEOUT", "UPSTREAM_UNAVAILABLE",
    "INVALID_RESPONSE",
]


class SearchProduct(BaseModel):
    """후보 구성과 검색어 비교에 필요한 원본 상품 필드."""

    id: PositiveInteger
    title: NonEmptyString
    description: StrictString
    category: NonEmptyString


class ProductPage(BaseModel):
    """상품 목록과 페이지 정보를 암시적인 타입 변환 없이 읽는다."""

    products: list[SearchProduct]
    total: NonNegativeInteger
    skip: NonNegativeInteger
    limit: NonNegativeInteger


class ProductCandidate(TypedDict):
    """후속 재고·견적 Tool에 전달할 후보."""

    product_id: int
    name: str
    category: str


class SearchResult(TypedDict):
    """모든 페이지 검색이 성공했을 때만 반환하는 결과."""

    status: Literal["ok"]
    products: list[ProductCandidate]
    count: int


def _search_error(
    code: SearchErrorCode, message: str, *, retryable: bool = False,
) -> ToolError:
    """기존 Tool과 같은 오류 정보를 예외 텍스트에 담는다."""
    return ToolError(json.dumps({
        "code": code, "message": message, "retryable": retryable,
    }, ensure_ascii=False))


async def _read_json(
    client: httpx.AsyncClient, url: str, *,
    params: dict[str, int] | None = None,
) -> object:
    """카테고리 목록·상품 페이지의 HTTP 실패를 같은 계약으로 전달한다."""
    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise _search_error(
            "UPSTREAM_TIMEOUT", "DummyJSON 상품 검색 제한 시간을 초과했습니다.",
            retryable=True,
        ) from exc
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status == 429 or 500 <= status <= 599:
            raise _search_error(
                "UPSTREAM_UNAVAILABLE",
                f"DummyJSON을 일시적으로 이용할 수 없습니다 (HTTP {status}).",
                retryable=True,
            ) from exc
        raise _search_error(
            "INVALID_RESPONSE",
            f"DummyJSON이 예상하지 않은 HTTP {status} 응답을 반환했습니다.",
        ) from exc
    except httpx.RequestError as exc:
        raise _search_error(
            "UPSTREAM_UNAVAILABLE", "DummyJSON 상품 검색 중 통신에 실패했습니다.",
            retryable=True,
        ) from exc

    try:
        return response.json()
    except ValueError as exc:
        raise _search_error(
            "INVALID_RESPONSE", "DummyJSON 응답을 JSON으로 해석할 수 없습니다.",
        ) from exc


async def search_products(
    category: Category, keyword: Keyword = "",
) -> SearchResult:
    """카테고리 전체에서 상품명·설명에 검색어가 포함된 후보를 찾는다."""
    # SDK 경유 호출에서는 이미 정규화되지만 직접 호출도 같은 검색 규칙을 쓴다.
    category = category.strip()
    keyword = keyword.strip().casefold()
    products: list[SearchProduct] = []
    seen_ids: set[int] = set()
    total: int | None = None
    skip = 0

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
        payload = await _read_json(client, f"{PRODUCT_API_URL}/category-list")
        try:
            categories = TypeAdapter(list[NonEmptyString]).validate_python(
                payload, strict=True,
            )
        except ValidationError as exc:
            raise _search_error(
                "INVALID_RESPONSE", "DummyJSON 카테고리 목록이 올바르지 않습니다.",
            ) from exc
        if category not in categories:
            raise _search_error(
                "INVALID_INPUT", f"존재하지 않는 카테고리입니다: {category}",
            )

        url = f"{PRODUCT_API_URL}/category/{quote(category, safe='')}"
        while total is None or skip < total:
            payload = await _read_json(
                client, url, params={"limit": PAGE_SIZE, "skip": skip},
            )
            try:
                page = ProductPage.model_validate(payload, strict=True)
            except ValidationError as exc:
                raise _search_error(
                    "INVALID_RESPONSE",
                    "DummyJSON 상품 또는 페이지 필드가 누락되거나 올바르지 않습니다.",
                ) from exc

            if page.skip != skip or (total is not None and page.total != total):
                raise _search_error(
                    "INVALID_RESPONSE", "DummyJSON 페이지 위치 또는 전체 개수가 일치하지 않습니다.",
                )
            total = page.total
            size = len(page.products)
            if (
                size > PAGE_SIZE or page.limit > PAGE_SIZE or size > page.limit
                or skip + size > total or (size == 0 and skip < total)
            ):
                raise _search_error(
                    "INVALID_RESPONSE", "DummyJSON 페이지의 상품 수가 올바르지 않습니다.",
                )
            for product in page.products:
                if product.category != category or product.id in seen_ids:
                    raise _search_error(
                        "INVALID_RESPONSE", "DummyJSON 상품 카테고리가 다르거나 상품 ID가 중복됩니다.",
                    )
                seen_ids.add(product.id)
            products.extend(page.products)
            skip += size

    candidates: list[ProductCandidate] = [
        {"product_id": product.id, "name": product.title,
         "category": product.category}
        for product in products
        if not keyword or keyword in product.title.casefold()
        or keyword in product.description.casefold()
    ]
    return {"status": "ok", "products": candidates, "count": len(candidates)}

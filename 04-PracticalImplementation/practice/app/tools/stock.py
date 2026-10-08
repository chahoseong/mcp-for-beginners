"""재고 Tool의 입력 제약, DummyJSON 조회, 성공 결과와 예상 오류 처리."""

import json
from datetime import UTC, datetime
from typing import Annotated, Literal, TypedDict

import httpx
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel, Field, ValidationError


# 서버의 Tool 선언과 단위 테스트가 동일한 입력 제약을 사용한다.
PositiveInteger = Annotated[int, Field(strict=True, ge=1)]
NonNegativeInteger = Annotated[int, Field(strict=True, ge=0)]
PRODUCT_API_URL = "https://dummyjson.com/products"
HTTP_TIMEOUT_SECONDS = 10.0
StockErrorCode = Literal[
    "PRODUCT_NOT_FOUND",
    "UPSTREAM_TIMEOUT",
    "UPSTREAM_UNAVAILABLE",
    "INVALID_RESPONSE",
]


class ProductStock(BaseModel):
    """재고 조회에 필요한 원본 필드만 엄격하게 읽는다."""

    id: PositiveInteger
    stock: NonNegativeInteger


class StockResult(TypedDict):
    """설계의 재고 조회 성공 필드. 조회 실패에는 사용하지 않는다."""

    status: Literal["ok"]
    product_id: int
    requested_quantity: int
    stock: int
    in_stock: bool
    checked_at: str


def build_stock_result(
    product_id: int,
    quantity: int,
    stock: int,
    checked_at: datetime,
) -> StockResult:
    """검증된 데이터로 재고를 판단한다. I/O나 현재 시각 조회는 하지 않는다."""
    return {
        "status": "ok",
        "product_id": product_id,
        "requested_quantity": quantity,
        "stock": stock,
        "in_stock": stock >= quantity,
        "checked_at": checked_at.astimezone(UTC).isoformat(),
    }


def _stock_error(
    code: StockErrorCode, message: str, *, retryable: bool = False
) -> ToolError:
    """모델이 읽을 오류 정보를 ToolError 텍스트에 담는다."""
    return ToolError(json.dumps({
        "code": code,
        "message": message,
        "retryable": retryable,
    }, ensure_ascii=False))


async def fetch_product_stock(product_id: int) -> int:
    """상품 재고를 조회하고 예상한 조회 실패를 ToolError로 전달한다."""
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
            response = await client.get(f"{PRODUCT_API_URL}/{product_id}")
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise _stock_error(
            "UPSTREAM_TIMEOUT", "DummyJSON 재고 조회 제한 시간을 초과했습니다.",
            retryable=True,
        ) from exc
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status == 404:
            raise _stock_error(
                "PRODUCT_NOT_FOUND",
                f"상품 ID {product_id}를 찾을 수 없습니다 (HTTP 404).",
            ) from exc
        if status == 429 or 500 <= status <= 599:
            raise _stock_error(
                "UPSTREAM_UNAVAILABLE",
                f"DummyJSON을 일시적으로 이용할 수 없습니다 (HTTP {status}).",
                retryable=True,
            ) from exc
        raise _stock_error(
            "INVALID_RESPONSE",
            f"DummyJSON이 예상하지 않은 HTTP {status} 응답을 반환했습니다.",
        ) from exc
    except httpx.RequestError as exc:
        raise _stock_error(
            "UPSTREAM_UNAVAILABLE", "DummyJSON 재고 조회 중 통신에 실패했습니다.",
            retryable=True,
        ) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise _stock_error(
            "INVALID_RESPONSE", "DummyJSON 응답을 JSON으로 해석할 수 없습니다.",
        ) from exc

    try:
        product = ProductStock.model_validate(payload)
    except ValidationError as exc:
        fields = sorted({
            str(error["loc"][0]) if error["loc"] else "response"
            for error in exc.errors()
        })
        raise _stock_error(
            "INVALID_RESPONSE",
            "DummyJSON 응답 필드가 누락되거나 올바르지 않습니다: "
            + ", ".join(fields),
        ) from exc
    if product.id != product_id:
        raise _stock_error(
            "INVALID_RESPONSE", "DummyJSON 응답의 상품 ID가 요청과 일치하지 않습니다.",
        )
    return product.stock


async def check_stock(
    product_id: PositiveInteger,
    quantity: PositiveInteger,
) -> StockResult:
    """상품의 현재 재고가 요청 수량 이상인지 확인한다. 재고를 예약하지 않는다."""
    stock = await fetch_product_stock(product_id)
    return build_stock_result(product_id, quantity, stock, datetime.now(UTC))

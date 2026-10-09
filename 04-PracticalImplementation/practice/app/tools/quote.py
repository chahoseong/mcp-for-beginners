"""상품 가격을 조회·검증하고 서버 정책으로 견적 금액을 계산한다."""

import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal, DecimalException
from typing import Annotated, Literal, TypedDict

import httpx
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import (
    AfterValidator, BaseModel, Field, StringConstraints, ValidationError,
)

from app import policy


PositiveInteger = Annotated[int, Field(strict=True, ge=1)]
PositiveFloat = Annotated[float, Field(strict=True, gt=0, allow_inf_nan=False)]
NonNegativeInteger = Annotated[int, Field(strict=True, ge=0)]
NonNegativeFloat = Annotated[float, Field(strict=True, ge=0, allow_inf_nan=False)]
NonNegativeNumber = NonNegativeInteger | NonNegativeFloat
DiscountPercentage = (
    Annotated[int, Field(strict=True, ge=0, le=100)]
    | Annotated[float, Field(strict=True, ge=0, le=100, allow_inf_nan=False)]
)
NonEmptyString = Annotated[
    str, StringConstraints(strict=True, strip_whitespace=True, min_length=1),
]
NonNegativeDecimal = Annotated[
    Decimal, Field(strict=True, ge=0, allow_inf_nan=False),
]
PRODUCT_API_URL = "https://dummyjson.com/products"
HTTP_TIMEOUT_SECONDS = 10.0
QuoteErrorCode = Literal[
    "PRODUCT_NOT_FOUND", "UPSTREAM_TIMEOUT", "UPSTREAM_UNAVAILABLE",
    "INVALID_RESPONSE", "POLICY_UNAVAILABLE",
]


def _validate_budget_precision(value: int | float) -> int | float:
    """SDK 입력 검증에서 소수 셋째 자리 예산을 반올림하지 않고 거절한다."""
    exponent = Decimal(str(value)).as_tuple().exponent
    if not isinstance(exponent, int) or exponent < -2:
        raise ValueError("budget은 소수 둘째 자리까지 입력해야 합니다.")
    return value


PositiveBudget = Annotated[
    PositiveInteger | PositiveFloat,
    AfterValidator(_validate_budget_precision),
    Field(json_schema_extra={"multipleOf": 0.01}),
]


class QuoteProduct(BaseModel):
    """견적에 필요한 원본 상품 필드. 가격·할인율은 숫자로만 받는다."""

    id: PositiveInteger
    title: NonEmptyString
    price: NonNegativeNumber
    discountPercentage: DiscountPercentage


class QuotePolicy(BaseModel):
    """정책 원본에서 읽은 값의 타입·범위를 검증한다."""

    policy_version: NonEmptyString
    currency: NonEmptyString
    shipping_fee: NonNegativeDecimal
    tax_rate: NonNegativeDecimal
    money_decimal_places: NonNegativeInteger
    rounding: Literal[
        "ROUND_05UP", "ROUND_CEILING", "ROUND_DOWN", "ROUND_FLOOR", "ROUND_HALF_DOWN",
        "ROUND_HALF_EVEN", "ROUND_HALF_UP", "ROUND_UP",
    ]
    validity_days: PositiveInteger
    discount_field: Literal["discountPercentage"]


class QuoteResult(TypedDict):
    """견적 계산 성공 결과. 예산 초과도 이 결과로 표현한다."""

    status: Literal["ok"]
    product_id: int
    name: str
    quantity: int
    currency: str
    unit_price: int | float
    discount_percentage: int | float
    discount_amount: float
    subtotal: float
    shipping_fee: float
    tax: float
    total: float
    within_budget: bool
    policy_version: str
    generated_at: str
    valid_until: str


@dataclass(frozen=True)
class QuoteAmounts:
    """JSON 변환 전에 Decimal로 유지하는 견적 금액 내역과 예산 판단."""

    discount_amount: Decimal
    subtotal: Decimal
    shipping_fee: Decimal
    tax: Decimal
    total: Decimal
    within_budget: bool


def calculate_quote_amounts(
    *,
    unit_price: Decimal,
    discount_percentage: Decimal,
    quantity: int,
    budget: Decimal,
) -> QuoteAmounts:
    """검증된 입력으로 계산한다. 외부 조회·입력 검증·JSON 변환은 하지 않는다."""
    money_unit = Decimal(1).scaleb(-policy.MONEY_DECIMAL_PLACES)
    base_amount = (unit_price * quantity).quantize(
        money_unit, rounding=policy.ROUNDING,
    )
    discount_amount = (base_amount * discount_percentage / Decimal(100)).quantize(
        money_unit, rounding=policy.ROUNDING,
    )
    subtotal = base_amount - discount_amount
    tax = (subtotal * policy.TAX_RATE).quantize(
        money_unit, rounding=policy.ROUNDING,
    )
    shipping_fee = policy.SHIPPING_FEE
    total = subtotal + shipping_fee + tax
    return QuoteAmounts(
        discount_amount=discount_amount,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        tax=tax,
        total=total,
        within_budget=total <= budget,
    )


def _quote_error(
    code: QuoteErrorCode, message: str, *, retryable: bool = False,
) -> ToolError:
    """기존 Tool과 같은 코드·설명·재시도 정보를 오류 텍스트에 담는다."""
    return ToolError(json.dumps({
        "code": code, "message": message, "retryable": retryable,
    }, ensure_ascii=False))


def _load_quote_policy() -> QuotePolicy:
    """정책 원본을 읽고 누락·잘못된 값을 견적 정책 오류로 전달한다."""
    values = {
        name.lower(): getattr(policy, name, None)
        for name in (
            "POLICY_VERSION", "CURRENCY", "SHIPPING_FEE", "TAX_RATE",
            "MONEY_DECIMAL_PLACES", "ROUNDING", "VALIDITY_DAYS", "DISCOUNT_FIELD",
        )
    }
    try:
        settings = QuotePolicy.model_validate(values)
        money_unit = Decimal(1).scaleb(-settings.money_decimal_places)
        if settings.shipping_fee != settings.shipping_fee.quantize(
            money_unit, rounding=settings.rounding,
        ):
            raise ValueError("배송비가 정책의 소수 자릿수를 초과합니다.")
        timedelta(days=settings.validity_days)
    except (ValidationError, DecimalException, ValueError, OverflowError) as exc:
        raise _quote_error(
            "POLICY_UNAVAILABLE", "견적 정책의 필수 값이 누락되거나 올바르지 않습니다.",
        ) from exc
    return settings


async def fetch_quote_product(product_id: int) -> QuoteProduct:
    """특정 상품의 가격·할인율을 한 번 조회하고 원본 응답을 검증한다."""
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
            response = await client.get(f"{PRODUCT_API_URL}/{product_id}")
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise _quote_error(
            "UPSTREAM_TIMEOUT", "DummyJSON 견적 상품 조회 제한 시간을 초과했습니다.",
            retryable=True,
        ) from exc
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status == 404:
            raise _quote_error(
                "PRODUCT_NOT_FOUND", f"상품 ID {product_id}를 찾을 수 없습니다 (HTTP 404).",
            ) from exc
        if status == 429 or 500 <= status <= 599:
            raise _quote_error(
                "UPSTREAM_UNAVAILABLE",
                f"DummyJSON을 일시적으로 이용할 수 없습니다 (HTTP {status}).",
                retryable=True,
            ) from exc
        raise _quote_error(
            "INVALID_RESPONSE", f"DummyJSON이 예상하지 않은 HTTP {status} 응답을 반환했습니다.",
        ) from exc
    except httpx.RequestError as exc:
        raise _quote_error(
            "UPSTREAM_UNAVAILABLE", "DummyJSON 견적 상품 조회 중 통신에 실패했습니다.",
            retryable=True,
        ) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise _quote_error(
            "INVALID_RESPONSE", "DummyJSON 응답을 JSON으로 해석할 수 없습니다.",
        ) from exc
    try:
        product = QuoteProduct.model_validate(payload)
    except ValidationError as exc:
        raise _quote_error(
            "INVALID_RESPONSE", "DummyJSON 견적 상품 필드가 누락되거나 올바르지 않습니다.",
        ) from exc
    if product.id != product_id:
        raise _quote_error(
            "INVALID_RESPONSE", "DummyJSON 응답의 상품 ID가 요청과 일치하지 않습니다.",
        )
    return product


def _money_number(value: Decimal) -> float:
    """계산이 끝난 금액을 유한한 JSON 숫자로 변환한다."""
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("금액을 유한한 JSON 숫자로 표현할 수 없습니다.")
    return number


async def calculate_quote(
    product_id: PositiveInteger,
    quantity: PositiveInteger,
    budget: PositiveBudget,
) -> QuoteResult:
    """서버가 조회한 상품 가격·할인율과 정책으로 견적을 계산한다."""
    _load_quote_policy()
    product = await fetch_quote_product(product_id)
    # HTTP 대기 중 원본이 바뀌었더라도 계산 직전에 다시 검증한다.
    settings = _load_quote_policy()
    try:
        amounts = calculate_quote_amounts(
            unit_price=Decimal(str(product.price)),
            discount_percentage=Decimal(str(product.discountPercentage)),
            quantity=quantity, budget=Decimal(str(budget)),
        )
        money = {
            name: _money_number(getattr(amounts, name))
            for name in ("discount_amount", "subtotal", "shipping_fee", "tax", "total")
        }
    except (DecimalException, ValueError, OverflowError) as exc:
        raise _quote_error(
            "INVALID_RESPONSE", "상품 가격과 수량으로 유한한 견적 금액을 구성할 수 없습니다.",
        ) from exc
    generated_at = datetime.now(UTC)
    try:
        valid_until = generated_at + timedelta(days=settings.validity_days)
    except OverflowError as exc:
        raise _quote_error(
            "POLICY_UNAVAILABLE", "견적 안내기간으로 종료 시각을 구성할 수 없습니다.",
        ) from exc
    return {
        "status": "ok", "product_id": product.id, "name": product.title,
        "quantity": quantity, "currency": settings.currency,
        "unit_price": product.price,
        "discount_percentage": product.discountPercentage,
        "discount_amount": money["discount_amount"], "subtotal": money["subtotal"],
        "shipping_fee": money["shipping_fee"], "tax": money["tax"],
        "total": money["total"], "within_budget": amounts.within_budget,
        "policy_version": settings.policy_version,
        "generated_at": generated_at.isoformat(),
        "valid_until": valid_until.isoformat(),
    }

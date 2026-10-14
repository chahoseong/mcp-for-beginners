"""도구 권한과 회사별 견적 권한을 함께 검사하는 메모리 정책 예제.

VerifiedCaller는 인증·토큰 검증을 마친 경계에서만 공급한다.
demo_callers()의 값은 정책 설명용 입력이며 실제 인증을 대신하지 않는다.
이 파일은 토큰 검증기, HTTP 응답 처리기, 실행 중인 MCP 서버가 아니다.
"""

from dataclasses import dataclass, replace


ISSUER = "https://login.example.com/"
TOOL_SCOPES = {"get_quote": "quote:read", "set_quote": "quote:write"}


class AccessDenied(Exception):
    """접근 정책의 거부. HTTP/MCP 오류 변환은 호출 경계의 별도 책임이다."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__("접근이 거부되었습니다.")


@dataclass(frozen=True)
class VerifiedCaller:
    """검증 완료한 발급자, 서비스 애플리케이션 ID, 허용 범위."""

    issuer: str
    client_id: str
    scopes: frozenset[str]


@dataclass(frozen=True)
class Quote:
    """서버가 보관하는 견적. company_id는 견적의 실제 소유 회사다."""

    quote_id: str
    company_id: str
    amount: int


@dataclass
class QuoteStore:
    """서버가 관리하는 애플리케이션 소속과 견적 저장소."""

    app_companies: dict[tuple[str, str], str]
    quotes: dict[str, Quote]


def make_demo_store() -> QuoteStore:
    """각 검사에서 독립적으로 사용할 수 있는 예제 데이터를 만든다."""
    return QuoteStore(
        app_companies={
            (ISSUER, "acme-reader"): "acme",
            (ISSUER, "acme-editor"): "acme",
            (ISSUER, "beta-editor"): "beta",
        },
        quotes={
            "Q-100": Quote("Q-100", "acme", 1000),
            "Q-200": Quote("Q-200", "beta", 2000),
        },
    )


def demo_callers() -> dict[str, VerifiedCaller]:
    """정책 검사용 입력이다. 이 객체 생성 자체가 인증은 아니다."""
    return {
        "reader": VerifiedCaller(ISSUER, "acme-reader", frozenset({"quote:read"})),
        "editor": VerifiedCaller(
            ISSUER, "acme-editor", frozenset({"quote:read", "quote:write"})
        ),
        "beta": VerifiedCaller(
            ISSUER, "beta-editor", frozenset({"quote:read", "quote:write"})
        ),
    }


def require_tool_scope(caller: VerifiedCaller | None, tool_name: str) -> None:
    """판단 정보가 없거나 도구에 필요한 권한이 없으면 거부한다."""
    if (
        not isinstance(caller, VerifiedCaller)
        or not isinstance(caller.issuer, str)
        or not caller.issuer
        or not isinstance(caller.client_id, str)
        or not caller.client_id
        or not isinstance(caller.scopes, frozenset)
        or any(not isinstance(scope, str) or not scope for scope in caller.scopes)
    ):
        raise AccessDenied("missing_verified_identity")
    required = TOOL_SCOPES.get(tool_name)
    if required is None or required not in caller.scopes:
        raise AccessDenied("tool_scope_missing")


def authorize_quote(
    caller: VerifiedCaller | None,
    tool_name: str,
    quote_id: str,
    store: QuoteStore,
) -> Quote:
    """도구 권한과 대상 소유권을 확인한 뒤 서버 내부 견적을 반환한다."""
    require_tool_scope(caller, tool_name)
    assert caller is not None  # 위 검사에서 이미 확인했다.
    company_id = store.app_companies.get((caller.issuer, caller.client_id))
    if not company_id:
        raise AccessDenied("company_membership_missing")

    quote = store.quotes.get(quote_id)
    if quote is None or not quote.company_id or quote.company_id != company_id:
        # 없는 견적과 타사 견적은 외부에 같은 거부 메시지를 준다.
        raise AccessDenied("target_unavailable")
    return quote


def get_quote(
    caller: VerifiedCaller | None, quote_id: str, store: QuoteStore
) -> Quote:
    """두 접근 검사에 통과한 견적만 호출자에게 반환한다."""
    return authorize_quote(caller, "get_quote", quote_id, store)


def set_quote(
    caller: VerifiedCaller | None, quote_id: str, amount: int, store: QuoteStore
) -> Quote:
    """접근 검사와 값 검사가 모두 끝난 뒤 금액을 변경한다."""
    quote = authorize_quote(caller, "set_quote", quote_id, store)
    if type(amount) is not int or amount < 0:
        raise ValueError("금액은 0 이상의 정수여야 합니다.")
    updated = replace(quote, amount=amount)
    store.quotes[quote_id] = updated
    return updated


def caller_from_mcp() -> VerifiedCaller:
    """현재 MCP HTTP 요청의 검증 결과를 정책 입력으로 옮기는 어댑터.

    기존 검증기가 검증한 issuer를 AccessToken.claims['iss']에 보존했다는
    계약을 전제한다. 원시 JWT를 디코딩하거나 요청 인자로 신원을 보충하지 않는다.
    """
    from mcp.server.auth.middleware.auth_context import get_access_token

    token = get_access_token()
    if token is None:
        raise AccessDenied("missing_verified_identity")
    claims = token.claims
    issuer = claims.get("iss") if isinstance(claims, dict) else None
    if (
        not isinstance(issuer, str)
        or not issuer
        or not isinstance(token.client_id, str)
        or not token.client_id
        or not isinstance(token.scopes, list)
        or any(not isinstance(scope, str) or not scope for scope in token.scopes)
    ):
        raise AccessDenied("missing_verified_identity")
    return VerifiedCaller(issuer, token.client_id, frozenset(token.scopes))


def demonstrate() -> None:
    """정상 조회·변경과 거부 후 상태 보존을 보여준다. 인증값은 출력하지 않는다."""
    store = make_demo_store()
    callers = demo_callers()
    get_quote(callers["reader"], "Q-100", store)
    print("자기 회사 견적 조회: 허용")

    cases = [
        ("타사 견적 조회", lambda: get_quote(callers["editor"], "Q-200", store)),
        ("읽기 권한으로 변경", lambda: set_quote(callers["reader"], "Q-100", 1500, store)),
        ("타사 견적 변경", lambda: set_quote(callers["editor"], "Q-200", 2500, store)),
        ("검증 정보 없이 조회", lambda: get_quote(None, "Q-100", store)),
    ]
    for label, operation in cases:
        before = dict(store.quotes)
        try:
            operation()
        except AccessDenied:
            assert store.quotes == before
            print(f"{label}: 거부, 상태 유지")
        else:
            raise AssertionError("거부되어야 하는 요청이 허용되었습니다.")

    set_quote(callers["editor"], "Q-100", 1500, store)
    assert store.quotes["Q-100"].amount == 1500
    print("쓰기 권한으로 자기 회사 견적 변경: 허용")


if __name__ == "__main__":
    demonstrate()

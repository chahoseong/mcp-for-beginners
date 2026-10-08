"""견적 정책 원본을 읽는 Resource 함수."""

from app import policy


def get_quote_policy() -> str:
    """견적에 적용할 정책을 Markdown으로 제공한다."""
    return policy.render_quote_policy()

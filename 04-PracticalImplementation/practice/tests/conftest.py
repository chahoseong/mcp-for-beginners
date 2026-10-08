"""pytest의 비동기 테스트를 전용 가상환경의 asyncio에서 실행한다."""

import pytest


@pytest.fixture
def anyio_backend() -> str:
    """SDK와 함께 설치된 AnyIO pytest 플러그인을 사용한다."""
    return "asyncio"

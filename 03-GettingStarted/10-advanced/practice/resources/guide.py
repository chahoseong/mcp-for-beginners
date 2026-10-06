async def read_guide() -> str:
    """Return the calculator guide."""
    return (
        "add는 두 수를 더합니다.\n"
        "multiply는 두 수를 곱합니다.\n"
        "두 도구 모두 숫자 입력 a와 b가 필요합니다."
    )


resource_guide = {
    "uri": "guide://calculator",
    "name": "calculator-guide",
    "description": "계산기 도구 사용 안내",
    "mime_type": "text/plain",
    "handler": read_guide,
}
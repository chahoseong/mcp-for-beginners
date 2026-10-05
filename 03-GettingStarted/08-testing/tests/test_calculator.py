import pytest

from mcp.server.mcpserver.exceptions import ToolError
from practice.server import add, divide

def test_add_returns_correct_result():
    x = 1
    y = 2
    assert add(x, y) == x + y


def test_divide_fraction():
    assert divide(5, 2) == 2.5


def test_divide_zero_numerator():
    assert divide(0, 2) == 0.0


def test_divide_zero_denominator():
    with pytest.raises(ToolError):
        divide(3, 0)
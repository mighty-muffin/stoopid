import pytest

from stoopid import add, fibonacci, multiply


def test_add() -> None:
    assert add(2, 3) == 5


def test_multiply() -> None:
    assert multiply(4, -2) == -8


@pytest.mark.parametrize(("n", "expected"), [(0, 0), (1, 1), (2, 1), (10, 55)])
def test_fibonacci(n: int, expected: int) -> None:
    assert fibonacci(n) == expected


def test_fibonacci_rejects_negative() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        fibonacci(-1)

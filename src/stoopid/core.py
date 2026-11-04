"""Arithmetic nobody needed."""


def add(a: int, b: int) -> int:
    """Return the sum of ``a`` and ``b``."""
    return a + b


def multiply(a: int, b: int) -> int:
    """Return the product of ``a`` and ``b``."""
    return a * b


def fibonacci(n: int) -> int:
    """Return the ``n``-th Fibonacci number (``fibonacci(0) == 0``).

    Raises:
        ValueError: if ``n`` is negative.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

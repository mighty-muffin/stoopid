"""stoopid: a deliberately meaningless package for testing release automation."""

from importlib.metadata import version

from stoopid.core import add, fibonacci, multiply

__all__ = ["__version__", "add", "fibonacci", "multiply"]

__version__ = version("stoopid")

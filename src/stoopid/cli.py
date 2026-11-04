"""Command-line interface: ``stoopid add 1 2``."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from stoopid import __version__
from stoopid.core import add, fibonacci, multiply


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stoopid", description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (("add", "add two integers"), ("mul", "multiply two integers")):
        cmd = sub.add_parser(name, help=help_text)
        cmd.add_argument("a", type=int)
        cmd.add_argument("b", type=int)

    fib = sub.add_parser("fib", help="n-th Fibonacci number")
    fib.add_argument("n", type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "add":
        result = add(args.a, args.b)
    elif args.command == "mul":
        result = multiply(args.a, args.b)
    else:
        try:
            result = fibonacci(args.n)
        except ValueError as exc:
            build_parser().error(str(exc))
    print(result)
    return 0

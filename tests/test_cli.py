import runpy
import sys

import pytest

from stoopid import __version__
from stoopid.cli import main


@pytest.mark.parametrize(
    ("argv", "expected"),
    [(["add", "1", "2"], "3"), (["mul", "3", "4"], "12"), (["fib", "10"], "55")],
)
def test_commands(argv: list[str], expected: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(argv) == 0
    assert capsys.readouterr().out.strip() == expected


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == __version__


def test_fib_negative_is_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["fib", "-1"])
    assert exc.value.code == 2
    assert "non-negative" in capsys.readouterr().err


def test_dunder_main(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "argv", ["stoopid", "add", "2", "2"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("stoopid", run_name="__main__")
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == "4"

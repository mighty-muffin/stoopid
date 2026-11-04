# consumer: using stoopid as a dependency

A minimal project that declares `stoopid` as a dependency and calls its
library API.

```toml
# pyproject.toml
[project]
dependencies = ["stoopid>=0.1"]
```

```python
import stoopid

stoopid.add(1, 2)  # 3
stoopid.multiply(3, 4)  # 12
stoopid.fibonacci(10)  # 55
stoopid.fibonacci(-1)  # raises ValueError
stoopid.__version__  # installed version, e.g. "0.1.0"
```

## Run it

```console
$ cd examples/consumer
$ uv run main.py
stoopid 0.1.0
add(1, 2)      = 3
multiply(3, 4) = 12
fibonacci(10)  = 55
fibonacci(-1)  -> ValueError: n must be non-negative
```

`uv run` creates a `.venv` and installs the latest `stoopid` from PyPI. With
pip instead: `pip install stoopid && python main.py`.

## Try it against your working tree

To run the example against the local checkout instead of the PyPI release:

```sh
uv add --editable ../..
```

This rewrites `pyproject.toml` with a `[tool.uv.sources]` entry; don't commit
that change.

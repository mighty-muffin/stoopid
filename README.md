# stoopid

[![CI](https://github.com/mighty-muffin/stoopid/actions/workflows/ci.yml/badge.svg)](https://github.com/mighty-muffin/stoopid/actions/workflows/ci.yml)
[![Release](https://github.com/mighty-muffin/stoopid/actions/workflows/release.yml/badge.svg)](https://github.com/mighty-muffin/stoopid/actions/workflows/release.yml)
[![PyPI](https://img.shields.io/pypi/v/stoopid)](https://pypi.org/project/stoopid/)
[![Python](https://img.shields.io/pypi/pyversions/stoopid)](https://pypi.org/project/stoopid/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

A deliberately meaningless Python package. The code does nothing useful; it
exists so the **release pipeline around it** can be tested end to end. See
[`specs/0001-stoopid-design.md`](specs/0001-stoopid-design.md) for the full design.

## Install

```sh
pip install stoopid                      # latest release (PyPI)
pip install --pre --no-deps \
  --index-url https://test.pypi.org/simple/ stoopid   # latest dev build (TestPyPI)
```

## Usage

```console
$ stoopid add 1 2
3
$ stoopid mul 3 4
12
$ stoopid fib 10
55
```

```python
>>> import stoopid
>>> stoopid.fibonacci(10)
55
```

## Development

```sh
uv sync                 # create .venv with dev tools
prek install            # git hooks (ruff, ty, uv lock check, …)
uv run pytest           # tests, 100 % coverage enforced
prek run --all-files    # every check CI runs
```

## How releasing works

1. Every PR title must follow [Conventional Commits](https://www.conventionalcommits.org/)
   (`feat: …`, `fix: …`, `feat!: …`, `chore: …`). PRs are squash-merged, so the
   title becomes the commit on `main`.
2. On each push to `main`, [release-please](https://github.com/googleapis/release-please)
   keeps a **release PR** open with the next version and the `CHANGELOG.md` entry.
   Until 1.0: `feat!` → minor, `feat`/`fix` → patch.
3. The same push publishes a dev build `X.Y.(Z+1).devN` to TestPyPI.
4. **Merging the release PR** tags `vX.Y.Z`, creates the GitHub Release, builds
   once, publishes to TestPyPI, smoke-tests the install, then publishes to PyPI
   (Trusted Publishing + PEP 740 attestations, no API tokens).
5. To force a version (e.g. 1.0.0), add `"release-as": "1.0.0"` to the package in
   `release-please-config.json` through a PR, then remove it after the release.

Dependencies, Actions and hooks are updated weekly by Renovate; non-major
updates merge themselves when CI is green.

One-time setup (PyPI publishers, release GitHub App, Renovate):
`scripts/setup-wizard.sh`.

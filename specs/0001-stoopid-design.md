# 0001 — stoopid: a throwaway package with a real release pipeline

Status: accepted (2026-11-04)

## Purpose

`stoopid` is a meaningless Python package. Its code does nothing that matters;
it exists so the **development and release workflow** around it can be
exercised end to end: conventional commits → semantic version → changelog →
GitHub Release → TestPyPI → PyPI, with as little human involvement as
possible.

## Decisions

### Package

| Decision | Choice | Why |
|---|---|---|
| Distribution / import name | `stoopid` / `import stoopid` | Matches the repo; free on PyPI and TestPyPI. |
| Content | Tiny math lib (`add`, `multiply`, `fibonacci`) + `stoopid` CLI | The console entry point lets every published artifact be smoke-tested by running it. |
| CLI framework | `argparse`, zero runtime deps | Installs from TestPyPI need no PyPI fallback index. |
| Python support | 3.10 – 3.14 | All non-EOL CPython versions; exercises a real matrix. |
| Build | uv + `uv_build` backend | Fast, current standard, one tool for env/lock/build. |
| Version source | `version` in `pyproject.toml`, read at runtime via `importlib.metadata` | One place for release-please to bump. |
| License | MIT (SPDX expression, PEP 639) | — |

### Quality gates

- ruff (lint + format), ty (type check), pytest with **100 % coverage enforced**
  (`--cov-fail-under=100`), no external coverage service.
- Hooks run through **prek** from `.pre-commit-config.yaml`; CI runs the same
  hooks. No task runner: `uv run …` and `prek run -a` are the interface.
- CI matrix: `ubuntu-latest` × Python 3.10–3.14.
- PR CI also builds sdist + wheel (`uv build`, wheel built *from* the sdist),
  checks metadata, installs the wheel in a clean venv and runs the CLI.
- An aggregate `ci-ok` job is the single required check for CI.

### Commits and repository rules

- Conventional Commits, enforced on the **PR title** (`pr-title` check).
- **Squash merge only**; squash commit title = PR title, body = blank, so the
  PR title alone drives the version bump (PR bodies such as Renovate release
  notes cannot smuggle in a `BREAKING CHANGE:` footer).
- Public repo `mighty-muffin/stoopid`. `main` ruleset: PR required (0
  approvals), required checks `ci-ok` + `pr-title`, linear history, no force
  push, no deletion. Org admins may bypass.
- Repo settings: auto-merge allowed, head branches deleted on merge.

### Versioning and releases

- **release-please** (manifest mode, `release-type: python`), run with a
  token from an **org-owned GitHub App** so its PRs trigger CI (the default
  `GITHUB_TOKEN` would not).
- First release **0.1.0** (`initial-version`). Pre-1.0 rules:
  `bump-minor-pre-major` + `bump-patch-for-minor-pre-major` (`feat!` → minor,
  `feat` → patch). Going to 1.0.0 is a deliberate act: set `release-as` in
  `release-please-config.json` via a PR, then remove it after the release.
- release-please also bumps the project's own entry in `uv.lock` (TOML
  extra-file), so `uv lock --check` stays green on the release PR.
- Merging the release PR is the **only** human gate.

### Publishing

One workflow, `release.yml`, on every push to `main`:

1. **release-please** — opens/updates the release PR, or, if the release PR
   was just merged, tags `stoopid-vX.Y.Z` (manifest mode puts the component in the tag) and creates the GitHub Release.
2. **build** — once. Release: version from `pyproject.toml` (checked against
   the tag). Otherwise a **dev build**: `X.Y.(Z+1).devN`, N = `github.run_number`,
   set in CI only and never committed.
3. **publish-testpypi** — every run (dev and release).
4. **smoke-testpypi** — install that exact version from TestPyPI (`--no-deps`)
   into a clean venv, run the CLI, check `--version`.
5. **publish-pypi** — release runs only, after the smoke test passes.

- Recovery: a manual `workflow_dispatch` run with `tag=stoopid-vX.Y.Z` skips
  release-please and runs steps 2–5 for that existing tag. Re-running failed
  jobs can't fix a broken workflow, because a re-run uses the workflow file from
  the original commit.
- Auth: **Trusted Publishing (OIDC)** only; no API tokens. GitHub
  environments `testpypi` and `pypi`, restricted to `main`, no required
  reviewers.
- **PEP 740 attestations** uploaded with every publish (default of
  `pypa/gh-action-pypi-publish` under trusted publishing).
- Actions are referenced by version tag (no SHA pinning, no zizmor, CodeQL or
  Scorecard).

### Maintenance

- **Renovate** (GitHub App), weekly, grouped, semantic `chore(deps)` titles;
  covers `uv.lock`/`pyproject`, GitHub Actions and prek hooks, plus a
  lock-file maintenance PR. Non-major updates auto-merge when green; majors
  wait for a human.

### Documentation

- `README.md` (install, usage, badges, how releasing works) and the
  `CHANGELOG.md` that release-please maintains.

## One-time manual setup

Done through `scripts/setup-wizard.sh`, which walks a human through what only
a human can do in a web UI:

1. PyPI and TestPyPI **pending trusted publishers**: owner `mighty-muffin`,
   repo `stoopid`, workflow `release.yml`, environments `pypi` / `testpypi`.
2. Create the org GitHub App (contents, pull requests, issues: read & write),
   install it on the repo, store `RELEASE_APP_ID` (variable) and
   `RELEASE_APP_PRIVATE_KEY` (secret).
3. Install the Renovate GitHub App on the repo.

Repo creation, settings, environments and the ruleset are scripted with `gh`.

## Out of scope

Docs site, multi-OS CI, Codecov, CONTRIBUTING/templates, task runner, runtime
dependencies, manual approval on PyPI publish.

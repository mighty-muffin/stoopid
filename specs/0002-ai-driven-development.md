# 0002 — AI-driven development with GitHub Agentic Workflows

Status: accepted (2026-11-04). Supersedes the *Purpose* of
[0001](0001-stoopid-design.md) and its "no runtime dependencies" rule; the rest
of 0001 (quality gates, commits, release pipeline) still holds.

## Purpose

`stoopid` stops being meaningless. AI agents running as
[GitHub Agentic Workflows](https://github.github.com/gh-aw/) (gh-aw) research
what it could become, propose concepts, and build the one a human picks. The
release pipeline from 0001 stays unchanged underneath: every agent change ships
through conventional commits → release-please → TestPyPI → PyPI.

AI is the **developer**. What the product *is* stays open; it may or may not
use AI at runtime.

## Decisions

### Product frame

Every concept must fit this frame; the agents may not change it.

| Decision | Choice | Why |
|---|---|---|
| Form | Python package `stoopid` on PyPI with a `stoopid` CLI | Keeps the name, the pipeline and the CLI smoke test working. |
| Python support | 3.10 – 3.14 | Unchanged from 0001. |
| Quality gates | ruff, ty, pytest with 100 % coverage, prek hooks | Unchanged from 0001; agents meet the same bar as humans. |
| Runtime dependencies | Allowed | A useful tool will need libraries. The TestPyPI smoke test installs dependencies from PyPI first, then `stoopid` from TestPyPI with `--no-deps`, so the two indexes are never mixed in one resolve. |
| Old commands | `add` / `mul` / `fib` are removed by the accepted concept's first roadmap issue, as a `feat!` | An honest breaking change; pre-1.0 rules turn it into a minor bump (0.2.0). |
| Domain | Developer-tooling CLIs (something a Python developer would `pipx install`) | Demand is visible on GitHub and forums, and the maintainer is a likely user. |

### Concept rubric

Concept research scores every proposal against:

1. **Demand** — evidence that people want it (linked issues, threads, posts).
2. **Gap** — what existing tools miss, named and compared.
3. **Buildable** — an MVP shippable in about 5 builder PRs.
4. **Self-contained** — no paid API or user secret required at runtime.
   AI-powered ideas are allowed, but must work without a key.

### Workflows

All workflows run on the **Claude** engine (`ANTHROPIC_API_KEY`).

| Workflow | Trigger | Writes |
|---|---|---|
| `concept-research` | Weekly. Scheduled runs are skipped while a concept is accepted; manual runs always proceed. | 3–5 `concept:proposal` issues |
| `planner` | A human adds `concept:accepted` to a proposal issue | Draft PR with `specs/0003-<concept>.md`; roadmap issues; closes the other open proposals |
| `builder` | Daily on weekdays. Skipped while an open PR labelled `agent` exists. | One draft PR (label `agent`) for one `agent:ready` issue, test-first |
| `builder` rework | `/fix <notes>` comment on an agent PR; one automatic attempt when CI fails on an agent PR | Commits pushed to the existing PR branch |
| `improver` | Weekly | Improvement issues only, never PRs |

The issue picked by the builder is the oldest open `agent:ready` issue.
Agent PR titles follow Conventional Commits like any other PR.

### Human gates

1. **Accept a concept** — add `concept:accepted` to one proposal issue.
2. **Triage** — add `agent:ready` to the issues the builder may work on.
   Planner and improver issues never arrive ready.
3. **Merge agent PRs** — they open as drafts; mark ready and squash-merge by
   hand. Agent PRs are never auto-merged.
4. **Merge the release PR** — unchanged from 0001.

### Identity and tokens

- **PRs** (create, push to branch) use the org GitHub App from 0001
  (`RELEASE_APP_ID` / `RELEASE_APP_PRIVATE_KEY`) through gh-aw's
  `safe-outputs` `github-app`, so `ci-ok` and `pr-title` run on agent PRs.
  PRs opened with `GITHUB_TOKEN` would not trigger CI.
- **Issues, comments and labels** use the default `GITHUB_TOKEN`. Events made
  by `github-actions[bot]` don't trigger other workflows, which keeps gh-aw's
  built-in loop protection.

### Agent capabilities

Least privilege. The agent job is always read-only; all writes go through
gh-aw safe outputs, after its threat-detection job.

| Workflow | Tools | Network |
|---|---|---|
| `concept-research`, `planner`, `improver` | web search, web fetch, GitHub read | defaults + web tools |
| `builder` | edit; bash limited to `uv`, `pytest`, `ruff`, `ty`, `prek`, `git`; GitHub read | `python` and `github` ecosystems only |

The builder cannot browse the open web, which limits what a prompt injection
arriving through issue text can reach. Agent PRs may not touch
`.github/workflows/` (gh-aw protected files).

### Memory

`concept-research` and `improver` keep notes in gh-aw `repo-memory` (a
`memory/*` branch, no expiry), so they don't re-propose rejected ideas or
re-file known gaps. `planner` and `builder` are stateless; they read issues
and the repo.

### Cost controls

| Control | Value |
|---|---|
| `max-ai-credits` (per run) | 200 (≈ $2) |
| `max-daily-ai-credits` (per workflow) | 500 (≈ $5) |
| `timeout-minutes` | 20; builder 30 |
| `stop-after` | not used (it resets on every recompile) |

Worst case ≈ $5 per workflow per day. Loosen only after reviewing
`gh aw logs` / `gh aw audit`.

### Labels

| Label | Set by | Meaning |
|---|---|---|
| `concept:proposal` | `concept-research` | A concept proposal issue |
| `concept:accepted` | human | The chosen concept; triggers `planner` |
| `agent:ready` | human | The builder may implement this issue |
| `agent` | `builder` | PR authored by an agent |

### Repository footprint

`gh aw init --engine claude --no-mcp --no-agent`, minus `.vscode/`:

- `.gitattributes` marks `.github/workflows/*.lock.yml` as generated.
- `.github/skills/agentic-workflows/SKILL.md` routes any coding agent editing
  these workflows to the gh-aw docs.

Each workflow is a `.github/workflows/<name>.md` source plus its compiled
`<name>.lock.yml`; edit the `.md`, then `gh aw compile`.

## Rollout

A stack of PRs, bottom first:

1. This spec, README, `gh aw init`, labels.
2. `concept-research`.
3. `planner`.
4. `builder`, with `/fix` and the CI retry.
5. `improver`, and the TestPyPI smoke-test change for runtime dependencies.

## One-time manual setup

1. Repo secret `ANTHROPIC_API_KEY` (before the first workflow runs):
   `gh secret set ANTHROPIC_API_KEY`.

## Out of scope

Copilot or Codex engines, auto-merging agent PRs, agents editing workflows or
the release pipeline, a second concept running in parallel.

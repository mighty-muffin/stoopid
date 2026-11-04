---
description: Rework an agent PR on `/fix <notes>`, or once automatically when its CI fails.
on:
  slash_command:
    name: fix
    events: [pull_request_comment]
  workflow_run:
    workflows: [CI]
    types: [completed]
    branches: ["agent/**"]
  # Automatic retries happen at most once per PR (spec 0002): skip unless CI
  # failed, the PR is an agent PR, and it doesn't carry agent:ci-retried yet.
  # (`workflow_run.conclusion:` would leak into the compiled `on:` block,
  # which GitHub rejects, so the conclusion is checked here instead.)
  steps:
    - name: Gate automatic CI retry
      id: retry_gate
      if: github.event_name == 'workflow_run'
      env:
        GH_TOKEN: ${{ github.token }}
        GH_REPO: ${{ github.repository }}
        HEAD_BRANCH: ${{ github.event.workflow_run.head_branch }}
        CONCLUSION: ${{ github.event.workflow_run.conclusion }}
      run: |
        echo "CI conclusion: $CONCLUSION"
        test "$CONCLUSION" = failure
        labels=$(gh pr list --head "$HEAD_BRANCH" --state open --json labels --jq '.[0].labels // [] | map(.name)')
        echo "PR labels: $labels"
        echo "$labels" | jq -e 'index("agent") != null and index("agent:ci-retried") == null'
if: needs.pre_activation.outputs.retry_gate_result != 'failure'
permissions:
  contents: read
  issues: read
  pull-requests: read
  actions: read
engine: claude
timeout-minutes: 30
max-ai-credits: 200
max-daily-ai-credits: 500
runtimes:
  uv:
    version: "latest"
network:
  allowed:
    - defaults
    - github
    - python
tools:
  github:
    toolsets: [repos, issues, pull_requests, actions]
  edit:
  bash: ["uv:*", "git:*", cat, ls, find, grep, head, tail, wc, diff]
safe-outputs:
  push-to-pull-request-branch:
    # Pushed as the org App so CI runs again on the new commit.
    github-app:
      client-id: ${{ vars.RELEASE_APP_ID }}
      private-key: ${{ secrets.RELEASE_APP_PRIVATE_KEY }}
    target: "*"
    required-labels: [agent]
    protected-files:
      policy: request-review
      exclude: ["/README.md"]
  add-labels:
    target: "*"
    allowed: [agent:ci-retried]
    max: 1
  add-comment:
    target: "*"
    max: 1
---

# Builder: fix

You rework an existing agent PR in `${{ github.repository }}`. Every PR you
touch carries the `agent` label and was opened by the builder (or planner).

## Which PR, and why

- **`/fix` comment** (`${{ github.event_name }}` is `issue_comment`): the PR
  is #${{ github.event.issue.number }}. The maintainer's request is the text
  after `/fix` in their comment:

  > ${{ steps.sanitized.outputs.text }}

  Read the rest of the PR conversation and any review comments too.
- **CI failure** (`${{ github.event_name }}` is `workflow_run`): look up CI
  run ${{ github.event.workflow_run.id }}; the PR is the open PR whose head
  branch is that run's head branch. Read the logs of its failed jobs and fix
  the cause. This is the PR's single automatic retry.

If the PR isn't open or lacks the `agent` label, call `noop` and stop.

## Fix it

1. Read `specs/0002-ai-driven-development.md`, the concept spec in `specs/`,
   the PR's linked issue and its diff.
2. Check out the PR's head branch (`git fetch origin <branch>` then
   `git checkout <branch>`) and run `uv sync --locked`.
3. Make the smallest change that addresses the request or the failure. For
   behaviour changes, update or add a failing test first.
4. Run the gates: `uv run ruff check --fix`, `uv run ruff format`,
   `uv run ty check`, `uv run pytest` (100 % coverage), and `uv lock --check`
   if dependencies changed.
5. Commit on the PR's branch with a message like `fix: <what changed>`, and
   push it with `push_to_pull_request_branch` for that PR number.

Same limits as the builder: never edit `.github/`, `specs/0001-*`,
`specs/0002-*`, `CHANGELOG.md`, or the `version` in `pyproject.toml`; stay
inside the PR's issue.

## Report

- **CI failure run:** add the label `agent:ci-retried` to the PR, whether or
  not you could fix it, so no second automatic retry happens.
- Comment once on the PR: what you changed and the final `uv run pytest`
  summary line. If you couldn't fix it, say what's still failing and why, so
  the maintainer can reply with a more specific `/fix`, fix it by hand, or
  close the PR.

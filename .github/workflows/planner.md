---
description: When a maintainer accepts a concept, write its spec as a draft PR and break it into roadmap issues.
on:
  issues:
    types: [labeled]
    names: [concept:accepted]
permissions:
  contents: read
  issues: read
  pull-requests: read
engine: claude
timeout-minutes: 20
max-ai-credits: 200
max-daily-ai-credits: 500
network:
  allowed:
    - defaults
    - github
    - python
    - news.ycombinator.com
    - reddit.com
    - stackoverflow.com
    - discuss.python.org
    - lobste.rs
    - dev.to
  hosted-web:
    allowed:
      - github.com
      - pypi.org
      - news.ycombinator.com
      - reddit.com
      - stackoverflow.com
      - discuss.python.org
      - lobste.rs
      - dev.to
tools:
  github:
    toolsets: [repos, issues, pull_requests]
  edit:
  bash: [cat, ls, grep, head, tail, wc, date]
  web-search:
  web-fetch:
safe-outputs:
  create-pull-request:
    # Opened as the org App so CI and pr-title run on it (spec 0002).
    github-app:
      client-id: ${{ vars.RELEASE_APP_ID }}
      private-key: ${{ secrets.RELEASE_APP_PRIVATE_KEY }}
    draft: true
    labels: [agent]
    allowed-files: ["specs/*.md"]
    auto-close-issue: false
  create-issue:
    max: 8
  link-sub-issue:
    max: 8
    parent-required-labels: [concept:accepted]
  close-issue:
    target: "*"
    required-labels: [concept:proposal]
    state-reason: not_planned
    max: 5
  add-comment:
    max: 1
---

# Planner

A maintainer just accepted a concept for `stoopid` by labelling issue
#${{ github.event.issue.number }} with `concept:accepted`. Turn it into a spec
and a roadmap the builder can work through one PR at a time.

## Read first

1. `specs/0002-ai-driven-development.md` — your operating rules. The
   *Product frame*, *Human gates* and *Workflows* sections are binding.
2. `specs/0001-stoopid-design.md`, `README.md`, `pyproject.toml`, `src/`,
   `tests/` — what exists today.
3. Issue #${{ github.event.issue.number }}, including every comment. Comments
   from the maintainer override the original proposal.

## Stop early if

- Another **open** issue (not #${{ github.event.issue.number }}) also has
  `concept:accepted`. Only one concept runs at a time. Comment on
  #${{ github.event.issue.number }} saying which issue is already accepted
  and that the maintainer should close one of them, then stop.
- Issue #${{ github.event.issue.number }} already has sub-issues, or an open
  or merged PR already adds a spec for it. The label was re-applied; comment
  that planning already happened (link it), then stop.

## 1. Spec PR

Write `specs/NNNN-<slug>.md`, where `NNNN` is the next free number in
`specs/` (0003 if this is the first concept) and `<slug>` is the concept's
short name. Follow the style of `specs/0001-stoopid-design.md`: a status
line (`Status: proposed (<today>)`), a *Purpose* section, *Decisions* tables
with a *Why* column, and an *Out of scope* section. Cover:

- Who it's for and the problem it solves (from the proposal's evidence).
- The CLI surface: commands, flags, exit codes, output formats, with an
  example session.
- The Python API, if any, that the CLI is built on.
- Runtime dependencies and why each is worth it.
- What the MVP includes and what it explicitly leaves out.
- How it's tested at 100 % coverage without network access in tests.

Stay inside the frame in spec 0002. Where the proposal is vague, decide and
record the decision with a reason rather than leaving questions open.

Open the PR with title `docs: add spec NNNN for <concept name>` and a short
body linking #${{ github.event.issue.number }}. Only files under `specs/` are
allowed.

## 2. Roadmap issues

Break the spec into **4 to 8** issues, each one small enough for a single
builder PR (roughly under 400 changed lines, including tests). Create them in
the order they should be built.

- **The first issue is always** removing the old `add` / `mul` / `fib`
  commands and the `add` / `multiply` / `fibonacci` functions, with their
  tests and README usage, and replacing the README intro and usage with a
  description of the new concept. Title:
  `feat!: replace math commands with <concept name> skeleton`.
- **Title** each issue with the Conventional Commit title its PR should
  have, e.g. `feat: add envdiff compare command`. Use `feat!` only for the
  first issue.
- **Body**:

  ```markdown
  Part of #<accepted issue>. Spec: `specs/NNNN-<slug>.md` (PR #<spec PR> until merged).

  ## Goal
  One or two sentences.

  ## Acceptance criteria
  - [ ] Observable behaviour, each one testable.
  - [ ] Tests cover it; 100 % coverage holds; `prek run -a` passes.

  ## Notes
  Pointers to the spec section, files likely touched, edge cases.
  ```

- Use `blocked_by` with the temporary ID of the previous issue when an issue
  can't start until another has merged.
- Link every roadmap issue as a sub-issue of
  #${{ github.event.issue.number }}.
- Do **not** add `agent:ready`. The maintainer decides what gets built.

## 3. Tidy up

- Close every other **open** issue labelled `concept:proposal`, except
  #${{ github.event.issue.number }}, with state `not_planned` and a one-line
  comment: `Closed: #${{ github.event.issue.number }} was accepted.`
- Leave #${{ github.event.issue.number }} **open**. It is the concept's
  tracking issue; while it's open, scheduled concept research stays dormant.
- Comment once on #${{ github.event.issue.number }}: link the spec PR, list
  the roadmap issues in build order, and remind the maintainer to merge the
  spec PR and label the first issue `agent:ready` to start the builder.

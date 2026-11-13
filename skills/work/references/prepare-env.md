# Stage: prepare-env

Set up the place the work runs and record its starting state, so the final gates can tell a
failure this change caused from one it inherited. Runs in every profile, right
after `understand-scope`. It records no receipt of its own: `eris baseline` keeps the result.

## 1. Worktree or workbench

- Create an isolated worktree from the latest `origin/main`, on the issue's branch name, inside
  the repo: `git worktree add --no-track -b <branch> .claude/worktrees/<ISSUE> origin/main`.
  When an issue or brief stacks on an unmerged sibling PR (`<stack-base>`), fetch and branch the
  worktree from `origin/<stack-base>` instead (`git fetch origin <stack-base>` then
  `git worktree add --no-track -b <branch> .claude/worktrees/<ISSUE> origin/<stack-base>`), pass
  `--base <stack-base>` when opening the draft PR, and carry `BASE_REF="origin/<stack-base>"` into
  Step 2 and `final-gates`.
  When an issue spans multiple PRs, only the final PR that completes `<KEY>` writes `Closes <KEY>`
  in its PR body; every contributing PR writes `Part of <KEY>` in its PR body so Linear attaches it
  as `contributes` instead of auto-closing `<KEY>` from the branch name on merge.
  Never a sibling of the checkout (`../<repo>-<issue>`). Work in the main checkout only when
  asked to.
- Start the repo's local stack (its workbench, when it declares one) only when the change needs running services.
- Install the repo's dependencies (`bun install`, `uv sync`) before taking any baseline. `eris baseline` installs only for a `bun.lock` or `uv.lock`; for any other stack it does not auto-install, so the `ci.local` gates own their install (each gate runs its own `go mod download`, `yarn install --immutable` or equivalent), and the install you ran in the worktree is not what the baseline measured.
- **`linear-only` runs skip worktree and install:** When `understand-scope` marked
  `scope: linear-only` (no git repo diff: Linear-only writes, Socrates living-doc entries, read-only
  spikes, or operator files outside a git worktree), stay in the current checkout
  with no worktree (`worktree: none` in the hand-back), no branch, and no dependency install.

**Done when:** `pwd` and `git remote -v` name the repo the issue belongs to (or `scope: linear-only` stays in the current checkout with `worktree: none`).

## 2. Baseline

From the worktree root, before changing anything (setting `BASE_REF="origin/<stack-base>"` when
stacked on an unmerged sibling PR, or leaving `BASE_REF` unset for `origin/main`):

```bash
BASE_REF="${BASE_REF:-origin/main}" # stacked branch: BASE_REF="origin/<stack-base>"
G="$(git rev-parse --absolute-git-dir)/eris"; mkdir -p "$G"
git merge-base "$BASE_REF" HEAD > "$G/final-gates.base"
eris baseline record --base "$BASE_REF"
```

It runs every `ci.local` gate in the root `eris.yaml` at the merge-base with `$BASE_REF` plus the
pragma leg (`eris lint --all`), writes that 40-hex `merge_base` to `<git-dir>/eris/baseline.json`,
and records GitHub's status at the branch point beside it as advisory. On a stacked branch, passing
`BASE_REF="origin/<stack-base>"` (`--base origin/<stack-base>`) is required so `eris baseline record`
reads the sibling PR's `eris.yaml` / `ci.local` instead of failing with `baseline-no-ci-local` on an
older `origin/main`, and so `final-gates.base` records the stack divergence commit rather than
`origin/main`. A failure here is pre-existing: leave it alone unless the change makes it
worse or the issue says to fix it. The `final-gates` stage runs `eris baseline diff`.

A repo with no `ci.local` has no baseline to record: run its test and lint commands once, keep the
failing lines in the plan's current-state section, and say so in one line.

A **`linear-only`** run changes no repo source, so it skips `eris baseline record` and records
`baseline: n/a (linear-only)` in `final-gates`. When the run edits operator files outside a repo
working tree, copy each target file's
starting state into `$G/before/` (`G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"`;
`mkdir -p "$G/before"`) before editing so `final-gates` can produce a deterministic `diff -u` artifact.

**Done when:** `record` printed its summary, the plan holds the pre-existing failures, or `linear-only` skipped the repo baseline (with `$G/before/` snapshotted for operator files).

## 3. Pragma

When the change will touch an eris governance site (a config key, a call to another service, a
queue, an event, a status write on a governed object), name the sites the plan will touch; `eris lint --all` reports
their pragma state. The plan names them so `final-gates` can check the diff against them. A
`linear-only` or operator-file run touches no governance site (`none (linear-only)`).

**Done when:** each governance site the change touches is named, or the plan says it touches none.

# Stage: deploy

Every profile. Some merged work changes nothing until someone runs a step on this machine:
fast-forwarding the checkout that `~/.claude` symlinks into, re-running `eris org-skills install` for
a new skill, agent or rule, a CLI rebuild, or a version-bump chore PR (pre-authorised by doctrine).
Find the step and run it from the merged base, never from the worktree. The main checkout is shared,
so update it only with a fast-forward while it sits on the base branch.

**Re-check right before a release.** A release step (a release script, a tag push, a package
publish, a `chore(release)` PR) runs once per version. Immediately before it:

- `git fetch origin main --tags`; `git ls-remote --tags origin <tag>` prints nothing, and
  `git log --oneline <merge sha>..origin/main` shows no release commit for that version;
- the version is absent where the runbook publishes it, when that can be queried;
- the thread still shows this run's claim as the earliest live one (`inventory`).

Any check failing means another run or a person released, or is releasing, that version: don't run
the step. The row is a hold whose receipt is the tag, commit or version you observed.

**Done when:** an observation shows the deployed state equals the merge, for example a clean drift
check or a binary version at the merge SHA. "None" counts only when the repo names no step.

## Discover the step

Look in this order and stop at the first source that names one:

1. The PR body: a "Deploy", "Rollout" or "After merge" section, or a checklist item.
2. The repo's `CLAUDE.md`, `README.md`, `RELEASING.md`, and `docs/` release or install pages.
3. `Makefile` / `package.json` scripts: `install`, `release`, `deploy`, `link`.
4. Precedent: how the last PR that touched the same paths was deployed (`git log -- <path>` and that
   PR's comments).

Known steps:

| Repo | Change | Step | Proof |
|---|---|---|---|
| a harness template fork | `skills/`, `agents/`, `rules/` | fast-forward the main checkout per "Run it" below: installed skills, agents and rules are symlinks into it. A *new*, renamed or deleted file is not live until `eris org-skills install` relinks it (a hold when the fast-forward is not possible, naming the command) | `readlink ~/.claude/skills/<name>` resolves into the main checkout, and the checkout's HEAD contains the merge |
| a bun CLI | source | the lockfile install per "Run it" below, then the repo's build/link script per its README | `<cli> --version` or the build stamp equals the merge SHA |
| any repo with a release runbook | version bump | the runbook's `chore(release)` PR, merged per doctrine pre-authorisation | the tag or published version exists |

A doc can drift from the repo. When the doc and the repo disagree, the repo wins: run `--help` or a
dry run first.

## Run it

- Run from the **merged base**, never from the feature worktree: it may be about to be removed, and
  it lacks anything merged since. The main checkout is shared with the reviewer and other jobs.
  Update it only when it is on the base branch, using `git -C <checkout> pull --ff-only`. If it is on
  another branch, or the fast-forward fails, run the step from a detached checkout of the merge SHA
  (`git worktree add --detach .claude/worktrees/<name> <sha>`, removed afterwards). Otherwise log a
  hold naming the exact command.
- In a repo with a bun lockfile (`bun.lock` or `bun.lockb`), install from it once the checkout sits
  at the merge and before any gate, build, link or deploy: run `bun install --frozen-lockfile` in the
  directory that holds the lockfile. A fast-forward moves source, never `node_modules`: a checkout
  that last installed before a lockfile or `patchedDependencies` change builds, deploys and fails its
  gates on the old dependencies, and a detached checkout has no `node_modules` at all. Run it every
  time, not only when the lockfile changed: the stale tree can predate the pull. The flag installs
  exactly what merged and leaves the lockfile alone in the shared checkout, where a plain
  `bun install` can rewrite it. A failed install, or a lockfile the flag refuses, is a step that
  cannot run: log a hold naming the command and its error line, and run no gate or deploy from that
  tree.
- A step that loads secrets or starts long-lived processes under an operator-managed runner is an
  operator action. Log it as a hold with the exact command.
- A step that reaches prod infra, runs migrations or touches destructive data is a hold, even under
  the LGTM.

## Prove it

The proof is an observation of the deployed state, not the step's exit code. Put the proof command
and its output in the ledger row.

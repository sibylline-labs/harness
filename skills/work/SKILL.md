---
name: work
kind: workflow
description: The work workflow for one issue, in ordered stages — write an implementation plan (`/work plan`), gate it, then implement it from thoughts/shared/plans (`/work implement`) with verification. Use to create, iterate on or implement a technical plan.
skills: [plan-shape, test-driven-development]
---

# Work

One orchestrator for a unit of work. Each stage is a reference read when the run reaches it; gates
that are useful on their own stay standalone skills and are invoked, not inlined.

## Stages

Run them in order. A stage starts only when the one before it is done. The first column is the stage
ref the profiles name.

| Stage | What it does | Read or run |
|---|---|---|
| understand-scope | read the issue, restate it, classify its user impact (`user-impact@1`), choose the profile, record the receipt naming the trigger and the class | [references/understand-scope.md](references/understand-scope.md) |
| prepare-env | worktree or workbench, install, the branch-point baseline, the pragma sites | [references/prepare-env.md](references/prepare-env.md) |
| plan | research the issue, write the plan in `thoughts/shared/plans/`, commit it first, push, and open the issue's single draft PR | [references/plan.md](references/plan.md) |
| research | when the trigger fires on a library the plan uses, cache its pinned docs, execute one load-bearing API, record the receipt | [references/research.md](references/research.md) |
| premise-gate | observe every load-bearing premise the plan rests on, write `thoughts/shared/premise/<YYYY-MM-DD>-<KEY>.md`, record the receipt | `/premise-gate` |
| sdk-check | find the SDK primitives the plan lacks, route each gap, write `thoughts/shared/sdk-check/<YYYY-MM-DD>-<KEY>.md` and record the receipt | [references/sdk-check.md](references/sdk-check.md) |
| plan-review | judge the plan against `plan-shape@1` and the design invariants; record the receipt | `/plan-review` |
| implement | carry out the frozen, reviewed plan, in the main loop or by dispatch | [references/implement.md](references/implement.md) |
| floor-evidence | record one receipt per requirement of the class's floor (`revert-path`, ...), each on a real artifact; U0 records none | [references/floor-evidence.md](references/floor-evidence.md) |
| final-gates | posture, baseline diff and rubrics; record the receipt, then the profile check, which flips the draft PR ready on exit 0 | [references/final-gates.md](references/final-gates.md) |

`/work plan <ticket or file>` starts at understand-scope. `/work implement <plan path>` starts at the
implement stage and runs the plan gate's Step 0 check first. A PRD or RFC goes to `/prd-review`
instead of the plan gate.

## Profiles

[`profiles.yaml`](profiles.yaml) holds `spine` and `deep`, each the ordered list of the stages that
record a receipt; `prepare-env`, `plan`, `implement` and `floor-evidence` run in every profile, and
`research` runs when its trigger fires. `understand-scope` picks the profile and proposes the class.
`floor-evidence` is in no profile: its receipts are named after the class's requirements, and
`eris gate check` derives those gates from the class and prints each as its own row. The run ends on

```bash
eris gate check --issue <KEY> --profile <spine|deep> --profiles ~/.claude/skills/work/profiles.yaml \
  --expect <the comment ids the run's record calls printed>
```

which exits 3 when any gate the profile lists has no passing receipt, or when an `--expect` id is not
yet readable. A gate the doctrine turns off is recorded `SKIPPED`, which passes. A `missing` receipt
is never healed by the run itself: only the session that ran a gate records it, and a receipt that
is missing at the end goes to the human or TPM to record (`plan-review` Step 0).

## Rules across stages

- The plan's shape is `plan-shape@1` (preloaded): the plan stage writes to it and `/plan-review`
  judges it.
- One draft PR per issue (or per repo when the issue spans several repos), opened at the plan stage.
  The `plan` stage commits `thoughts/shared/plans/<plan>.md` as the branch's first plan commit,
  pushes, and opens a single draft PR (`gh pr create --draft`) titled with `<KEY>`. Later gate notes,
  plan amendments (`/plan-review` `## Gate Amendments`), and implementation commits accrue on that
  same branch and PR; `final-gates` flips the PR ready (`gh pr ready`) when the profile check exits
  0. Never rebase or force-push a branch after recording a receipt, so `refs/pull/<N>/head` keeps
  every receipt's `blob/<sha>/<path>` link reachable after squash merge and branch deletion.
- **Closing vs contributing PR attachment:** Only the single PR that completes `<KEY>` (for a 1-PR
  issue, or the final PR in the merge order of a multi-PR issue) writes `Closes <KEY>` in its PR
  body and attaches in Linear with `type: "closes"`. Every other PR for `<KEY>` (earlier phase PRs
  or companion repo PRs in `cross-repo` work) is a **contributing PR**: its PR body starts with
  `Part of <KEY>` (keeping `<KEY>` in its branch name and PR title, since `Part of <KEY>` in the body
  overrides the branch-name closing link on merge) and its Linear diff link (`get_diff` `issueLinks`
  / `update_diff` `addedIssueLinks`) is `type: "contributes"` (if a merged contributing PR lacked
  `Part of <KEY>` and was branch-linked as closing, remove its attachment with `delete_attachment`).
- Commit and push every in-repo artifact before `eris gate record`. `eris gate record` refuses an
  uncommitted in-repo artifact (`"commit and push first"`) and deep-links `blob/<sha>/<path>`. Every
  stage that binds an in-repo file (`understand-scope`, `research`, `premise-gate`, `sdk-check`,
  `plan-review`, `floor-evidence`) commits and pushes that file before running `eris gate record`.
  (`final-gates` binds `<git-dir>/eris/final-gates.diff`, which lives in the git dir outside the
  worktree and is never committed.)
- **`linear-only` scope class (no repo diff):** When a run's deliverable produces no git repository
  diff (Linear issues, labels, comments, living docs such as `eris socrates` entries, read-only
  spikes, or operator files outside a repo working tree), `understand-scope` marks
  `scope: linear-only` and every stage writes its gate artifact under
  `G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"` (`$G/scope.md`, `$G/plan.md`, `$G/premise.md`,
  `$G/sdk-check.md`, `$G/floor-<requirement>.md`, `$G/final-gates.diff`). Paths under
  `<git-dir>/eris/` sit outside any worktree, so `eris gate record` classifies them as
  `{ _tag: "file" }`, skips the in-repo commit/push precondition, and attaches a gzip+base64
  `artifact.copy` to the `gate-receipt@v2` record (`eris gate check` falls back to that stored copy
  when the local file is gone). A `linear-only` run creates no worktree (`worktree: none`), makes no
  commits or `git push` calls, and opens no draft PR.
- Every receipted artifact is write-once. Each gate binds its own file (`understand-scope` →
  `thoughts/shared/scope/` or `$G/scope.md`, `premise-gate` → `thoughts/shared/premise/` or
  `$G/premise.md`, `sdk-check` → `thoughts/shared/sdk-check/` or `$G/sdk-check.md`, `plan-review` →
  `thoughts/shared/plans/<plan>.md` or `$G/plan.md`, `final-gates` → `<git-dir>/eris/final-gates.diff`
  or `$G/final-gates.diff`), and no later stage edits a file an earlier stage's live receipt binds.
- The reviewed plan is frozen. Only `/plan-review` binds `thoughts/shared/plans/<plan>.md` (or
  `$G/plan.md` on a `linear-only` run); any edit after review reads as `drift`, so amend the plan,
  commit and push the amendment as a new commit (for in-repo plans), and re-run `/plan-review`
  instead.
- Wait on an ask without polling. After raising an `eris ask` the run needs answered to proceed, end
  the turn: the harness re-invokes the session on an answer, a new comment on the issue, a closed
  ask or the TTL. Never poll for it.
- Divide by context, not problem type: 1–3 tasks or tightly coupled edits stay in the main loop; 4+
  independent phases dispatch to `impl-*` agents.

## Handoff

The `final-gates` stage ends the run: on exit 0, it flips the issue's draft PR ready (`gh pr ready`;
skipped on a `linear-only` run, which has no PR and reports `worktree: none`), posts the issue
comment with what changed, the gate check lines and any `follow-ups:` (or `needs input: ask <id>`
only for a human-only action), moves the issue to In Review, and ends with a final `result:` line; on
exit 3, the PR stays draft and the failing lines are posted as the blocker.

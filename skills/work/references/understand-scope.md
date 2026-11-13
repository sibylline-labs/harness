# Stage: understand-scope

The first stage of every run: what changes, where, why and how, its user-impact class, and which
profile the run takes. It writes a scope note and records an
`understand-scope` receipt naming the profile, the trigger that chose it and the class. Both profiles list `understand-scope`, so a run that never
recorded one fails `eris gate check --profile`.

## 1. Read the issue

Read the issue description and every comment in full; a comment overrides the description. Read the
parent Epic's arc line for this issue, and any comment routed here from another issue. Note any
standing operating notices and the active doctrine already in context; do not bulk-read the
rules directory.

**Done when:** you can say which comment, if any, overrides the description.

## 2. Restate it

One sentence on what will change (states, files, tokens), and one line per term you are
interpreting. Ask only if a term is genuinely ambiguous.

When the deliverable writes no tracked file in any git repository — Linear issues, labels, comments,
or Socrates living docs (e.g. an `eris socrates` entry, or a read-only spike whose output is
Linear docs and issues), or operator files outside a repo working tree — mark the run
**`linear-only`**. A `linear-only` run stays in the current checkout (the repo the session started
in, or the repo that owns the subject doc or service) and writes every gate artifact to
`G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"` with no worktree (`worktree: none`), no commits
and no draft PR.

**Done when:** the sentence names the repo and the files or surfaces it touches (or marks `scope: linear-only` and names the Linear / operator-file deliverables).

## 3. Classify the user impact

Load `/user-impact` and apply `user-impact@1` to the restated change: the class (`U0`–`U3`) and one
line on what reaches it from an external entry point. Classify now, not at the end: the class
decides which receipts the `floor-evidence` stage records, so the plan carries that evidence
(a revert path for U1, a zero-downtime shape and an e2e run for U2, a rehearsed rollback for U3,
plus anything the active doctrine's `policy.user_impact` adds: `business-as-usual` and `lock-in`
add `e2e` to U1; `eris doctrine gates` prints the effective set as `@user-impact` rows).
When unsure between two classes, take the higher: a later receipt can raise the class without a
grant, but lowers a U2 or U3 only with `--authorized`. A doctrine whose `escalate_on` names `U2` or
`U3` reads this class in the next step.

**Done when:** the scope note has a `## Class` line, `<U-class>: <what reaches the change>`.

## 4. Choose the profile

The profiles live in [`../profiles.yaml`](../profiles.yaml). Start at the active doctrine
posture's `policy.profile_default` (the `*` row of `eris doctrine check`; the posture's fenced
`policy:` block in the doctrine file), else `spine`. Escalate to `deep` when a trigger
holds:

| Trigger | Holds when |
|---|---|
| `estimate>=4` | the issue's estimate is 4 points or more |
| `new-surface` | the change adds a service, CLI verb, route family, skill kind, queue or store no sibling has |
| `cross-repo` | the change edits, or needs a change in, a second repo |
| `sdk-gap` | the change needs an SDK primitive that is missing (the `sdk-check` stage confirms it) |

When the active posture's policy carries `escalate_on`, its list replaces this table (doctrine
wins); a trigger in the table that held but is not in that list is named as `overridden`.

A trigger found after this stage (the plan meets an SDK gap, a second repo turns up) escalates the
run then: write a new scope note and record a new receipt. The latest receipt wins.

**Done when:** each trigger is marked `held` or `quiet`, with the fact behind it.

## 5. Write the scope note and record the receipt

Write `thoughts/shared/scope/<YYYY-MM-DD>-<KEY>.md` in the target repo (creating the issue's
worktree from `origin/main` per `prepare-env` step 1 first if not already in it): the restatement,
the term lines, the class line, and the trigger table with each mark. Commit and push the scope note
on the issue's branch before calling `eris gate record` (it refuses an uncommitted in-repo
artifact with `"commit and push first"`). The receipt binds the note's
sha256, so leave it unchanged once recorded.

```bash
git add thoughts/shared/scope/<YYYY-MM-DD>-<KEY>.md
git commit -m "docs(scope): record understand-scope for <KEY>"
git push -u origin HEAD
eris gate record understand-scope --issue <KEY> --verdict PASS \
  --artifact thoughts/shared/scope/<YYYY-MM-DD>-<KEY>.md --doctrine <doctrine file> \
  --rubric user-impact@1 --impact <U0-U3> \
  --evidence "profile: deep; trigger: estimate>=4 (8 pts), cross-repo (eris)" \
  --evidence "class: U1: new /v1/errands field behind flag errand_eta"
```

For a **`linear-only`** run (no git repo diff), write `$G/scope.md` inside the git dir
(`G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"`, untracked so `eris gate record` stores
`{ _tag: "file" }` plus a gzip+base64 `artifact.copy` on the receipt, with no commit or push) and include
`scope: linear-only` in the first `--evidence` line:

```bash
G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"; mkdir -p "$G"
eris gate record understand-scope --issue <KEY> --verdict PASS \
  --artifact "$G/scope.md" --doctrine <doctrine file> \
  --rubric user-impact@1 --impact <U0-U3> \
  --evidence "profile: <spine|deep>; scope: linear-only; trigger: <held triggers>" \
  --evidence "class: <U0-U3>: <what reaches the change>"
```

The first evidence line is `profile: <p>; trigger: <held triggers, each with its fact>`, or
`trigger: none` for a run that stays on its default. Add `; overridden: <triggers>` when the
doctrine dropped one. The second is the class line from step 3. If `record` fails, report its
error line and go on: the final check fails closed on the missing receipt, and the human or TPM
records it.

**Done when:** `record` printed the comment id, the receipt carries `--impact`, and the run's final
check names this profile:
`eris gate check --issue <KEY> --profile <p> --profiles ~/.claude/skills/work/profiles.yaml`.

# Stage: floor-evidence

Prove what the user-impact class requires, so the run's final check meets the floor without a
steer. Runs in every profile, after `implement` and before `final-gates`.
It records one receipt per requirement of the class, each named after the requirement. It records
no `floor-evidence` receipt, so no profile lists it: `eris gate check` derives the requirement
gates from the class and prints each as its own row (`revert-path\tmissing\t-`).

## 1. Read the class

The class is the one `understand-scope` recorded (`--impact`), or a higher one if the diff as built
reaches further: re-apply `user-impact@1` to the diff. Raise it on this stage's first receipt
(`--impact <higher>`). Never lower it here: lowering a U2 or U3 needs a human's `--authorized` grant.

A class owes its hard floor (`USER_IMPACT_FLOOR` in eris, the table in `/user-impact`) plus
whatever the active doctrine posture's `policy.user_impact[class]` adds; `eris gate check
--profile` enforces the union. Read the effective set, not the table:

```bash
eris doctrine gates --profiles ~/.claude/skills/work/profiles.yaml | grep '^@user-impact'
```

Each `@user-impact<TAB><class><TAB><req,...>` row is one class's set, and a class with no row owes
none. With no rows at all (no doctrine policy), the hard floor applies:

| Class | Hard floor |
|---|---|
| U0 | none |
| U1 | `revert-path` |
| U2 | `revert-path`, `zero-downtime`, `e2e` |
| U3 | `revert-path`, `zero-downtime`, `e2e`, `rollback-rehearsal` |

`business-as-usual` and `lock-in` raise U1 to `revert-path`, `e2e`, so a U1 run under them also
records `e2e`; `rapid-prototype` adds nothing.

**Done when:** the class is named, with the receipts its effective set owes.

## 2. Produce each artifact

Each receipt stands on an artifact the change really produced, never on prose written to fill the
slot. Write notes to `thoughts/shared/floor/<YYYY-MM-DD>-<KEY>-<requirement>.md`, commit them, and
push them on the issue's branch before calling `eris gate record` (it refuses an uncommitted in-repo
artifact with `"commit and push first"`); keep logs under 16 KiB
(record the part the gate relied on).

| Requirement | The artifact |
|---|---|
| `revert-path` | the revert, run: `git revert --no-commit <sha>` on a scratch branch with the tests green, or the flag flipped off and the behaviour shown gone. The note quotes the command and its output |
| `zero-downtime` | the deploy shape that keeps serving: expand/contract migration order, both versions running against one schema, the traffic split. The note names the order and the check that proved it |
| `e2e` | an end-to-end run through the real entry point (`--e2e <log>`) |
| `rollback-rehearsal` | the rollback, performed on a non-production copy, with the data checked after (`--log <log>`) |

A requirement the change cannot meet is a finding for the human, not a `SKIPPED`: `SKIPPED` never
meets the floor. Post it on the issue and stop.

**Done when:** each requirement has its artifact on disk.

## 3. Record the receipts

From the worktree root, commit and push each note on the issue's branch first, then
record one receipt per requirement:

```bash
git add thoughts/shared/floor/<YYYY-MM-DD>-<KEY>-revert-path.md
git commit -m "docs(floor): record revert-path evidence for <KEY>"
git push
eris gate record revert-path --issue <KEY> --verdict PASS \
  --artifact thoughts/shared/floor/<YYYY-MM-DD>-<KEY>-revert-path.md \
  --rubric user-impact@1 --impact <class> --doctrine <doctrine file> \
  --evidence "revert: <command> -> <result>"
```

On a **`linear-only`** or operator-file run (normally `U0`; when classed `U1`+), write
`$G/floor-<requirement>.md` (`G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"`) and record without
`git commit` or `git push`:

```bash
G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"; mkdir -p "$G"
eris gate record revert-path --issue <KEY> --verdict PASS \
  --artifact "$G/floor-revert-path.md" \
  --rubric user-impact@1 --impact <class> --doctrine <doctrine file> \
  --evidence "revert: <command> -> <result>"
```

Add `--e2e <log>` on `e2e`, `--log <log>` on `rollback-rehearsal`. Keep each comment id `record`
prints for the final `--expect`. If `record` fails, report its error line and go on: the final check
fails closed on the missing receipt, and the human or TPM records it.

**Done when:** every requirement of the class has a recorded `PASS`, or the class is U0.

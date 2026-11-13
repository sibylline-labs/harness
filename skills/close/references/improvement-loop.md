# Stage: improvement-loop

The `tpm-merge` and `next` close profiles' stage that turns a finished issue's code into at most five
leaner-codebase suggestions a day per project, filed under one Epic. A suggestion makes the code
smaller or simpler, with no feature, and is judged by `improvement@1`
([`improvement`](../../improvement/SKILL.md)). The stage never dispatches anything: each suggestion
carries `dispatch: allowed` or `dispatch: withheld`. Under `next` the scoped `/tpm` report reads it.
Under `tpm-merge` the `close-ledger` stage lists each `dispatch: allowed` suggestion on its
`follow-ups:` line for the TPM that merged the PR.

All Linear writes go through `/linear-workflow`.

## 1. Gate

Decide whether the stage runs. Read three things:

- **Doctrine.** `eris doctrine gates` prints the active posture's `close.improvement-loop` mode:
  `on` (file, and mark each suggestion `dispatch: allowed`), `file-only` (file, mark
  `dispatch: withheld`) or `off`. A posture with no policy, or no `close.improvement-loop`, is `on`.
- **Planned size.** The `est` half of the issue's `effort:` row in this run's ledger (points, or
  `none`; `none` is 0). The `linear` stage has already overwritten Linear's `estimate` with the
  actual, so neither the Linear field nor a comment holds the plan at this point: take it from the
  ledger. An issue the run did not close has no `effort:` row; use its current `estimate`.
- **Project.** The primary issue's project. No project means nowhere to file.

| Result | Then |
|---|---|
| doctrine `off` | Stop. Record nothing: `eris gate check` writes the doctrine `SKIPPED`. Put `improvement-loop skipped · doctrine <posture>: close.improvement-loop off` in the close ledger |
| planned estimate under 4 | Record the no-op (below) and stop |
| no project, or the doctrine unreadable | Record the no-op with that reason as evidence, and stop |
| otherwise | Go on, in the mode the doctrine names |

The no-op receipt, with this file as the artifact:

```bash
eris gate record improvement-loop --issue <KEY> --verdict PASS \
  --artifact ~/.claude/skills/close/references/improvement-loop.md \
  --evidence "no-op: planned estimate N < 4"
```

**Done when:** the result is in the ledger, and a skip other than doctrine `off` has its receipt.

## 2. Find candidates and judge them

Read the merged diff and the files it touched, and look for code that could shrink: a hand-rolled
helper a library or sibling already provides, a duplicated branch, a dead path, a dependency only one
call site uses. Load `/improvement` and judge each candidate. Keep only `PASS`, and write the measure
as the rubric asks (`-40 LOC: …`, `C901 14 → 6`). Five is the daily cap, so put the strongest first.

Write the candidates to `thoughts/shared/improvement/<YYYY-MM-DD>-<KEY>.json` in the repo the diff
landed in:

```json
[{"title": "Collapse the three retry loops onto with_retry", "paths": ["src/a.py", "src/b.py"],
  "measure": "-60 LOC: three hand-rolled loops replaced by the existing helper",
  "verdict": "PASS", "body": "What changes, where, and how the existing tests pin it."}]
```

**Done when:** every candidate in the file has a verdict, and each `PASS` states a measure.

## 3. File and record

Each suggestion's identity is a **hash**: the first 12 hex characters of the sha256 of the title
and the sorted paths, joined by the unit separator (`\037`). Describe the change rather than the
session, so the same idea found tomorrow hashes the same and is not filed twice:

```bash
{ printf '%s' "<title>"; for p in <sorted paths>; do printf '\037%s' "$p"; done; } \
  | shasum -a 256 | cut -c1-12
```

Then, per project and UTC day:

1. **Find or create the day's Epic**, titled `[improvement-loop] <project> — <YYYY-MM-DD>`: search
   the project's issues by that title first (`list_issues`), and create it only when absent, with the
   workspace's existing `Epic` label.
2. **Skip duplicates.** A suggestion whose `hash: <12 hex>` line already sits on any issue in the
   project, in any state, is a duplicate and is not filed again. A canceled suggestion is how a human
   rejects one.
3. **File up to five** `PASS` suggestions as children of the Epic (`parentId` by UUID), each with
   the existing `Improvement` label, the measure, a `hash: <12 hex>` line, and
   `dispatch: allowed` (mode `on`) or `dispatch: withheld` (mode `file-only`) in its description.
   The rest are `over_cap`; their code stays and a later run can file them.
4. **Record the receipt:**

```bash
eris gate record improvement-loop --issue <KEY> --verdict PASS --rubric improvement@1 \
  --artifact thoughts/shared/improvement/<YYYY-MM-DD>-<KEY>.json \
  --evidence "epic <identifier> (created|found); filed N, duplicate N, rejected N, over_cap N; dispatch <allowed|withheld>"
```

A Linear failure is a `--verdict BLOCKING` receipt with its error as evidence. A rerun is safe: the
Epic is found by its title, and a hash already filed is skipped.

**Done when:** the receipt's comment id is in the close ledger.

## Verdicts

To calibrate `improvement@1`, read each filed suggestion's outcome from its state type: completed is
accepted, canceled or duplicate is rejected, anything else is open.

# Stage: final-gates

The last stage of every run: prove the change against its branch-point baseline and its rubrics,
record the `final-gates` receipt, then let `eris gate check --profile` decide whether the run ends.
**The stage's exit code is the check's.** A missing, blocking or drifted receipt exits 3 and stops
the loop: the issue stays In Progress.

Runs once, at the end (`gates: { final-gates: once-at-end }` under rapid-prototype), after the last
commit is pushed. A fix-forward commit after step 4 means running the stage again from step 1.

## 1. Posture

Run `/posture-check` on the diff; it also checks any governance site (a config key, a service
seam, a queue, an event) the diff changed. On a **`linear-only`** or operator-file run, no git repo
diff touches a registered surface, so skip `/posture-check` (`posture: n/a (linear-only)`).

**Done when:** posture prints its 3-line result with no `BLOCKING` (or `n/a (linear-only)`).

## 2. Baseline diff

From the worktree root:

```bash
eris baseline diff
```

It reruns every `ci.local` gate and the pragma leg against what `prepare-env` recorded:
`new-failure` and `worse` exit 3; `pre-existing` is ignored; `fixed` and `improved` are credited.
Keep the stdout lines for the evidence comment.

On `baseline-no-ci-local` (the repo has no `ci.local`), run the repo's test and lint commands once
and compare the failing lines with the plan's current-state section: a failure not listed there is
new. On `baseline-missing`, `prepare-env` was skipped: say so in the evidence, and treat every
failure as new. On a **`linear-only`** or operator-file run, skip `eris baseline diff` and report
`baseline: n/a (linear-only)`.

**Done when:** no gate reads `new-failure` or `worse`, each new failure is fixed and step 2 re-run,
or `n/a (linear-only)`.

## 3. Rubrics

Load `/verification-before-completion` and grade the diff with the rubrics it judges. Two always
reach this stage:

- `user-impact@1`: re-judge the class `understand-scope` proposed against the diff as built, with one
  line on what reaches the change. It becomes `--impact`: the same class, or a higher one when the
  diff reaches further than scoped. Never a lower one without `--authorized <grant>` from a human. A
  raised class owes the new requirements: run `floor-evidence` again for them before recording
  here. Its evidence is the `floor-evidence` receipts.
- `unit-test-admission@1`, when the diff adds a test: list the tests added since the recorded
  branch-point base `$B` that carry no `admits:` comment, then read every new test for a tautology.
  `$B` is the base `prepare-env` recorded (step 4 below shows how it resolves); when the branch has
  merged main in, advance it to the merge-base with `origin/main`, so tests main brought in are not
  judged as the branch's own.

  ```bash
  git diff -U0 --no-ext-diff --no-color "$B" HEAD -- '*test*' '*spec*'   # the added test lines
  ast-grep scan --filter test-no-admits <the test files the diff touches> # when the repo carries the rules
  ```

  Read only hits that overlap lines this branch added: a pre-existing test with no comment is not
  this change's debt. A listed test that is load-bearing is `AMENDED`; a tautology is `BLOCKING`.

**Done when:** each rubric has its verdict and one line of reason.

## 4. Record the receipt

The verdict is `BLOCKING` if any step above blocks, `AMENDED` if a rubric amended, else `PASS`. The
artifact is the branch's diff against `$B` (resolved from `baseline.json` `.merge_base`,
`final-gates.base`, or `git merge-base "$BASE_REF" HEAD` with `BASE_REF="origin/<stack-base>"` on a
stacked branch), written to the git dir so it is never committed:

```bash
BASE_REF="${BASE_REF:-origin/main}" # stacked branch: BASE_REF="origin/<stack-base>"
A="$(git rev-parse --absolute-git-dir)/eris/final-gates.diff"; G="$(dirname "$A")"; mkdir -p "$G"
B="$(jq -r '.merge_base // empty' "$G/baseline.json" 2>/dev/null)"
[ -n "$B" ] || B="$(cat "$G/final-gates.base" 2>/dev/null)"
[ -n "$B" ] || B="$(git merge-base "$BASE_REF" HEAD)"
printf '%s\n' "$B" > "$G/final-gates.base"
git diff --no-ext-diff --no-color "$B" HEAD > "$A"
test -s "$A"
eris gate record final-gates --issue <KEY> --verdict <PASS|AMENDED|BLOCKING> --artifact "$A" \
  --rubric user-impact@1 --rubric unit-test-admission@1 --doctrine <doctrine file> \
  --impact <U0-U3> --evidence "base: $B" --evidence "baseline: <one line>"
```

When `prepare-env` ran on a stacked branch (`BASE_REF="origin/<stack-base>"`), `baseline.json`
(`.merge_base`) and `final-gates.base` already hold the stack base's 40-hex merge-base SHA `$B`. When
`prepare-env` was skipped, set `BASE_REF="origin/<stack-base>"` so the fallback
`git merge-base "$BASE_REF" HEAD` resolves against the unmerged stack base rather than `origin/main`
(and if an earlier command wrote `origin/main`'s merge-base into `"$G/final-gates.base"` on a stacked
branch, refresh it first with `git merge-base origin/<stack-base> HEAD > "$G/final-gates.base"`).

On a **`linear-only`** or operator-file run, `git diff` is empty because no repo tracked file
changed. Write a deterministic verification artifact to `A="$G/final-gates.diff"`
(`G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"`): for a Linear-only task, write the verified
Linear read-back summary (issue IDs, states/labels, comment/doc IDs); for an operator-file task,
write the unified diff against the `prepare-env` snapshot
(`diff -u "$G/before/<file>" "<live-file>" > "$A" || true`). Then record `final-gates` against
`"$A"`:

```bash
G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"; mkdir -p "$G"
A="$G/final-gates.diff"
eris gate record final-gates --issue <KEY> --verdict <PASS|AMENDED|BLOCKING> --artifact "$A" \
  --rubric user-impact@1 --doctrine <doctrine file> \
  --impact <U0-U3> --evidence "baseline: n/a (linear-only)"
```

Drop `--rubric unit-test-admission@1` when the diff adds no test. Keep the comment id `record`
prints, beside the ids the run's earlier `record` calls printed. If `record` fails, report its error
line, hand the exact command to the human or TPM, and go on: step 5 fails closed on the missing
receipt.

**Done when:** `record` printed the comment id, or its failure and the handed-off command are
written.

## 5. Check the profile

Regenerate the artifact against the recorded branch-point base `$B` (never the live
`git merge-base origin/main HEAD`, which becomes `HEAD` once the PR merges and produces a 0-byte
diff), so code pushed (or an operator file edited) after the receipt reads as `drift` (for a
`linear-only` run, re-run the operator-file `diff -u` into `"$A"` or leave the Linear read-back note
at `"$A"` untouched — never overwrite `"$A"` with an empty `git diff`), then check:

```bash
B="$(cat "$G/final-gates.base" 2>/dev/null)"
[ -n "$B" ] || B="$(jq -r '.merge_base // empty' "$G/baseline.json" 2>/dev/null)"
git diff --no-ext-diff --no-color "$B" HEAD > "$A"
test -s "$A"
eris gate check --issue <KEY> --profile <spine|deep> --profiles ~/.claude/skills/work/profiles.yaml \
  --expect <every comment id this run's record calls printed, comma-separated>
```

Pass the full UUIDs (an 8-character prefix never matches). `--expect` re-reads for about 30 s and
exits 3 with `gate-receipt-unseen` if one never shows, so a receipt written seconds ago is never read
as absent and a fresh `BLOCKING` never hides behind an older `PASS`. Ids older than a minute may be
dropped from the list.

- **Exit 0**: flip the issue's draft PR ready for review (`gh pr ready`), confirm every PR for
  `<KEY>` is attached in Linear (`get_diff` `issueLinks` / `update_diff` `addedIssueLinks`) as
  `closes` (`Closes <KEY>`) on the single PR that completes `<KEY>` and `contributes`
  (`Part of <KEY>`) on every contributing PR (on a `linear-only` run, skip `gh pr ready` and PR
  attachment since there is no PR, and report `worktree: none` on the hand-back's last line), post
  the evidence comment (what changed, steps 2–3 in a line each, and the check lines quoted), then
  move the issue to In Review. A question a house default answers is not an ask: apply the default
  and say so. Reserve `needs input:` for actions only a human can take: minting or storing a secret,
  a prod deploy, a ruleset or permission change, custody of customer credentials, or a true one-way
  door (each line carrying `ask <id>`); before writing `needs input:`, name which human-only class it
  is; if none, it is a follow-up. Put everything else under `follow-ups:`, never under
  `needs input:` (post-merge verification, syncing the harness, "TPM should check X", "merge after
  Y", and suggested next issues; file any follow-up you can and cite its issue ID). A clean exit is:
  PR open and green, issue In Review, a hand-back comment posted, and a final `result:` line.
  Nothing more.
- **Exit 3**: stop. Leave the PR in draft and the issue In Progress, and post the failing check
  lines as the blocker. `missing` is recorded only by the session that ran that gate, or by the
  human or TPM; `drift` means re-running the gate on the changed artifact. Never re-record a receipt
  to make the check pass. When `eris doctrine gates` prints `@remediate\ton\t…` naming
  `final-gates-fail` and the failure is a review's open findings, run
  `eris gate remediate --issue <KEY> --on final-gates-fail` and quote its line in the blocker:
  `launched` (a remediation round now fixes the findings and reports to the issue), `pending` (a
  round is already open), `off`/`nothing` (no round applies), or `hand-off` (exit 3: `max_rounds`
  reached; the human signs off with every round's report). Then stop: the remediation session, not
  this one, pushes the fix.

**Done when:** the check exited 0, the PR is marked ready (`gh pr ready`), and the issue is In
Review, or it exited 3 and the blocker is posted.

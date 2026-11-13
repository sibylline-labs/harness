# Review report mode — emitting `review-report@1`

A review that `eris gate` can verify: which PR head and diff it read, at what effort, by whom, with which
version of this skill and which vocabulary, and every finding typed. The report has **no verdict**:
`eris gate check` derives pass from it. The schema is printed by `eris gate schema review-report`.

The model reviews and judges. `scripts/review_report.py` computes every digest and writes the file; never
type a sha by hand.

## Steps

Run from the PR's checkout, at the PR head, with nothing to commit afterwards (a later commit moves the
head and the report reads as drift).

1. **Prepare.**

   ```bash
   S=~/.claude/skills/thermo-nuclear-code-quality-review/scripts/review_report.py
   CTX=$("$S" prepare --pr <N> [--surface <name>] [--vocabulary <repo path>])
   ```

   It refuses when local `HEAD` is not the PR head, or when the skill dir has uncommitted changes. It
   writes `diff.patch` and `context.json` beside each other under `<git-dir>/eris/review-<N>/`. The
   surface defaults to `code-quality`, with [`code-quality-classes.md`](code-quality-classes.md) as its
   vocabulary. Any other surface reads `thoughts/vocabulary/<surface>.md` from the PR's repo.

2. **Review in fresh context.** Dispatch the reviewer subagent(s) the effort row names, each with the
   reviewer brief below and nothing else from this session: no plan, no chat, no author reasoning.

3. **Verify.** Dispatch the verifier(s) the effort row names with the verifier brief. A finding the
   verifier refutes gets `status: refuted`, with the refutation appended to its `evidence`. Otherwise it
   stays `open`.

4. **Emit.** Write the findings JSON (an array of `{id, severity, class, file, line, status, evidence}`)
   and a prose body. Then run:

   ```bash
   "$S" emit --context "$CTX" --findings findings.json --body body.md \
     --effort <low|medium|high|max> --model <your model id> --author <PR author actor> --fresh-context
   ```

   `--actor` defaults to `session:$CLAUDE_CODE_SESSION_ID`. `--author` is the actor that wrote the PR,
   which for an agent PR is the implementing session. Pass `--fresh-context` only when steps 2–3 ran in
   subagents given just the brief. `emit` refuses if the head or diff moved since `prepare`, if a finding's
   class is not in the vocabulary, if the skill or the vocabulary changed since `prepare`, if a line is not
   an integer ≥ 1, if a text field is empty or not a string, or if two findings share an id. It prints the
   report path, `<git-dir>/eris/review-report-<N>.md`.

5. **Record** (when a gate needs it):

   ```bash
   eris gate record <gate> --issue <KEY> --review-report <report path>
   eris gate check --issue <KEY> --gates <gate> [--effort <required>]   # derived pass, effort floor
   ```

   The verdict is derived at record time; `--effort` is a `gate check` floor. The report lives in the git
   dir, so it is a `file` artifact and needs no commit.

## Effort

These levels are borrowed from native `/code-review`, which runs from a few high-confidence findings up to
many.

| effort | reviewer passes | findings reported | verify pass |
|---|---|---|---|
| `low` | 1 | `blocking`/`major` with high confidence only | each `blocking`/`major` |
| `medium` | 1 | all severities | each `blocking`/`major` |
| `high` | 1 | all severities | every finding |
| `max` | 2 independent: a structure lens (Q1–Q5) and a boundary lens (Q6–Q8 + surface classes), then merged and de-duplicated | all severities | every finding, one fresh verifier each |

`classes_checked` is always the whole vocabulary. A pass that skips a class has not checked it, so run
every class at every effort.

## Severity

| severity | when (from SKILL.md's Approval Bar) |
|---|---|
| `blocking` | a presumptive blocker: kept complexity with a plain code-judo path, a file pushed past 1000 lines, ad-hoc branching that tangles a flow, scattered feature checks, an indirect wrapper/cast contract, a duplicated helper or wrong layer |
| `major` | a structural regression or missed simplification short of a blocker |
| `minor` | a legibility or maintainability concern |
| `nit` | cosmetic |

An open `blocking` or `major` finding fails the derived pass.

## Reviewer brief

> You are a code-quality reviewer in a fresh context. Read `<skill dir>/SKILL.md` (the rubric) and
> `<vocabulary path>` (the classes). Review the unified diff at `<diff.patch>`, reading the repo at
> `<checkout>` for surrounding code as needed. [max only: Your lens is <structure: Q1–Q5 | boundary:
> Q6–Q8 and the surface classes>.] Check every class in the vocabulary. Return only a JSON array of
> findings `{id, severity, class, file, line, status: "open", evidence}`, where `class` is a vocabulary
> class ID, `file` is repo-relative, `line` is a line in the new file (≥ 1), and `evidence` quotes the code
> and says why it is that class. Severity follows the table in `references/review-report.md`. Return `[]`
> when nothing clears the bar. Do not pad the list.

## Verifier brief

> You are verifying one review finding in a fresh context. Here is the finding `<json>`. The diff is at
> `<diff.patch>` and the repo at `<checkout>`. Try to refute it. Is the code really as quoted? Does the
> class apply? Is the severity justified by the table in `references/review-report.md`? Return
> `{"id", "verdict": "confirmed" | "refuted" | "downgraded", "severity"?, "reason"}`.

Apply the result to the finding. `confirmed` leaves it as it is. `refuted` sets `status: refuted` and
appends the reason. `downgraded` sets the new severity and appends the reason. A refuted finding counts
only when someone other than its raiser agrees, and the verifier is that someone.

## Digest contract

The `eris gate check` checkers recompute these values, so they must stay equal to them.

| field | value |
|---|---|
| `target.repo` | `owner/name` of the checkout's `origin` |
| `target.head_sha` | `git rev-parse HEAD`, which must equal the PR's `headRefOid` |
| `target.diff_sha256` | sha256 of the stdout of `git diff --no-ext-diff --no-color <merge-base origin/main HEAD> HEAD`, which is what `eris gate check` derives. The base is always `origin/main`, because that is the base `gate check` recomputes against |
| `reviewer.skill.name` | this skill's directory name |
| `reviewer.skill.harness_sha` | `HEAD` of the repo that holds this skill's source (the harness checkout the skills are installed from) |
| `reviewer.skill.sha256` | sha256 of the manifest `"<path relative to the skill dir>\0<sha256 hex of the blob bytes>\n"`, one line per blob under `skills/<name>/` in `git ls-tree -r <harness_sha>`, sorted by path. Blobs, not working-tree bytes, so symlinks, eol filters and `skip-worktree` cannot skew it, and the value is reproducible from `harness_sha` alone. A dirty skill dir is refused, so the reviewer read what the digest names |
| `reviewer.vocabulary.path` | repo-relative, except the default, which is harness-relative (`skills/thermo-nuclear-code-quality-review/references/code-quality-classes.md`) |
| `reviewer.vocabulary.sha256` | sha256 of the vocabulary file's bytes |
| `classes_checked` | the vocabulary's `## Class <ID> — ` heading IDs, in file order |

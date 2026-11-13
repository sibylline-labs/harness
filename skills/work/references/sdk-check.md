# Stage: sdk-check

Find the primitives the plan needs that the SDK lacks, and route each gap before implementation
writes the logic in the consumer. The SDK is the shared library the organisation's services build
on (one per language, if there are several). A gap in the SDK is fixed in the SDK, never worked
around in the consumer.

Runs after the premise gate and before the plan gate, on the `deep` profile. The doctrine can turn
it off (`gates: { sdk-check: off }`); then don't run the stage and record nothing: the run's final
`eris gate check --profile deep` writes the doctrine `SKIPPED` itself (it reads the posture from
`--doctrine`), printing `doctrine: recorded sdk-check SKIPPED as doctrine:<posture>@<hash>`.
`eris gate record` refuses a SKIPPED verdict, and a bare posture name passed to
`eris gate skip --authorized` records as a human grant, so neither is the doctrine path. Off skips
only this planning-time gap search.

## 1. List the primitives the plan needs

Read the plan's phases and name each capability its code will reach for that is not business logic:
an HTTP call, a retry, config or secret reading, a schema, an error type, a CLI verb, a route
boundary, a DB query, a cache, a background task, a test double.

**Done when:** each primitive is one line naming the phase that needs it.

## 2. Look each one up in the catalogue

Read the SDK's own catalogue: its README export matrix or reference docs, one row per module. Confirm
a symbol in the SDK's source before you rely on it. Read the checkout the consumer actually installs
(its lockfile pin), not memory. A primitive the SDK has is not a gap, even if the consumer has a
second, hand-rolled way to do it today.

**Done when:** each primitive is marked `covered` with the SDK symbol, or `gap`.

## 3. Size each gap and route it

| Size | What it is | Route |
|---|---|---|
| **thin** | a param, a flag, or one small primitive in a module the SDK already has | file an issue in the SDK's project, and start a fresh `/work plan <ISSUE>` session in the SDK checkout for it. Implement against the released SDK when it lands, or proceed on the local route if the plan cannot wait |
| **large** | a new module, a primitive that spans modules, or an SDK that does not exist yet | build it locally in the consumer, behind a `lift-candidate` marker |

The marker is a comment on the line above the local primitive:

```ts
// lift-candidate: linear-pagination — cursor loop over a GraphQL connection
```

```python
# lift-candidate: retry-budget — bounded retries keyed to Retry-After
```

Name the pattern, not the call site. List every marker with plain text search:

```bash
rg -n 'lift-candidate:' <repo>
```

The `close` workflow's `lift-to-sdk` stage (`skills/close/references/lift-to-sdk.md`) consumes that
listing, judges each candidate and files the ones marked at two or more call sites.

**Done when:** each gap has a route: an SDK issue plus its session receipt line, or a marker at a
`file:line` (planned now, placed in the implement stage).

## 4. Record the receipt

Write `thoughts/shared/sdk-check/<YYYY-MM-DD>-<KEY>.md` in the target repo (the primitives from
step 1, the catalogue lookup from step 2, and each gap's route from step 3), commit and push that
note on the issue's branch (`eris gate record` refuses an uncommitted in-repo artifact with
`"commit and push first"`), then record one receipt per run against that note — never against the
plan file, which `/plan-review` amends in the next stage. The receipt binds the note's sha256, so
leave it unchanged once recorded. No gaps is a `PASS` with one `no gaps` line.

```bash
git add thoughts/shared/sdk-check/<YYYY-MM-DD>-<KEY>.md
git commit -m "docs(sdk-check): record sdk-check for <KEY>"
git push
eris gate record sdk-check --issue <KEY> --verdict PASS \
  --artifact thoughts/shared/sdk-check/<YYYY-MM-DD>-<KEY>.md \
  --doctrine <doctrine file> --impact <class> \
  --evidence "gap: <primitive> (<sdk>) -> thin: <SDK ISSUE>, session <session id>" \
  --evidence "gap: <primitive> (<sdk>) -> large: lift-candidate <file:line>"
```

On a **`linear-only`** or operator-file run (no repo code changes), write `$G/sdk-check.md`
(`G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"`) and record without `git commit` or
`git push`:

```bash
G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"; mkdir -p "$G"
eris gate record sdk-check --issue <KEY> --verdict PASS \
  --artifact "$G/sdk-check.md" \
  --doctrine <doctrine file> --impact <class> \
  --evidence "no gaps: linear-only (no repo code changes)"
```

Add each route to the plan before the plan gate, so `/plan-review` judges the plan that names it.

**Done when:** `record` printed the comment id.

---
name: plan-review
kind: gate
description: Pre-implementation design and invariant gate on a technical plan — runs in the main agent loop to stress-test precedent and library currency, class closure, type monotonicity, red-on-main lint proof, gate delta-invariance, remediation round-trip survival, k-step state/TOCTOU interleavings, and oracle budgets before code is written. Judges plans against `plan-shape@1`. Use after the `work` plan stage and premise-gate, before the `work` implement stage.
---

# Plan Review

Stress-test an implementation plan (`thoughts/shared/plans/*.md` or `thoughts/plans/*.md`) **in the main agent loop** after `premise-gate` has observed its substrate facts and before the `work` implement stage ([`work`](../work/SKILL.md)) dispatches code agents. The plan's shape is judged against the `plan-shape@1` rubric ([`plan-shape`](../plan-shape/SKILL.md)): record each of its criteria that failed as an `AMENDED` row.

Do not hand plan review off to a separate validator subagent: the main agent that researched the codebase and authored the plan holds the shared context needed to connect substrate observations, check invariants, and revise the plan in place without a lossy handoff.

## Step 0 — Check Existing `## Gate Amendments` Section (Run Once)

Before running the review, inspect the plan for an existing `## Gate Amendments (premise-gate + plan-review)` section:

- **Present with verdict `PASS` (and no unreviewed phases added since):** run Step 5's `eris gate check`
  for the plan's issue. `pass`: **stop**, note the recorded constraints and steering, and proceed to
  `/work implement` without running `/plan-review` again. `missing`: do not record; post the status
  line on the issue and stop. `gate check` cannot tell a record that never happened from a receipt
  that was removed, and a session that did not run the review cannot vouch for it, so the human or
  TPM records it. `drift` or `blocking`: the plan changed after its review, or failed it, so run
  Steps 1–5 again. Never answer `drift` by re-recording: that would receipt a plan nobody reviewed.
- **Absent or incomplete:** Run Steps 1–5 below in the main loop and amend the plan in place.

**Done when:** either an existing `PASS` section's constraints are loaded into context (and its receipt checks `pass`), or the plan is confirmed ready for its first review pass.

## Step 1 — Ground in Precedent, Library Currency & Checker Scope

1. Read the target repo's `.claude/rules/`, `thoughts/retros/`, and recent `thoughts/handoffs/` on the touched surface.
2. Locate the named sibling reference implementation in the codebase (`file:line`) for each new pattern in the plan, and verify the plan's code blocks match its conventions (`codebase-is-the-pattern-authority`).
3. For any newly introduced library, SDK major version, or external API choice, verify current idioms and deprecations via installed `.d.ts` / package definitions or a web search rather than training-cutoff memory. When the library is missing from the lockfile, released after the model's knowledge cutoff, or a major version above the installed one, judge its research with the `emerging-tech-research@1` rubric (load it): a missing cache or an unexecuted load-bearing API is `BLOCKING`.
4. Inspect the repo's checker configs (`pyproject.toml` type-checker and linter tables, `tsconfig.json`, `sgconfig.yml`, `eris.yaml`) and confirm every file the plan creates or edits sits inside their active scan globs.

**Done when:** every new pattern cites a live `file:line` sibling reference, any external library/API choice is verified against current definitions/docs, and every touched path is confirmed inside the active typecheck and lint globs (or a phase adds the path to the config).

## Step 2 — Audit the Six Design Invariants

Apply all six universal design invariants below to the plan. Each invariant is derived from a first-pass design flaw that previously escaped to adversarial review.

### 1. Class Closure & Type Monotonicity
- **Class closure:** When the plan fixes a bug or closes a gap, grep or AST-scan the repo for every sibling occurrence of the defect pattern (a column read by name in one path and by mapped attribute in another, `pk_cols[0]` on a composite primary key, a discarded dependency parameter) and include every hit in scope. Rewriting a path while leaving a broken sibling case in the same function or package is an incomplete plan.
- **Type monotonicity:** Every new or refactored signature preserves or narrows existing types (generic bounds, concrete models, discriminated unions). Replace any planned `Any`, untyped `dict`, or positional `tuple` return with a typed model or bound generic.
- **Zero touched-file diagnostics:** Verification criteria must run the typechecker and linter explicitly on the touched files (`tsc --noEmit`, the repo's Python type checker) with **0 diagnostics** — never "unchanged baseline diagnostic count".

### 2. Static Rung & Red-on-Main Proof
- **Highest rung first:** Every invariant over code syntax, call sites, or registration metadata (an unused auth dependency, inline column filters, a missing builder keyword argument) sits on the `arch`, `type`, or `lint` (`severity: error` `ast-grep`) rung in `## Invariants and Their Rung` — never a runtime boot check, `inspect` walk, or wrapper class around the owning choke point (`work-at-the-owning-layer`).
- **Red-on-main:** Every `lint` row records its rule ID, its `Escape Catalogue` (≥15 shapes, red-teamed before code), and its **observed red hit count on unfixed `main`** (or a mutation probe) before any fix phase runs.

### 3. Gate Delta-Invariance & Discriminator Cardinality
- **Delta-invariance:** When a plan specifies a gate, diff, reconciler, or matcher over `(Baseline B, Target T, Rendered/Live M)`, write a 3-way set-partition truth table proving that scope, kind, type, and exclusion filters apply only to untouched background (`B ∩ T`) and never suppress an authored delta (`(T \ B) ∪ (B \ T)`) or excuse unstated code output (`M \ T`).
- **Producer-consumer symmetry:** Snapshot/render producers and gate/diff consumers share identical endpoint predicates.
- **Discriminator cardinality:** Every field used as an exclusion or partition key (e.g. `derived_from`) carries a live value-distribution count (`GROUP BY field, family`) proving it uniquely discriminates the intended subset.

### 4. Post-Publish Idempotence & Remediation Round-Trip
- **Post-publish idempotence:** For any lint rule or diagnostic $P(S_{\text{local}}, S_{\text{remote}})$ that reads published/registry state, trace one publish of the bad state ($S'_{\text{remote}} = \text{ingest}(S_{\text{bad}})$) and verify $P(S_{\text{bad}}, S'_{\text{remote}})$ still fires on the second run rather than self-silencing.
- **Round-trip survival:** Trace the diagnostic's recommended fix ($S_{\text{bad}} \to S_{\text{advised}}$) through the downstream consumer (`ingest(S_{\text{advised}})`) and verify the authored fact survives rather than being dropped at ingest.

### 5. Transactional Preconditions & $k$-Step Interleavings
- **In-transaction precondition re-read:** Every guard whose precondition a concurrent mutation can invalidate (actor active/admin status, remaining admin count, resource state) re-reads that state *inside* the mutating transaction rather than trusting request or session context.
- **$k$-step transition disjointness:** For schedulers, leases, and state machines, trace multi-step sequences (`cancel → schedule → schedule` while running, repeat calls, a token lease during scheduled deletion). Lease and generation markers use out-of-band sentinels (`LEASED = -1` or a unique run token) so $k \ge 1$ intervening transitions cannot collide with the active run.
- **Mirrored-authority write paths:** For every row of the plan's `## Mirrored-field write paths` table (`plan-shape@1` criterion 8) that marks an authority field, confirm a phase builds its update and revoke paths, not only the insert, and that the refresh path's field set includes the authority. A refresh that rewrites `name` but not `role` is the defect.
- **Total claim & post-egress commit monotonicity:** Every path that mutates claimed rows — including backoff and await-only arms — acquires the claim first. Post-side-effect commits (`markProcessed`, `markDelivered`) guard only on `status = 'pending'`, never on volatile retry counters (`attempts`, `next_attempt_at`).

### 6. Loop-Invariant Hoisting & Oracle Budget
- **Hoist deterministic checks:** Every reference oracle, step-counter assertion, or structural equality check runs **once outside** any timing or `performance.now()` sampling loop; the loop body executes only the operation being timed.
- **Oracle budget:** When applying a test helper or oracle to a larger fixture or multiple pairs, state `calls_per_test × per_call_complexity` and measured `oracle_ms` in the plan, keeping `total_oracle_ms + total_sampling_ms` under 10% of the CI test timeout.

**Done when:** all six invariants have been evaluated against the plan, with a concrete finding or an explicit "clean / N/A (reason)" row for each.

## Step 3 — Run the Stack Surface Checklist

Read [`references/stack-checklists.md`](references/stack-checklists.md) and run it against the repo's stack. The repo's own contract outranks the generic list: read its `AGENTS.md` / `CLAUDE.md` and its root `eris.yaml` `ci.local` (when present) before you judge a plan's verification.

**Done when:** every item in the checklist is checked against the plan's files and schemas, and any repo-specific rule in `AGENTS.md` is checked too.

## Step 4 — Fold Amendments & Emit Verdict

Record the review table directly in the plan under `## Gate Amendments (premise-gate + plan-review)` and fold every required fix into the phase specs and `## Invariants and Their Rung` before implementation begins:

| Check | Status (`CLEAN` / `AMENDED` / `N/A`) | Plan change / steering note |
|---|---|---|
| 1. Class closure & type monotonicity | … | … |
| 2. Static rung & red-on-main proof | … | … |
| 3. Gate delta-invariance & cardinality | … | … |
| 4. Post-publish & remediation round-trip | … | … |
| 5. Transactions & $k$-step interleavings | … | … |
| 6. Loop-invariant oracle budget | … | … |
| 7. Stack checklist (`<stack>`) | … | … |

End the section with one verdict line, `**Verdict:** PASS` (zero unaddressed findings) or `**Verdict:** FAIL — <open findings>`. Step 0 and `/work implement` read this line.

The section is this skill's receipt. Write it only after loading this skill (`Skill` `plan-review`, the `/plan-review` command, or a read of this file by path): a plan whose `## Gate Amendments` came from a session that never loaded the gate is a table written from memory.

**Done when:** the table and the verdict line are written into the plan, every `AMENDED` item is reflected in the phases and success criteria, and the verdict is `PASS`.

## Step 5 — Record the Gate Receipt

The section above is the receipt inside the plan; this one is the receipt a loop can check.
`plan-review` is the **only** gate that binds `thoughts/shared/plans/<plan>.md` (`premise-gate`
and the SDK-check stage bind their own notes under `thoughts/shared/premise/` and
`thoughts/shared/sdk-check/`, so Step 4 appending `## Gate Amendments` never drifts an earlier
gate's receipt). After Step 4's last edit to the plan, **commit and push the amended plan as a
new commit** on the issue's draft PR branch (`eris gate record` refuses an uncommitted in-repo
artifact with `"commit and push first"`, and committing the amendment separately keeps the
initial plan commit and the reviewed plan commit distinct on the PR). Then record `plan-review`
from the repo root, linking both the commit-pinned blob (`blob/<sha>/<path>`) and the draft PR's
files view (`pull/<N>/files`). It binds the plan's sha256, so any later byte change, a ticked
checkbox included, reads as `drift`:

```bash
git add thoughts/shared/plans/<plan>.md
git commit -m "docs(plan): fold plan-review gate amendments (<KEY>)"
git push
SHA="$(git rev-parse HEAD)"
PR_URL="$(gh pr view --json url -q .url)"
REPO_SLUG="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
eris gate record plan-review --issue <KEY> --verdict <PASS|BLOCKING> \
  --artifact thoughts/shared/plans/<plan>.md \
  --rubric plan-shape@1 --doctrine <doctrine file> --impact <class> \
  --evidence "plan-shape@1 criteria 1-8 PASS; design invariants 1-7 PASS; blob: https://github.com/$REPO_SLUG/blob/$SHA/thoughts/shared/plans/<plan>.md; files: $PR_URL/files"
eris gate check --issue <KEY> --gates plan-review   # Step 0 and the loop: exit 0 on pass
```

On a **`linear-only`** run (no git repo diff), after Step 4 folds `## Gate Amendments` into
`$G/plan.md` (`G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"`), record `plan-review`
against `"$G/plan.md"` with no `git commit`, `git push`, or PR links (`eris gate record` stores
`{ _tag: "file" }` plus a gzip+base64 `artifact.copy` with the receipt, and `$G/plan.md` is
frozen thereafter):

```bash
G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"; mkdir -p "$G"
eris gate record plan-review --issue <KEY> --verdict <PASS|BLOCKING> \
  --artifact "$G/plan.md" \
  --rubric plan-shape@1 --doctrine <doctrine file> --impact <class> \
  --evidence "plan-shape@1 criteria 1-8 PASS; design invariants 1-7 PASS; scope: linear-only (stored plan copy)"
eris gate check --issue <KEY> --gates plan-review
```

- `--verdict` is `PASS` for `**Verdict:** PASS` and `BLOCKING` for `**Verdict:** FAIL`. A `BLOCKING`
  receipt is recorded too, and implementation does not start.
- `<KEY>` is the plan's issue (its title, filename or branch). With no issue, skip the
  receipt and say so in one line.
- Transport is the gateway's gate-receipt routes, signed in with `eris login` (run it once per
  machine). `eris gate --help` is the contract. Every failure to reach or sign in to the store
  exits 3 with one slug (`eris-login-required` means run `eris login`).
- If `record` fails, report its error line verbatim and go on without a receipt. Do not retry with
  another credential: the loop's `eris gate check` then fails closed, which is the point.
- Only the session that ran Steps 1–4 records. A later session that finds the receipt `missing`
  follows Step 0 and leaves the record to the human or TPM.

**Done when:** `record` printed the new comment id (or you wrote the skip line), and the plan has not been edited since.

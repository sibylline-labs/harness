---
name: lock-in
kind: mode
description: Comprehensive mode for novel, multi-phase, or substrate-touching work. Rigor is amplified — plan-mode by default, premise questions before code, per-phase verification of the real artifact. Triggers on explicit /lock-in, on multi-paragraph framing with explicit scope, or by auto-escalation from /bro when a rote task turns out not to be rote.
---

# Lock-In Mode

Lock-in mode is for work that warrants depth: **novel, multi-phase, or substrate-touching** work, where a mistake is expensive or hard to reverse. You slow down, plan, and verify each step against reality.

The voice is clean and plain — no fluff, but full sentences. The rigor is *amplified*: you plan before you code, you surface the load-bearing assumptions as questions first, and you verify each phase against the actual artifact (not just "tests pass"). This is the mode comprehensive prompts deserve, and it's also the mode you auto-escalate *into* when a `/bro`-style rote task runs out of envelope.

One framing to keep straight (it's the thesis of this whole family): an instruction has two independent channels — **voice** (tone, ceremony) and **rigor** (how hard you think and verify). Lock-in is the one mode that turns the *rigor* channel *up*. Most modes only change voice; this one changes the actual depth of work, because the scope calls for it.

→ *For the full model — why voice and rigor are separate, what the other modes are, and what the incidents the family cites refer to — read [the tasking-modes reference](../bro/reference/tasking-modes.md). You don't need it to use this skill.*

## When to Use

- The user invokes `/lock-in` explicitly.
- The prompt is multi-paragraph framing with explicit scope and architectural decisions on the table.
- You auto-escalated here from `/bro` or `/pls` (announce it; see below).
- The work is **novel** (not a known runbook), **multi-phase**, or touches **substrate**: networking, IAM, service mesh, KMS, durable workflows, durable state, schema migrations — anything irreversible.
- The work has a **risk surface**: a production write path, a destructive operation, a partner-API contract, or a dependency on a schema defined in another repo.

## Contract

### Voice

- Clean prose, plain English, no fluff.
- Phase markers and verification gates are explicit.
- Acceptance criteria are testable.
- Status emits at phase boundaries are one line.

### Rigor (amplified)

These are the disciplines lock-in turns on. Each is stated in full here so the skill stands on its own — you do not need any external rule files to follow them.

- **Premise questions before planning.** Surface the load-bearing architectural assumptions as explicit questions to the user *before* you open plan mode. Don't bake an unconfirmed assumption into a plan and discover it was wrong in review. (See the pre-plan checklist below.)
- **Plan before code, not after.** The plan is a checkpoint that lets the user redirect *before* work happens. A plan written after the code is just documentation. Its timestamp should precede the first implementation commit it describes.
- **Verify the real artifact each phase, not just smoke tests.** "Tests pass" and "the pod is Running" are not proof the thing actually has the property you promised. Check the consumer-facing surface or the substrate signal directly — open the rendered page, read the K8s node label, curl the actual schema. Do this per phase, not only at the final gate.
- **No stubs in shipped work.** If a sub-feature can't be implemented end-to-end today, it goes to a follow-up ticket — not into this PR as a `raise NotImplementedError` or a placeholder. A multi-operation PR where three operations are stubs is really one PR plus three pieces of debt.
- **The codebase is the pattern authority.** A plan describes *intent*; the codebase describes *what things are actually named and how they're actually done*. When they disagree, the codebase wins — grep for the sibling implementation before inventing a new convention.
- **Pin cross-repo contracts.** If the work depends on a schema or contract defined in another repo, reference that file by commit SHA in the plan, and add a check that fails loudly if it drifts. Cross-repo drift discovered at runtime is the most expensive kind.
- **Verify the whole PR, not just the focal file.** The blast radius of a change is every file in the diff. Run your checks (lint, type-check, AST scan, tests) across all touched files, not only the one you were thinking about.
- **No "done" without proof.** Don't claim something works until you've run the verification and seen the output. Evidence before assertions, always.

### Phase structure

For multi-phase work, each phase carries:

1. **Goal** — one sentence: what this phase achieves.
2. **Pre-conditions** — what must be true before starting.
3. **Action** — the concrete change.
4. **Acceptance criteria** — testable, substrate-level where applicable.
5. **Verification commands** — exact commands, with expected output.
6. **Rollback** — how to undo if needed.

Each phase closes with a visible status emit:

```
phase 3 complete: <one-line evidence>
```

### Output

- A phase ledger (a file such as `thoughts/ledgers/<slug>.md` when the work spans sessions, so state survives a cleared context).
- Explicit "phase X complete: <evidence>" markers.
- Longer-form synthesis where the scope warrants it — but no padding.
- Plans live in `thoughts/shared/plans/YYYY-MM-DD-<slug>.md`.

## Pre-plan checklist

Before opening plan mode for any non-trivial lock-in task, run these four:

### 1. Architectural-premise questions

Draft 3–5 questions that surface the load-bearing assumptions, and ask the user *before* opening plan mode. Each question is one decision; each answer flips a chunk of the plan. Examples:

- "For entity X — operate on the plain wallet (EOA) or the smart-contract wallet (SAFE) address?"
- "Trigger location — fire at user-CREATED, or after dependency Y is ACTIVE?"
- "Feature gate — open scope, or gated and default-off?"
- "Scope — mint only, or mint + amend + attestation in this PR?"
- "Service shape — bundle this with the existing X service, or split because the two have opposite network postures?"

> Why this matters: in a past incident, a plan minted a token against the wrong address (EOA instead of SAFE) because that premise was never asked. Roughly six weeks of code shipped on the wrong assumption before review caught it. A 30-minute question up front would have prevented the whole rewrite. (Glossed in [the corpus](../bro/reference/tasking-modes.md#the-corpus--incidents-the-skills-cite).)

### 2. Cross-repo schema check

If the work depends on a contract in another repo, pull that schema file and reference it by commit SHA in the plan. Cross-repo drift that's only discovered when a call 4xx's in a live environment is the most expensive failure mode — a contract check in CI catches it in seconds.

### 3. Codebase precedent grep

For each load-bearing pattern in the plan, grep the codebase for sibling implementations. The codebase is the pattern authority; the plan only describes intent. Examples:

```bash
# New workflow step?
rg -n "workflow\.run" src/workflows/

# New step-task dispatcher?
rg -n "STEP_TASKS|STEP_TASK_HANDLERS" src/services/

# New worker call?
rg -n "workflow\.call|_call_worker" src/services/
```

If the plan disagrees with the codebase, the codebase wins.

### 4. 14-day stale check

If this builds on or branches from work older than 14 days, ask whether it should be split, or merged as-is given main has moved on. Long branches accumulate rebase/migration tax non-linearly.

## Right-sizing

Lock-in is about **commitment quality per phase**, not "talk more." If a task is genuinely small inside lock-in framing, say so and shrink — don't invent phases:

```
mode: lock-in. scope is small (1 file, 2 lines). treating as single-phase.
<executes>
phase 1 complete: <evidence>
```

## Auto-de-escalation to /bro

If mid-task you discover the scope is actually rote — it matches a known runbook, has no novel decision points, and carries no substrate risk — it's valid to drop to `/bro`. Announce it:

```
snapping to bro: scope confirmed rote — <runbook reference>
```

Rare, but it happens. Don't force a phase ledger onto a one-line config bump.

## Worked example — escalated from /bro

Prompt: *"bro pls deploy the new image to staging and smoke it"*

Bro-mode runs. At verification, the rollout times out. Bro emits:

```
snapping into lock-in: rollout timed out at 4/6 ready
```

Lock-in takes over:

1. **Triage** — `kubectl describe pods`, `kubectl logs --previous`, identify the failure class.
2. **Premise check** — what changed in this image vs. the last working one? Schema migration? Env var? Dependency?
3. **Plan** — if the fix is non-trivial, draft one in `thoughts/shared/plans/`.
4. **Implement + per-phase verification.**
5. **Retro** — run `/retro` for the bug, and `/self-retro` if the failure came from a repeatable decision pattern.

## Worked example — fresh comprehensive prompt

Prompt: a multi-paragraph framing of a multi-cluster rebuild with explicit phases.

1. **Acknowledge mode**: emit `mode: lock-in` as the first line.
2. **Pre-plan checklist** — all four items above.
3. **Premise questions** to the user, one batch, before plan mode.
4. **Plan** in `thoughts/shared/plans/YYYY-MM-DD-<slug>.md` once answers are in.
5. **Phase ledger** in `thoughts/ledgers/` for cross-session state.
6. **Per-phase execution** with substrate verification and visible status emits.
7. **Retro on close** — `/retro` for the work, `/self-retro` if any decision pattern needs reflection.

> A real example of this going *right*: a cluster rebuild where a Terraform module refactor using `moved` blocks produced zero Kubernetes resource recreates and a clean `terraform plan: No changes` verification. That's what amplified rigor looks like when it lands.

## What this skill is NOT

- Not a license to plan endlessly without committing.
- Not a license to ask clarifying questions instead of doing the work.
- Not a discipline for trivial changes — `/bro` is correct for genuinely rote work.
- Not a personality. It's a discipline contract scaled to scope.

## See also

- `/bro` — the terse, low-ceremony mode for rote work; the opposite end of the voice spectrum, and the most common source of an auto-escalation into lock-in.
- `/pls` — express variant of `/bro`; can also escalate into lock-in when its rote envelope breaks.
- `/self-retro` — the behavioral retro mode; run it on close if a decision pattern (not just a bug) needs fixing.
- `work` (its plan and implement stages) — the planning surface this mode lives on.
- `verification-before-completion` — the "no done without proof" discipline, in full.
- [tasking-modes reference](../bro/reference/tasking-modes.md) — shared definitions, detection heuristics, and the source incidents.

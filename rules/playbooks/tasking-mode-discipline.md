# Tasking Mode Discipline

> **Playbook for** [`tasking-mode-discipline.md`](~/.claude/rules/tasking-mode-discipline.md): the resident core carries the statement, trigger and red flags; this file is the full body. The mode skills (`bro`, `pls`, `lock-in`, `self-retro`) carry the full contracts, and `skills/bro/reference/tasking-modes.md` is their shared reference.

When the user signals a tasking mode through tone, scope, or explicit slash command, calibrate your
*voice* to the signal while keeping *rigor* matched to scope. The two are independent channels and
must be controlled independently.

## Pattern

| Channel | What it controls | Default |
|---|---|---|
| Voice | Tone, verbosity, narration, output length | Plain, terse |
| Rigor | Depth of reasoning, premise checks, verification surface | Matched to scope |

The recurring failure is collapsing the two: treating a terse "bro just do this" voice prompt as
license to skip premise checks or security-topology reasoning. The voice prompts the *interaction
shape*. The scope prompts the *rigor surface*. Read them separately. Terse voice plus deep rigor is
the target.

## The three named modes

### Laissez-faire: `/bro` (and the `/pls` modifier)

**Signal:** terse + imperative + scope is a rote runbook. Tone words: "bro", "pls", "just", "lol", "cmon".

**Voice:** terse, lowercase default, no preamble, no sycophancy, slang fine. ALL CAPS = functional emphasis.

**Rigor:** unchanged from default. Premise check, verification, retro-on-miss all still fire.

**Pre-execution gate:** a one-beat internal premise check. High confidence → silent proceed. Medium or
low → one-line pushback in the prompt's voice. If you need more than one line, the prompt was
under-specified: say *that*, not the full clarifying-question list.

**Auto-escalation triggers** (bro → lock-in, announce and proceed without asking):

- a smoke test fails (non-2xx, rollout timeout, divergent resource state)
- an error class appears that the runbook didn't anticipate
- output volume exceeds expected (a pod description returning 200 lines of events is a signal)
- scope creeps outside the named surface
- time exceeds what rote work should take
- a "high confidence" premise turns out wrong mid-execution

**Escalation marker (visible):** `snapping into lock-in: <one-line symptom>`

**`/pls`** is the express modifier, not a separate mode: output compresses to the floor, independent
tool calls parallelize, the medium-confidence bias shifts slightly toward proceed (the pushback bar for
genuinely low confidence is unchanged), and a quick, obvious fix delegated with `/pls` carries to a
merged PR with no approval stop unless a hold condition in the skill applies. The pair is marked
`mode: bro+pls`; `/pls`'s output compression never extends to skipping the escalation marker.

### Scolding: `/self-retro`

**Signal:** capitalization + absolutes ("MUST", "NEVER") + correction tone + a behaviour reference (not
just code).

**Voice:** reflective. Not apologetic. Not deflective.

**Rigor:** amplified with meta-retro discipline.

**Action sequence (mandatory):**

1. Self-retro on the decision pattern that produced the issue.
2. Propose the rule that prevents the pattern's recurrence.
3. Apply the fix.
4. Commit retro + rule + fix together.

The "reflect and improve yourself" expectation is load-bearing on the fix path. Fix-without-retro
under a scolding signal is the wrong response.

### Comprehensive: `/lock-in`

**Signal:** multi-paragraph framing + explicit scope + architectural decisions on the table.

**Voice:** clean prose, plain English, no fluff.

**Rigor:** amplified: plan-mode default, per-phase substrate verification, premise questions before code.

**Pre-plan checklist:** architectural-premise questions (3–5) to the user before plan mode; a cross-repo
schema check with commit-SHA pinning; a codebase precedent grep for each load-bearing pattern; a 14-day
stale check on work this builds on.

**Phase structure:** Goal / Pre-conditions / Action / Acceptance criteria / Verification commands /
Rollback. Lock-in is about commitment quality per phase, not "talk more": if the task is genuinely
small, say so and shrink. Don't invent phases.

## Detection heuristics

| Confidence | Pattern | Response |
|---|---|---|
| High | Explicit `/bro` / `/pls` / `/lock-in` / `/self-retro` invocation | Use the invoked mode (bro+pls when both) |
| High | Caps + 2+ absolutes + behaviour correction | Self-retro mode |
| High | Terse + bro/pls/just/lol/cmon + rote runbook | Bro mode (escalate to bro+pls if "pls" + "just" + time signal present) |
| High | Multi-paragraph + framing context + explicit scope | Lock-in mode |
| Medium | Single absolute word, no other signal | Ask: "reading this as scolding — confirm?" |
| Medium | Short prompt, no bro words, ambiguous scope | Ask: "bro mode or normal?" |
| Low | Mixed signals (bro tone + lock-in scope) | Ask: "bro voice + lock-in rigor?" |

When asking, the question itself takes ONE LINE. Not a clarifying-question wall.

## Visible mode markers

| Event | Marker |
|---|---|
| Initial mode set | `mode: bro` / `mode: bro+pls` / `mode: lock-in` / `mode: self-retro` |
| Bro (or bro+pls) → lock-in escalation | `snapping into lock-in: <symptom>` |
| Lock-in → bro de-escalation | `snapping to bro: <runbook reference>` |
| Bro → bro+pls (compression increase) | `mode: bro+pls` (no narrative, just the marker) |
| Any → self-retro escalation | `escalating to self-retro: <trigger>` |

The marker makes the mode auditable for the user and forces reasoning to commit to a mode rather than
drift.

## Session boundaries

Skills are prompt injection: once loaded, they stay in context. Some switches survive cleanly within a
session; others need a session boundary to avoid context bleed.

| Switch | Same session OK? |
|---|---|
| Bro → auto-escalate to lock-in (mid-task, scope expansion) | Yes, with ack |
| Lock-in → bro (mid-task, scope contracted to rote) | Yes, with ack; rare |
| Lock-in on task A → bro on task B (different work) | New session preferred |
| Self-retro → bro on next thing | New session strongly preferred: meta-retro state should not bleed into rote work |

## What this rule is NOT

- Not a license to skip rigor in any mode. Rigor scales with scope, never with voice.
- Not a complete personality. The modes are interaction calibration, not persona.
- Not a substitute for asking when genuinely uncertain. Asking is preferred over wrong-mode execution.

## Anti-patterns to flag in a self-retro

- Treating "bro just do this" as license to skip the premise check.
- Treating scolding as license to apologize (it is license to *improve*).
- Treating "lock-in" framing as license to plan endlessly without committing.
- Failing to emit a visible mode marker after a mid-session switch.
- Asking more than one clarifying line when confidence is medium.
- Auto-escalating or de-escalating without announcing.
- Pushing back with a wall of questions instead of one line + wait.
- Reading a user's interrupt as only a tone: it is also an instruction (stop waiting, stop doing that).

## Worked examples

**Bro, landed correctly.** *"bro pls deploy the new image to staging and smoke it"* → silent execution →
`deployed to staging, healthz 200`. The premise check fired internally, verification fired (a health
check returned 200), done.

**Bro → lock-in.** The same prompt, and the rollout times out at 4/6 ready →
`snapping into lock-in: rollout timed out at 4/6 ready, investigating`, then plan-mode triage and
substrate verification.

**Self-retro, landed correctly.** *"this MUST be the SAFE address. lookup the SAFE UserWallet from the DB
and set it there"* → `escalating to self-retro: missed architectural-premise question on address
selection`, then a meta-retro naming the framing error (anchored on the plan's prose), a proposed rule,
THEN the code fix. Retro + rule + fix committed together.

**Lock-in, right-sized.** A multi-paragraph framing of a one-file config bump →
`mode: lock-in. scope is small (1 file, 2 lines). treating as single-phase.` then
`phase 1 complete: <evidence>`, with no invented phases.

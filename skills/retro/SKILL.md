---
name: retro
kind: workflow
description: Issue-anchored retrospective — trace a divergence (bug, incident, slog, descope, drift discovered late) to its true root cause through Linear and git evidence. Use after a hard debugging episode, when an issue fought back, before merging hard-won fixes, or when asked "how did we get here".
---

# Retro

"How did we get here, and what did we learn?" A retro anchors on a Linear issue, assembles the evidence trail, traces the causal chain to the true root cause, and routes each learning to the one home where it will be found again.

A retro is earned by **divergence** — the actual path departed from the expected one. Bugs and incidents, but equally slogs, descopes, scope churn, review-cycle burns, drift discovered late. Routine clean work doesn't retro.

Linear is the source of truth for internal facts. When code, a ledger, or memory disagrees with the issue trail, trust the trail — and note the disagreement; it is usually itself a rung in the chain.

## Step 1 — Resolve the anchor

The anchor is a Linear issue:

- **Explicit**: `/retro ABC-123`.
- **Implicit**: resolve from the current branch/PR — branch name (Linear's branch convention embeds the identifier), PR body, issue attachments.

No issue found → say so and offer a degraded git-only retro; proceed only on confirmation. Anchor already closed → **post-hoc mode**: same process, PR-bound outputs skipped in Step 5.

**Done when:** the anchor is stated along with the mode (pre-merge / post-hoc / degraded).

## Step 2 — Assemble the evidence (pass 1)

Collect inline — this pass is small. Calls and what to pull from each surface: [`references/traversal.md`](references/traversal.md).

- The anchor issue: description, every comment, state history.
- Direct relations: parent, blocking/blocked, related, duplicates.
- The project's **Load-Bearing Decisions** and **Key Assumptions** docs — which decisions and assumptions led to this issue or constrained it. (Read them; this is not a rollup pass.)
- Git/PR: branch commits, review threads, diff shape.
- Session artifacts: `thoughts/` ledgers and plans, prior retros naming the same surface.

Interleave it all into a **dated timeline**: decision points, the first divergence, the discovery moment.

**Done when:** the timeline exists and the first divergence point is identified with its evidence.

## Step 3 — Trace the causal chain

The core artifact. Walk from symptom down through three altitudes:

| Altitude | The rung asks | Yields |
|---|---|---|
| **Surface** | what in the code/config broke? | gotchas, patterns, fixes |
| **Behavioural** | what process or decision habit let it happen? | SOPs, controls, skill/rule changes |
| **Structural** | what strategy or architecture made that habit natural? | strategic flags |

Rules of the chain:

- Every rung cites **observed** evidence — a comment, commit, doc line, LBD — never inference: a premise is observed, not inferred. A rung without evidence is a pass-2 signal, not licence to guess.
- The chain **bottoms out** at a structural cause, or stops explicitly: "chain ends here because X".

**Pass-2 signals** — dispatch `research-agent` subagents, one per evidence stream ([`references/dispatch.md`](references/dispatch.md)), when:

- a rung lacks evidence or the chain won't bottom out
- the chain contradicts a Load-Bearing Decision or Key Assumption
- the same pattern appears in prior retros or sibling issues (recurrence)
- comments show scope churn whose origin is upstream of the anchor

State which pass ran and why.

**Done when:** every rung carries evidence, and the chain bottoms out or carries an explicit stop.

## Step 4 — Derive learnings and opportunities

Attach learnings to rungs. Every altitude gets at least a considered "nothing here":

- **Harness & workflow improvements** — hooks, automation, CI gates that would have caught this mechanically. Draft as Linear issue proposals.
- **SOPs & behavioural changes** — controls the team buys into: skill edits, rules, design-process or scoping changes. Draft as Linear issue proposals.
- **/self-retro** — if a behavioural rung implicates agent behaviour in this session, name the decision pattern and offer to run `/self-retro` now.
- **Strategic flags** — highlight, never solution: fundamental strategy problems, long-horizon footguns and mounting tech debt, load-bearing structures (code or process) faltering under load. Labeled flags for human and team-pass attention.

## Step 5 — Write the outputs

1. **Retro doc** — `thoughts/retros/YYYY-MM-DD-<slug>.md` per [`references/template.md`](references/template.md).
2. **Linear comment on the anchor issue** — distilled: chain summary, learnings, flags, proposal list. Scan the draft for operational metadata that is as sensitive as a key (storage paths, secret variable names, "real X credentials" phrasings) before posting.
3. **Inline GOTCHA comments** — wherever the fix's "why" is non-obvious: `# GOTCHA: <why>. See: thoughts/retros/<file>`. Post-hoc mode: list as suggestions in the retro doc instead.
4. **PR comment** — a pointer only: root-cause one-liner plus links to the Linear comment and retro doc. No duplicated body.
5. **Issue proposals** — present the harness/SOP drafts; file via `/linear-workflow` only on accept. Never silently create trackers. These proposals (filed issues + doc `- [ ]` items) are the queue the team actions next: a retro *drafts* opportunities, a later pass *implements* them. When the queue is non-empty, close with a passive pointer ("logged N opportunities") and let the user drive.
6. **CLAUDE.md** — repo-local code gotchas only, terse, in *Gotchas & Patterns*. Behavioural learnings reach rules via `/self-retro`; generalizable findings reach living docs via `eris socrates classify` then `eris socrates submit`. One durable home per learning.

## Checklist

- [ ] Anchor + mode stated
- [ ] Timeline with first divergence point
- [ ] Chain: evidence on every rung; bottomed out or explicit stop
- [ ] Every altitude considered for learnings
- [ ] `## Opportunities` section present in the doc, even when every row is an explicit "nothing here" — a learning written as prose with no checkbox and no issue is a deferral with no destination, which is the failure retros most often document and most often repeat
- [ ] Retro doc written; Linear comment posted (secret-scanned)
- [ ] GOTCHA comments added (or listed as suggestions, post-hoc)
- [ ] PR pointer comment (pre-merge mode)
- [ ] Proposals presented; filed only on accept
- [ ] /self-retro offered if agent behaviour implicated

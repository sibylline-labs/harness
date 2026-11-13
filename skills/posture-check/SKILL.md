---
name: posture-check
kind: gate
description: >-
  Per-PR surface-conformance gate: validates a diff touching a registered
  tier-1 surface (auth, secrets, CORS, webhooks) against cumulative surface
  state using named pattern classes. Deterministic-first, bounded 3-line
  output, fail-closed on unregistered surfaces.
---

# /posture-check — per-PR surface-conformance gate

When a change touches a **tier-1 surface** (auth, secrets, CORS, webhooks, API mounting,
feature gates), this skill answers one question:

> Does this diff introduce a new instance of a known pattern class on this
> surface, or combine with existing components to produce a new failure
> scenario?

Not *does the diff do what it claims* (`verification-before-completion`); not *is the whole
surface broken* (a full audit of the surface). The cumulative-state-aware middle tier: **read the
diff against the current state of the surface, with the surface's named pattern classes as the
lens.** Calibration: a past auth audit returned dozens of findings, each locally defensible at
the moment it was introduced (an empty-string secret default, credentials allowed beside a
wildcard origin, a feature gate that fails open) — the cumulative **posture** is what's broken,
not any individual PR. Diff-shaped review cannot see that; this skill grades the diff against the
surface.

## Run modes

| Mode | Invocation | Behaviour |
|---|---|---|
| **Manual (touch)** | `/posture-check` | The flow below, on the current diff against `main`. |
| **Manual (sweep)** | `/posture-check <surface>` | Sweep the named surface against its full current state — ast-grep rules + the vocabulary's `Shape:` lines; no fan-out, no subagents. |
| **Dry-run** | `--dry-run` on either manual mode | Print which files matched which surface and which classes would run; emit no findings. |
| **Auto-fire** | a repo-wired hook (optional) | A repo that wants a nudge can wire a prompt-submit hook that, when session changes touch a registered surface, injects a ≤3-line suggestion to run this skill: once per surface per session, never blocking. This skill ships no hook. |

## The contract — three load-bearing properties

1. **Bounded output.** ≤3 lines per surface. More than 3 distinct findings → top one +
   *"+N more — run `/posture-check <surface>` for the full sweep"*. Exact shapes:
   [`references/output-format.md`](references/output-format.md). A finding that needs an operator
   decision also goes out as a blocking ask (step 7); its id rides line 1, so the cap holds.
2. **Deterministic-first.** Most checks are ast-grep rules; LLM judgment only for classes the
   vocabulary flags LLM-required. Write the rule first; promote to LLM only when the shape is
   syntactically impossible to express. Rules + escalation:
   [`references/class-checks-deterministic-vs-llm.md`](references/class-checks-deterministic-vs-llm.md).
3. **Fail-closed on unknown surface.** When a run asserted to be surface-relevant matches no
   registered surface, emit the tag-or-out-of-scope line — never a silent pass. The explicit,
   auditable opt-out is `posture-check: oos` in the PR description.

Two hard corollaries: the skill is **read-only** (no vocabulary writes, no Socrates-doc writes, no
tracker issues — it emits text, plus the one blocking ask of step 7; humans act on it), and it
holds a **cost ceiling** of roughly a few cents and ~30 seconds per run — past it, emit
*"budget exceeded — escalate to a full surface audit"* and stop. A surface that keeps exceeding
the budget is too big for per-PR gating; the answer is the full sweep, not a bigger budget.

## The flow

1. **Identify the diff.** `git diff --name-only main...HEAD`, or the PR's changed-files list.
   Done when you hold the changed-file list.

2. **Match files to surfaces.** The registry is `.claude/surfaces.yml` in the consuming repo
   ([`references/surface-registry-format.md`](references/surface-registry-format.md)). Match each
   changed file against every surface's `paths` globs; a file may match several surfaces, and is
   gated by all of them. Then:
   - **No `.claude/surfaces.yml` is not rot.** The repo never registered a surface, so the result
     is n/a. Print nothing else and record `posture: n/a (no surfaces.yml)` in the final-gates
     evidence line. Step 6 still runs.
   - **A registry that does not parse or breaks the schema** is registry rot: surface the parse
     error verbatim and stop.
   - **No surfaces matched, none asserted** → exit silently. Most changes land here; the skill is
     not a tax on unrelated work.
   - **No surfaces matched but the run asserted one** (a surface argument, or the user framed the
     change as touching a tier-1 surface) → emit the fail-closed line (property 3) and stop.
   - **One or more matched** → continue, per surface.

3. **Load the class taxonomy.** Per touched surface: the skill-shipped classes in
   [`references/class-checks-deterministic-vs-llm.md`](references/class-checks-deterministic-vs-llm.md)
   plus the repo-local vocabulary at the registry's `class_taxonomy` path (default
   `thoughts/vocabulary/<surface>.md`). Missing vocabulary → shipped classes only, plus one
   warning line naming the missing file.

4. **Run deterministic checks.** Apply each ast-grep rule for the surface's deterministic classes
   over the diff. Distinguish:
   - **New instance** — the rule matches an *added* line.
   - **Combined instance** — an added component plus pre-existing surface state produces the
     scenario (e.g. a new `allow_credentials=True` in a file where `allow_origins=["*"]` already
     lives).

   On every tier-1 surface, also run the skill-shipped class `authority-mirrored-at-insert-only`
   (entry and LLM residue in the class-checks reference). Done when every deterministic class for
   the surface has fired or cleared.

5. **Escalate residual LLM-required classes.** One focused subagent per class, answering a single
   yes/no pair — new instance? combines with existing state? — with `file:line` evidence. Soft cap
   5 LLM classes per surface (top 5 by severity; the rest defer to the full sweep); no retries.
   Dispatch prompt: in the class-checks reference.

6. **Pair with the governance gate.** Independently of surface matching, if the diff touches a
   governance site the repo lints (a config key, a settings field, a call reaching another service,
   an `eris.yaml`), run the repo's governance lint in the same pass. Different question (does this
   diff pay what its site owes?), same per-PR moment, same bounded contract. The overlap is real: a
   settings diff can trip both gates, and the surface registry is not what decides the governance
   obligation, so a repo with no `surfaces.yml` still owes it.

7. **Emit the bounded output** per [`references/output-format.md`](references/output-format.md).
   Severity is read from the vocabulary's `Typical severity` — never assigned here. Silence is the
   correct output for a clean diff.

   **Ask the operator, blocking.** A top finding of severity `⚠` or `ⓘ` on a PR is a decision, not
   a remark: a medium question left as prose in a hand-back rides the Done transition unread. File
   one blocking ask, with the issue from the branch or PR title and the PR from
   `gh pr view --json number -q .number`:

   ```bash
   eris ask "posture-check (<surface>): <class-id> — <class-name> at <file:line>. Fix before merge, or accept as intended?" \
     --issue <KEY> --pr <N> --blocking --recommend fix \
     --option fix="Fix before merge" \
     --option accept="Accept as intended and record a Load-Bearing Decision"
   ```

   Append ` · ask <id>` (the id `eris ask` prints) to line 1 of the finding; that is the finding's
   receipt, and the final-gates receipt quotes it. A low finding, the fail-closed line, the budget
   line and any run with no PR (a sweep) send no ask. If `eris ask` fails, keep the finding as prose
   and say "ask not filed" with the stderr. Never retry a create: run `eris ask list --issue <KEY>`
   before asking again. This skill never waits on the ask; gates and merges block on an open
   blocking ask.

## After a fire

- **Real regression** → fix before merge; the class entry's `Why it kills` names the stakes.
- **A fire on a tier-1 surface is never a question.** Report it as a finding to fix, or file the
  issue and link it from the receipt or hand-back. "Should X…?" as a prose question in the hand-back
  gives the finding no owner.
- **Intentional** (a deliberate surface-policy change) → record a Load-Bearing Decision so the next
  PR doesn't re-flag it: `eris socrates classify --title <t> --statement <s> --source <url>` (local,
  sends nothing), then `eris socrates submit --title <t> --statement <s> --source <url> --evidence <one line: why, then repo@sha:path#L or a PR link>`.
- **The same un-named class keeps firing** → the vocabulary is missing a class; add an entry to the
  surface's vocabulary file (format in the class-checks reference), then the next run checks it.

---
name: verification-before-completion
kind: gate
description: Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
---

# Verification Before Completion

## Overview

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Rubrics This Gate Judges

Before the claim, load each rubric that applies and grade the diff with its enum verdict
(`PASS` / `AMENDED` / `BLOCKING`). A `BLOCKING` is a failed verification.

| Rubric | Applies when | Over |
|---|---|---|
| `unit-test-admission@1` | the diff adds a test | each new test and its `admits:` comment |
| `user-impact@1` | always | the stated U0–U3 class and its evidence |
| `improvement@1` | the change is sold as a refactor, cleanup or improvement | the stated LOC or complexity measure |

The plan the change implements was judged earlier by `plan-review` against `plan-shape@1`, and
any research it leaned on by `emerging-tech-research@1`; this gate does not re-judge them, but a
plan with no `**Verdict:** PASS` fails the "Plan was gated" row below.

## The Strongest Form: a Fresh Adversarial Gate

Same-session self-verification is contaminated — the agent that wrote the code inherits its own rationalizations. The strongest gate runs in a **fresh context** (the `verify-adversarial` agent, ideally a separate session) that re-derives PASS/FAIL from evidence alone.

Two non-negotiables that same-session verification routinely skips:
- **CI must actually run green** — not "tests should pass", not a partial local run. Run the full CI gate and read the exit code. If CI is genuinely unavailable, run the standard local equivalent and say so explicitly; an unrun gate is not a passed gate.
- **Separate pre-existing from introduced failures** — stash to a clean baseline, run, and diff, so a red result is attributed to your change, not inherited noise.

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| New tests are worth keeping | Each new test's `admits:` comment names the failure mode it protects; red→green observed this session | Green count, coverage delta, "N tests added" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |
| Plan was gated | The plan's `## Gate Amendments` section ends `**Verdict:** PASS`, written in a session that loaded `/plan-review` | A gate table written from memory, "reviewed the plan" |
| Code meets standards | Diff walked against the repo's own conventions doc (`AGENTS.md`, `.claude/rules/`) | Linter passing |
| UI looks correct | Screenshot or visual verification | "I updated the CSS" |
| UI PR ready | Screenshots attached where the team reviews (the issue or PR, per repo convention) | Screenshots taken locally, "verified visually" |
| Component renders | Browser confirms rendering | File was created/edited |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler ≠ runtime |
| "Agent said success" | Verify independently |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |
| "The code looks right" | Looking ≠ running |
| "Build passed so it works" | Build ≠ runtime behavior |
| "The tools are green so the code is good" | Tools ≠ standards conformance |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Lint rules (rule first):**
```
✅ Write rule → Run on unfixed code (MUST FAIL, N hits) → Fix → Run (pass)
❌ "I've added a lint rule" (never seen catching the real code)
```

**Regression tests (Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

**UI/UX changes:**
```
✅ Drive the affected route in a browser → Capture evidence → Confirm it matches intent
❌ "I updated the component" / "The styles should be correct"
```

## Why This Matters

From failure after failure:
- "I don't believe you" - trust broken
- Undefined functions shipped - would crash
- Missing requirements shipped - incomplete features
- Time wasted on false completion → redirect → rework

---

## Verification by Workstream

Green tools prove the code **runs**. They do not prove it **conforms**: a passing linter says
nothing about magic strings, god modules or a missing field on a response. Every workstream
demands both: the tool gate *and* a walk of the diff against the standards that govern it. Find
the repo's gate before you run anything: read `AGENTS.md` / `CLAUDE.md` and the CI workflow, and
run what CI runs, not what the package manager could run.

### Backend / library / CLI

- **Tools, all of them, not a subset.** The full test suite (not only the changed tests); the
  linter and formatter check over every changed file; the type checker over every changed file; the
  repo's structural scan (`ast-grep scan`) over every changed file. Re-run the scan after the
  formatter, because formatting can shift a suppression comment off its match line.
- **Conformance walk.** Load the repo's conventions doc and walk every changed hunk against it:
  magic strings, parameter drilling, raw dicts where a typed model belongs, god modules, a response
  missing a field its consumers read. The completion criterion is **every changed hunk accounted
  for**: each one either conforms or is fixed. A file you skimmed is a file you did not verify.
- **Warning-severity rules block nothing by themselves.** A scan that prints warnings and exits 0
  does not gate; you are the gate, so fix every hit the scan prints.
- **A CLI or a script is verified by running it**, with its real flags, against a real input, and
  reading its exit code and its stderr. A unit test over the argv builder cannot see an invalid flag.

### Frontend

- **Tools:** lint, type check and production build, then the structural scan over changed files.
- **Conformance walk** against the repo's UI conventions: state consolidation, global versus local
  state, re-entrant guards, empty and loading states. A green build says nothing about any of them.
- **Browser:** a component that compiles is not a component that renders. Drive the affected route in
  a real browser (a headless driver such as `agent-browser`, in an isolated session you close
  before finishing), at a phone width as well as desktop, and read the console. Browser verification
  is NOT optional for new components or pages, layout or styling changes, responsive work, animation
  or interaction changes, or anything the user will see.
- **Evidence:** attach screenshots of every new or changed screen where the team reviews (the issue
  or PR, per repo convention), captured after animations settle, in flow order, each captioned with
  the commit it was taken at and whether it was reached for real or with stubbed API responses. If a
  state couldn't be reached, name it rather than leaving it out.

### Large diffs

Past roughly 10 changed files or 500 changed lines, self-review degrades into skimming: you
already know what you meant, so you read intent rather than text. Dispatch a subagent to review the
diff independently against the repo's conventions, split by directory when one agent cannot read it
all. **Independently** is the load-bearing word: give it the diff and the standards, never your
conclusion, your rationale, or a list of the parts you think are fine. A reviewer told where to look
reproduces your blind spot. Then verify their `file:line` claims against the code before you repeat
them. A read-only agent (`verify-adversarial`) has no `Agent` tool and cannot dispatch; it runs the
same review itself, one directory at a time, reading each changed file in full before judging it.

### Cross-Cutting

```bash
# Verify scope = ALL PR-touched files
git diff --name-only main...HEAD
```

**Verification scope = ALL PR-touched files, not just the focal module.**

This matches what CI will run. If you skip any of these, the PR will fail in CI and produce yet another `fix(lint)` commit.

Before pushing to remote, whichever workstream(s) you ran:

- [ ] Every command of the repo's gate run over the whole change, 0 failures, 0 new diagnostics
- [ ] Every changed hunk walked against the repo's conventions
- [ ] No plan files, agent output, or `.claude/plans/` accidentally staged

---

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, PR creation, task completion
- Moving to next task
- Delegating to agents

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion/correctness

## The Bottom Line

**No shortcuts for verification.**

Run the command. Read the output. THEN claim the result.

This is non-negotiable.

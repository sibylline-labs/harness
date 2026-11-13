---
name: test-driven-development
kind: workflow
description: Lint-driven development, rule before test. Use when implementing any feature or bugfix, fixing a defect or enforcing a convention, before writing implementation code, when writing or reviewing tests, or when deciding whether a test earns its place at all.
---

# Lint-Driven Development

A correction is fixed at the lowest layer that can hold it, in this order:

1. **Architecture**: make the mistake unrepresentable.
2. **Types**: make the type checker reject it.
3. **Lint**: a built-in rule (ruff `banned-api`, biome) before a custom ast-grep rule.
4. **Behaviour test**: only for behaviour no rule can express.
5. **Docs and agent rules**: last, for what no mechanism can hold.

**Rule before test.** A rule guards the whole class of mistake, everywhere, at no runtime cost. A test pins one instance, and too often it just restates the implementation. Whichever artifact you pick, it is written first and seen **red** on real code before the fix.

## Rule-first: when the defect or convention has a structural signature

A structural signature is anything a parser or type checker can see: a banned import, a forbidden call, a missing decorator, a wrong exception class, an unchecked `None`.

1. **Observe the premise by executing it.** Reading the source is inference. Run the code and show the behaviour you are about to rule on.
2. **Write the rule.** Use the highest rung that holds it: a type, then a built-in lint rule, then ast-grep. Its message names the fix and a provenance pointer.
3. **Run it on the unfixed tree and see it fail.** The hit count is the real scope of the work. Triage every hit as fix, scoped ignore with a reason, or rule too broad.
4. **Fix the code until the rule passes.**
5. **The rule ships with its own cases.** ast-grep rules carry `ast-grep test` cases, valid and invalid, drawn from the real mistake. Built-in rules ship with the probe that showed each banned alias resolves.

Completion criterion: the rule is wired into the repo's CI gate, it was red in this session's output with N hits, every hit is triaged, and it is now green.

Worked example, rule red at 52 hits against the ticket's guess of 5: [worked-example-rule-first.md](worked-example-rule-first.md).

## Behaviour tests: for behaviour no rule can express

Retry and replay branches, money movement, idempotency and state machines are behaviour. A rule cannot assert that a retry ran. These get a test, and the test still goes red first.

### The value gate

Before writing any test, complete this sentence:

> **When {production failure mode}, this test goes red — observed at {seam}.**

- The completed sentence becomes the test's `admits:` comment, directly above the test or its decorators (`# admits:` / `// admits:`), followed by why no cheaper rung holds it. The final gate grades it with `unit-test-admission@1`, and ast-grep warns on a new test that lacks one.
- The failure mode must be a *behavior* going wrong, not "someone edited this constant".
- If a type, schema, lint rule or existing test already catches the failure, the sentence fails. Write the rule instead, or nothing.
- If you can't tell whether the value is real (a wire contract? a compliance string?), ask in one line.

You write tests at near-zero marginal cost; the team maintains every one at full cost. The metric is **confidence per maintenance minute**. The catalog of what earns a test and what never does: [what-earns-a-test.md](what-earns-a-test.md).

### Tautology tests

A **tautology test** passes by construction, so it protects nothing and bakes in stale or wrong logic. It takes two forms:

- **It restates the implementation**: the expected value is computed the way the code computes it, or the assertion pins an assignment.
- **It mocks the very thing under question**: the mock supplies the behaviour the test claims to check. In one real case, nine tests mocked the database context to raise SQLAlchemy's `IntegrityError` while the real call raised the data-layer wrapper's own class. They stayed green over twelve handlers that could never run.

A behaviour test whose oracle comes from the code under test, or whose mock decides the outcome, is deleted or rewritten. Never extend it.

### Seams

A **seam** is the public boundary where behavior is observable from outside: the API route, the service method callers use, the persisted state read back through the interface, the emitted event. Tests live at seams, never against internals, private attributes or call topology. Agree the seams before the first test: confirm them with the user, or list them in the plan or PR description.

Mocking doctrine, covering what to fake, what to leave real and how to keep mocks honest: [mocking-and-seams.md](mocking-and-seams.md). Read it before creating any mock.

### The loop

Work in **vertical slices**: one test, one minimal implementation, repeat. Each test is a **tracer bullet** that responds to what the last cycle taught you.

**RED**: write one test at the seam, run it, and read the failure. It must *fail*, not error, for the reason the docstring states. If it passes immediately, it tests behaviour that already exists, so fix it or delete it.

**GREEN**: write the minimum that passes. Run the test and its neighbours; read the output.

**Refactor** after green, keeping green.

**Bug fix** is the same loop seeded with a repro, after asking whether a rule can hold the class instead. A test that existed before the fix and passes against the broken code is a tautology: revert the fix and watch the test go red to prove it is not one.

### Mutation check: red on break, as one command

To prove a kept rule or test can fail, break the code it guards and watch the gate go red. `scripts/mutate.py` does this, so don't hand-roll an apply-run-restore loop. It runs the gate unmutated first and refuses if that is already red. Then, for each mutant, it applies one exact-string edit, runs the gate, and reports `KILLED` (the gate went red, with the failing test lines) or `SURVIVED`. It restores the file byte-identical, mtime included, every time, including after Ctrl-C. Each mutant gets its own mtime, so a `.pyc` or transform cache cannot hand a mutant the original code. A `SIGKILL` leaves a `<file>.mutate-orig` sidecar, which blocks the next run until `restore` puts the file back.

```bash
M="$HOME/.claude/skills/test-driven-development/scripts/mutate.py"
uv run --script "$M" run --file hooks/x.py --replace 'if not ok:' --with 'if False:' -- uv run pytest -q tests/test_x.py
uv run --script "$M" run --mutants data/scratch/mutants.json   # [{"id","file","replace","with","cmd"?}], or {"cmd": [...], "mutants": [...]}
uv run --script "$M" restore                                   # after a crash
```

Exit 0 means every mutant was killed, 1 means one survived, 2 means an error. Paste the report as the red-on-break evidence. A survivor means the gate does not guard that line: strengthen the gate, or name the survivor and why you accept it.

### Oracles

Every test asserts an outcome observable at its seam: a return value, a state change read back through the interface, or a raised error (`pytest.raises`, not a bare "does not throw"). Expected values come from an independent source of truth, such as a spec, a worked example or a known-good literal.

Assert on a collaborator call only when the call *is* the contract: money moved, event published, an irreversible provider action, exactly-once semantics. Everything else asserts the resulting state.

### Consolidation duty

The suite is a budget you spend, not a ledger you append to. Read a surface's existing tests before adding one:

- The same invariant across many values → one parameterised table.
- A new scenario that subsumes older narrow tests → delete them in the same change.
- A test a new rule now guards → delete it in the same change.

Deleting a test that no longer earns its place ranks equal to writing one.

## Done

Run the detectors in [review-heuristics.md](review-heuristics.md) over the test diff. Done when:

- every structural defect or convention in the change is held by a rule that was red then green in this session's output;
- every new test's docstring completes the value-gate sentence and went red then green;
- no test in the diff is a tautology, and the detector pass is clean.

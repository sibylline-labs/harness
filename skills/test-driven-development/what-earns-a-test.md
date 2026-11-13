# What Earns a Test — and What Never Does

Load when the value-gate sentence feels forced, when testing configuration/models/enums, or when reviewing a test diff.

The question is always the same: **what production failure does this detect, and is this the cheapest thing that detects it?**

## Earns a test

| Surface | Why it earns one | Shape |
|---|---|---|
| Domain logic with branches | The branch can be wrong | Unit test at the service seam, worked-example oracle |
| Money movement, authorization, identity | Failure is expensive and irreversible | Behavioural scenario + narrowly-scoped call assertion (the call is the contract) |
| Wire contracts (API shapes, enum wire values, provider payloads) | External consumers break silently | One parameterised contract table per public schema |
| Persistence invariants (constraints, round-trips, soft delete) | ORM/DB coercion is silent | Round-trip through a real DB seam, every field asserted |
| Regressions | The bug happened; it can happen again | Repro test named for the bug, red on symptom first |
| Safety/compliance-approved copy | The wording is legally or safety load-bearing | Snapshot/requirement-ID test, one per requirement — not per phrase |
| Idempotency / exactly-once | Retry semantics are invisible until they fail | Scenario invoking twice, asserting single effect |

## Never earns a test (the mirror catalog)

Each of these restates the code — its only red condition is "someone edited the assignment." A test-suite audit found over a thousand of them in one codebase; every row below is drawn from that corpus.

| Mirror | Example | What actually guards it |
|---|---|---|
| Config scalar pin | `assert _MAX_RETRIES == 3` | The assignment itself; policy manifest if it's an operational contract |
| Private attribute pin | `assert agent._output_type is ChatOut` | It's private — no consumer, no contract |
| Enum member count | `assert len(AccountType) == 10` | Nothing — adding a valid member *should not* fail a test; pin wire *values* in a contract table if external |
| Factory default restatement | `assert create_user().status == "active"` | Tests the factory, not the model; the factory's own single test |
| Literal docstring/prose pin | `assert "retries three times" in tool.description` | Snapshot test only if the wording is a wire/safety contract |
| Callable-exists check | `assert callable(migration.upgrade)` | Import succeeding; one loader sanity test for all migrations |
| Schema restatement | asserting a Pydantic field's type/default | The type checker and the schema declaration |
| Tautology | `expected = sum(i.price for i in items)` then asserting the sum | Nothing — it passes by construction; use a known literal |
| Mock decides the outcome | the mock raises the exception the handler catches, but the real collaborator raises another class | A rule on the structural signature (a ruff `banned-api` entry for the wrong exception class), or a fake that behaves like the real seam |

When an operational value (a rate limit, a model name) genuinely must be change-reviewed, the mechanism is **one** typed manifest validated by **one** parameterised test — or a snapshot diff in a policy lane — never one test function per scalar.

## Doesn't need a test, needs a different lane

- **Architecture rules** (forbidden import, required decorator, "never wrap `workflow.run()` in try"): a named ast-grep/lint rule with positive+negative fixtures — fails with a violation location, runs in seconds, no app import. Not a pytest function walking the AST.
- **"Does the whole app boot"**: one smoke test owns this; individual tests that import the world to assert one scalar are paying its cost without its coverage.

## The implementation-without-test case

Some changes are legitimately shipped with no new test: pure config wiring already exercised by an existing seam test, a rename fully covered by the type checker, docs/copy outside any contract. Say so explicitly in the PR ("no new tests: covered by X / no behavioural surface") rather than adding a mirror to look diligent. A named absence beats decorative presence.

---
name: unit-test-admission
kind: rubric
description: Rubric unit-test-admission@1 for whether a new test earns its place. Each new test carries an `admits:` comment naming the failure mode it pins and why no cheaper rung holds it. Use when adding a test or judging the tests a diff adds.
---

# unit-test-admission@1

**Producer:** `impl-*` agents and `test-driven-development`, for every test they add.
**Judge:** `verification-before-completion` (final gates), over the tests the diff adds.

## The comment

Each new test has an `admits:` comment directly above it, or above its decorators. The
comment names the failure mode the test pins and why a cheaper rung (type, lint, schema)
can't hold it. A lint rule can read it and warn on a new test that has none; keep that rule
to lines the branch added, so old tests are not a tax.

```python
# admits: the lint must fail red when a rubric loses its judge; nothing else runs it in CI.
def test_rubric_without_judge_fails(tmp_path): ...
```

```ts
// admits: a 504 from the deploy tool is retried, not reported as a token fault; no type sees the status.
test("retries a 504", async () => { ... });
```

## Verdicts

- **PASS**: every new test has a specific `admits:` comment, and none is a tautology.
- **AMENDED**: comments are missing or vague (`admits: tests the function`), but every test
  is load-bearing. The judge lists the tests and the comments are fixed forward. AMENDED
  passes `eris gate check`.
- **BLOCKING**, while it is still in the diff:
  - a tautology: it asserts its own setup, or mocks the unit under test;
  - a test for a two-way-door fix with no regression history;
  - a test whose `admits:` names a failure that a type, lint or schema already holds.

## Examples

- PASS: `# admits: CRLF frontmatter must still parse; git autocrlf checkouts produce it.`
- AMENDED: a load-bearing parser test with no comment. The judge lists it and moves on.
- BLOCKING: a test builds a dict, then asserts the dict has the keys it was built with.
- BLOCKING: `# admits: the return type is str`. The type checker already holds that, so delete the test.

---
paths:
  - "**/test_*.py"
  - "**/*_test.py"
  - "**/tests/**"
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.spec.ts"
  - "**/__tests__/**"
---

# Tests Should Not Lock In Bugs

When writing a test that "verifies existing behavior", ask first: *is this behavior correct?* If the answer is no or unclear, the test is freezing a bug in place, and anyone proposing a fix will have to delete the test first, making "is this a bug at all?" the wrong starting question.

## Pattern

Tests describe a specification, not a moment in time. An assertion like `assert json["created_at"] == "2021-01-01T00:00:00+00:00"` looks like it's verifying behavior, but if the "correct" value for `created_at` is the integer `1609459200000`, the test is actively defending the bug.

Before writing a regression or snapshot test, ask:
- Would I write this same assertion from first principles, without looking at the current output?
- Does this assertion describe what the code *should* do, or only what it *currently* does?
- If I found this test in review, would I flag the assertion as weird?

If any of those raise a flag, the test is locking in behavior that should be examined, not asserted.

## DO

```python
# Tests what the contract promises.
restored = Model.model_validate_json(original.model_dump_json())
assert restored.created_at == original.created_at       # round-trip fidelity
assert isinstance(restored.created_at, int)             # type is part of the contract
```

## DON'T

```python
# Locks in a lossy JSON encoder. If ISO conversion is a bug, this test
# defends it. A fix must delete this test first, which looks like a regression.
def test_backward_compatibility_maintained(self):
    user = SampleUser(id=1, name="Compatible User", created_at=1609459200000)
    json_result = user.model_dump_json(indent=2)
    assert '"created_at": "2021-01-01T00:00:00+00:00"' in json_result
```

## When This Applies

- Snapshot tests where the snapshot was generated from current output without review
- Regression tests written *after* a bug report, asserting the current (buggy) output
- "Backward compatibility" tests that enshrine the existing shape without asking whether the existing shape is correct
- Any test whose assertion the author can't justify from specification alone
- A test created in the **same commit** as the behaviour it asserts: nothing marks it as a description rather than a decision
- A test that pins a *mutation* (a dedup, a sort, a coercion, a truncation) applied to a value that crosses a signature, hash, or wire contract

## Red Flags

- Test name contains "backward compat" or "existing behavior" but doesn't link to a spec / ADR / issue explaining *why* that behavior is correct.
- Assertion is a literal copy of current output, not a value derived from specification.
- During debugging, you find a test that asserts the wrong thing and realize it was written to pass, not to describe the contract.
- The test was born in the same commit as the code it tests, and you are treating its existence as evidence the behaviour was decided. A named, passing test is the most persuasive thing in a file; it is not a rationale.
- A sibling field, row, or endpoint documents the *opposite* guarantee in prose, and a test pins only the one that contradicts it.
- Tooling has flagged the test as low-value more than once. Value detectors score usefulness, not correctness: two hits on the right line for the wrong reason is still two hits.

## Source shapes

- A serialization test asserted the lossy ISO-string output of a JSON encoder. That conversion later caused a production 500 in a strict-typed consumer, and the fix required deleting the assertion. The test should have asserted the integer contract from the start.
- A validator that deduplicated a signed list, and a test pinning the dedup as intent, were added in one commit. The test sat unchallenged for months, was flagged low-value twice, and was the one test in thousands that broke when the dedup was finally removed. Usefulness and correctness are different questions, and a value detector asks only the first.

Companions: `unit-test-admission@1` (an `admits:` comment names the failure a test pins, which is the question this rule asks first), and `six-month-maintenance-test` (a test that cannot fail, or defends a defect, costs upkeep and buys no confidence).

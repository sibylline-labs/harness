---
name: user-impact
kind: rubric
description: Rubric user-impact@1, the U0–U3 user-impact class of a change and the evidence each class requires. Use when proposing or judging a change's impact class in a handoff, a PR or a gate receipt (`--impact`).
---

# user-impact@1

**Producer:** the implementing loop or `impl-*` agent proposes a class in its handoff.
**Judge:** `verification-before-completion` (final gates). The class is recorded as `--impact`.

The hard floor is no downtime and no customer losses. No doctrine, override or door rung
lowers it.

| Class | Meaning | Required evidence |
|---|---|---|
| U0 | internal only: tooling, build, docs, and internals no external entry point reaches | none beyond the gate profile |
| U1 | user-visible, reversible | a proven revert path: the revert command run, or a flag flip shown |
| U2 | availability risk | U1, a proven zero-downtime shape, and `e2e` evidence |
| U3 | irreversible user loss | U2 and a rehearsed rollback |

This table is the floor. The active doctrine posture can raise a class with `policy.user_impact`
(never lower it): a stricter posture requires `e2e` for U1 too. `eris gate check` enforces the
union, and `eris doctrine gates` prints it as `@user-impact` rows.

The producer proposes the class, with one line on what reaches the change (the external entry
points that can run the changed code).

## Verdicts

- **PASS**: a class is stated with a one-line reachability reason, and its evidence is present.
- **AMENDED**: a class is stated, but the reason is thin. The judge restates it.
- **BLOCKING**:
  - no class is stated;
  - a U2 or U3 proposal was lowered without a human receipt;
  - the class's required evidence is missing.

## Examples

- PASS: "U0: changes `skills/` lint only; no external entry point reaches it."
- PASS: "U1: new `/v1/orders` field behind flag `order_eta`; flag-off shown in dev."
- AMENDED: "U0: internal." The judge restates it as "U0: build hook; runs only in local sessions."
- BLOCKING: "U0" on a change to a public API route.
- BLOCKING: "U2" lowered to "U1" in a later commit, with no human receipt.

---
name: improvement
kind: rubric
description: Rubric improvement@1 for whether a change sold as an improvement makes the code leaner. Net LOC falls or a measured complexity metric falls, with no feature and no syntactic sugar. Use when writing or judging a refactor, cleanup or improvement-loop change.
---

# improvement@1

**Producer:** the `impl-*` agent implementing an improvement issue (the `close` workflow's
improvement-loop stage).
**Judge:** `verification-before-completion` (final gates), over the diff.

An improvement is measured, not asserted. State the measure in the handoff: net LOC from
`git diff --shortstat <base>`, or a named complexity metric before and after (cyclomatic
complexity, function count, dependency count, branches in a hot function).

## Verdicts

- **PASS**: net LOC falls, or a measured complexity metric falls, and the diff adds no
  feature, no public surface and no syntactic sugar.
- **AMENDED**: it is leaner, but mixes in a behaviour change. Split the behaviour change
  into its own PR.
- **BLOCKING**:
  - it adds surface (a new flag, option, abstraction or public function);
  - it is a rename or reformat sold as an improvement;
  - no measure is stated.

## Examples

- PASS: "−142 LOC: three hand-rolled retry loops collapse onto the existing `with_retry`."
- PASS: "`resolve_groups` cyclomatic complexity 14 → 6; behaviour pinned by the existing tests."
- AMENDED: "−60 LOC, and the error message now includes the path": split the message change out.
- BLOCKING: "+80 LOC: a `Strategy` base class so the next caller is easier": that's a feature.
- BLOCKING: walrus operators and comprehensions swapped in, with no measure and no fewer branches.

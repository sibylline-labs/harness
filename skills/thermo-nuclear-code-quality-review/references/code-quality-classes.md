# Code-Quality Classes — the `code-quality` surface vocabulary

The default vocabulary of a review report (`surface: code-quality`) when the repo registers no surface in
`.claude/surfaces.yml`. Each class is one of the Non-Negotiable Additional Standards in
[`../SKILL.md`](../SKILL.md) (`Q1` = standard 0 … `Q8` = standard 7), in the per-class format of the
`posture-check` vocabulary (see its `class-checks-deterministic-vs-llm.md`). The prose rubric stays in
SKILL.md; this file gives each standard the class ID a finding's `class` and the report's `classes_checked`
carry.

`review_report.py` reads the IDs from the `## Class <ID> — ` headings: adding a class is a heading here, and
an addition-only change to the class checklist is a tighten.

## Class Q1 — Missed code-judo simplification

**Shape:** the change keeps whole branches, modes, helpers or layers that a reframing of the change would delete.
**Why it kills:** incidental complexity becomes permanent; every later change pays for concepts that never needed to exist.
**Typical severity:** major; blocking when the simpler path is plain and the PR preserves a lot of complexity.

## Class Q2 — File pushed past 1000 lines

**Shape:** a file under 1000 lines before the diff is over 1000 after it.
**Why it kills:** large files stop being readable as a unit; decomposition gets harder each change.
**Typical severity:** blocking unless the author gives a compelling structural reason.

## Class Q3 — Spaghetti branching in an existing flow

**Shape:** new ad-hoc conditionals, special cases, one-off booleans or nullable modes inserted into an unrelated or already busy path.
**Why it kills:** each branch multiplies the states a reader must hold; feature checks scatter across shared code.
**Typical severity:** blocking when it tangles an existing flow; major otherwise.

## Class Q4 — Working but messier design accepted

**Shape:** behavior is right, but the structure is worse than a visible cleaner version with the same behavior; refactors that move complexity without deleting it.
**Why it kills:** "it works" approvals ratchet the codebase toward mess.
**Typical severity:** major.

## Class Q5 — Hacky, magic or thin abstraction

**Shape:** generic mechanisms hiding a simple data shape; identity wrappers; pass-through helpers; brittle "magic" behavior.
**Why it kills:** indirection without clarity; readers must reverse-engineer what a direct flow would state.
**Typical severity:** major when it makes the design more indirect; minor for a single thin wrapper.

## Class Q6 — Muddy type or boundary contract

**Shape:** unnecessary optionality, `any`/`unknown`, casts, loosely shaped ad-hoc objects, or a silent fallback papering over an unclear invariant.
**Why it kills:** the real invariant is invisible to the checker, so violations surface at run time.
**Typical severity:** major; minor for an isolated cast.

## Class Q7 — Logic in the wrong layer or a duplicated helper

**Shape:** feature logic leaking into shared paths, implementation details leaking through an API, or a bespoke helper where a canonical one exists.
**Why it kills:** architectural drift; two copies of one concept diverge.
**Typical severity:** blocking when a clear canonical home exists; major otherwise.

## Class Q8 — Needless sequencing or non-atomic update

**Shape:** independent work serialized for no reason, or related updates that can leave state half-applied.
**Why it kills:** brittle orchestration and partial states that are hard to reason about and recover from.
**Typical severity:** major when partial state is reachable; minor for sequencing alone.

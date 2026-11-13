# Ask What the Check Could Not See

> **Playbook for** [`ask-what-the-check-could-not-see.md`](~/.claude/rules/ask-what-the-check-could-not-see.md): the resident core carries the statement, trigger and red flags; this file is the full body.

Sharpens two parents at once, because the mechanism is one:
[`premise-observed-not-inferred.md`](~/.claude/rules/premise-observed-not-inferred.md) governs whether a
**named** premise was observed; `verification-before-completion` governs whether a claim has **any**
evidence. Both fire correctly and still leave this gap: a check's own frame is not self-certifying. Run
this immediately *after* either one.

**A discipline's output is evidence about what was inside its frame. It is never evidence that the
frame was the right size.** After running a premise table, a verification, a scan, or any
coverage-producing check, spend one beat naming what it could not have seen.

## Pattern

Rituals that produce coverage (a premise table, a green test run, a lint pass, an audit checklist)
hand you an artifact: seven observed premises, `27/27`, zero findings. The artifact is legible,
countable and satisfying, and it silently answers a question you did not ask: *was this the complete
set?*

The failure is not laziness. It is the opposite: the more thorough the check, the more its output feels
like proof of completeness. Seven observations that each changed the design is strong evidence the
*exercise* is working, and no evidence at all about the eighth premise that was never written down. A
discipline can only act on what enters it, so an enumeration hole is invisible to every downstream
guard, including the ones designed to catch exactly this class.

Two frames account for most real cases, and both sit at a boundary the author naturally enumerates
*outward from and stops at*:

1. **The other operand.** When the deliverable compares, joins, reconciles, syncs, diffs, migrates, or
   dedups, the author enumerates premises for the side being *authored* and takes the other side as
   given. Two identity spaces that never meet produce **plausible rows, never an error**, which is why
   nothing downstream catches it.
2. **The instrument.** A test count, a benchmark, a probe result is a fact about instrument-plus-subject.
   When the subject branches on a property of the instrument's environment (host capability, installed
   binary, network reachability, locale, clock), the number is a property of that environment and
   reporting it bare is a wrong claim.

## DO

- **After a premise table is written, read it back and ask what is missing**, not whether each entry is
  observed. "What is this feature comparing, joining, or syncing?" If the answer is anything, the table
  needs one **identity premise per operand** before it needs sources, shapes, or ownership.
  ```bash
  # Comparison feature: observe BOTH id spaces before writing either leg.
  # Mine reads the merged doc → one row per leaf.
  # What does the thing I'm diffing against read?
  rg -n 'merged_doc' src/lint/        # my leg: the merged doc, one row per leaf
  rg -n 'declaring' src/publish/      # their leg: raw per-doc keys, one id per DECLARING doc
  ```
- **Ship a verification number with its configuration** whenever the code under test branches on an
  environment property. `27/27` → `27/27 on darwin, no GNU timeout on PATH`. If you can't name the
  properties, that is the finding.
- **Ask what a green result depended on** before reporting it: which binaries were present, which branch
  of a capability check ran, which fixtures existed. A branch like
  `if command -v timeout; then … else … fi` in the path under test is a standing instruction to measure
  both sides.
- **Prefer a check whose frame is stated in its output.** A runner that prints its host capabilities
  makes every future `N/N` self-describing at near-zero permanent cost.

## DON'T

- Treat "every entry in the table is observed" as "the table is complete." Those are different claims
  and only the first was checked.
- Enumerate a comparison's premises from the side you are building and take the other operand as given,
  even when it is your own code, in your own repo, documented in a file you already cited.
- Report a count, duration, or pass rate as a property of the code when it is a property of the code
  *on this machine*.
- Read a document for the one question you brought to it. The sentence that answers "who owns this?"
  often also answers "what does it emit?": ask both while it is open.
- Derive the test corpus solely from the design. Fixtures written from the same mental model can only
  confirm that model in higher resolution; at least one fixture must exercise the shape that
  *distinguishes* the two things being compared.

## Red Flags

- The deliverable is a diff / reconcile / sync / migrate / dedup and the premise list contains no
  premise about the other side's identity.
- Your premise table has N entries and you cannot say how you knew N was enough.
- A capability branch (`command -v`, `if [[ -x ]]`, a try/except import, a feature-detect) exists
  anywhere in the path under test, and you measured one side of it.
- You are about to report a number without being able to state, in one clause, what environment
  produced it.
- Every fixture in the suite has the same structural shape as the example in the design doc.
- The thoroughness of the check is doing the work of arguing it was complete.

## The surfaces

| Surface | The sentence applied there |
|---|---|
| checking a human's qualitative claim | the metric you chose is a frame; state the operationalisation before the verdict, and put the proxy on trial when it disagrees with direct experience |
| rendered artifacts with a design source | a screenshot checked against itself with fixtures confirms the builder's model; tick every element the contract names, and render the real record, fetched live |
| risk registers for metered services | consumption is the frame a failure-mode register cannot see; one multiplication per meter before shipping |
| handing over a deliverable whose evidence has a named gap | static gates all read source, so runtime sits outside every one of them at once; run the thing, or hand it over labelled *unverified*: naming the gap does not close it |
| shared infra (hooks, templates, shared CLIs) | a home-repo green cannot see the callers it does not own; exercise one real consumer from a foreign repo, worktree or subagent before close |
| round-trip tests (serialize, cache, persist) | the assertions are the frame; an unasserted field's coercion passes green, so assert every field that crossed the trip |
| reporting an absence ("no longer", "nothing qualified", "no hits") | an empty result describes the search's frame; run a positive control and name the frame in the claim |
| detached CLI launches | a spy asserting `spawn(buildArgv())` is a closed loop that cannot see invalid flags or missing session targets; probe every branch against the real binary and run a live smoke check before close |
| interactive TUI/UI views | a single-frame snapshot cannot see boxes swapping order on a key press, clamped cursors, or filters hiding rows; walk the live interaction loop before close |

## Source shape

One review caught two defects with one mechanism. **(1)** A plan observed seven premises, every one
about the leg being authored and none about the identity function of the operand being diffed against.
The code leg read a merged document (one row per leaf for an inherited key); the push it compared
against read raw per-document keys and minted one id per *declaring* document. The two id spaces could
not meet on an inherited key: a "key unregistered" count read 360 on the live estate and all 360 were
false. The answer was in a sentence the plan itself cited, read for a different question, and the unit
tests were all single-service, so the corpus inherited the design's blind spot. **(2)** `27/27` was
reported as verification, but one script exec'd through GNU `timeout`, which walks past a shell-function
stub; the machine had no `timeout`, so the in-shell fallback ran. With coreutils on PATH, the same file
was 23/27.

## Not the same as

[`close-the-blast-radius.md`](~/.claude/rules/close-the-blast-radius.md) enumerates the sites a
*change* affects; this rule enumerates what a *check* could not see. Opposite direction, same
discipline of counting before declaring done. [`six-month-maintenance-test.md`](~/.claude/rules/six-month-maintenance-test.md)
is the reason the fix here is one printed banner, not a bespoke lint per stub.

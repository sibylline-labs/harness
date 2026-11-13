# The Six-Month Maintenance Test

> **Playbook for** [`six-month-maintenance-test.md`](~/.claude/rules/six-month-maintenance-test.md): the resident core carries the statement, trigger and red flags; this file is the full body.

Every artifact you produce (a test, an abstraction, a config knob, a doc, a helper) is not output, it
is **inventory the team looks after**. Before producing one, ask: **"is this really worth the effort
of looking after in six months' time?"** The work that matters is not the code shipped today; it is
what today's code adds to (or subtracts from) the long-term maintenance load.

## Pattern

Agents produce artifacts at near-zero marginal cost, so volume always *feels* like diligence: more
tests, more validation, more docs, more speculative flexibility. But every artifact carries a
permanent maintenance liability (it must stay green, stay current, stay understood), and that cost is
paid by the team forever, not by the author once. The operative disciplines:

- **Quality over quantity.** One behavioural test at a stable seam outranks ten mirrors of the
  implementation. One paragraph that will stay true outranks a page that rots.
- **YAGNI.** Build for the requirement in front of you, not the imagined one. Speculative parameters,
  "just in case" branches, and defensive artifacts nobody asked for fail the six-month test on arrival.
- **The metric is confidence (or capability) per maintenance minute**, never count of artifacts
  produced.

This is a lens on *how to execute the process*, not licence to skip it. Instructions, skills and
checklists **are the authority**: they are the process the team wants followed. When following
guidance faithfully still produces artifacts that fail the six-month test, that is a signal the
*guidance* needs changing: raise it to the owner (one line), and fix the instruction at its source so
the whole corpus improves. Neither silent deviation nor months of silent mass-production is
acceptable; escalation through the human is.

## DO

- Before creating an artifact, run the six-month test: who consumes this, what failure does it catch
  or capability does it add, and is that worth its upkeep? Put the answer where reviewers can see it
  (a test's `admits:` comment, a PR's "why" line).
- Prefer consolidation over accretion: fold the new case into the existing table, helper or doc;
  delete what the new thing subsumes, in the same change.
- When a checklist or skill drives artifact production and the artifacts are failing the six-month
  test, flag the guidance to its owner immediately. The Nth artifact is not more diligent than the
  first flag.
- Ship named absences: "no new tests, covered by X" or "no abstraction, one call site" beats
  decorative presence.

## DON'T

- Equate volume with diligence, or green count with completion evidence.
- Add speculative flexibility (parameters, branches, hooks) for requirements that don't exist yet.
- Keep producing an artifact class you privately doubt. Doubt is escalation fuel, not something to
  swallow.
- Treat this lens as permission to skip process steps. The process is the authority; this test
  governs what the process's steps *produce*.

## Red Flags

- You can't name the consumer or failure mode of the thing you're about to create.
- The justification is "the checklist says so" with no six-month answer behind it.
- You're on the Nth near-identical artifact this session and haven't asked whether the class is worth
  it.
- A "just in case" or "might need it later" appears in your reasoning.

## Companions

[`dont-read-churn-as-rot.md`](~/.claude/rules/dont-read-churn-as-rot.md) is the inverse: don't tear
down what earns its keep. [`tests-should-not-lock-in-bugs.md`](~/.claude/rules/tests-should-not-lock-in-bugs.md)
covers tests that cost upkeep and defend a defect.

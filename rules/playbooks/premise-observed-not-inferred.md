# Premise Observed, Not Inferred

> **Playbook for** [`premise-observed-not-inferred.md`](~/.claude/rules/premise-observed-not-inferred.md): the resident core carries the statement, trigger and red flags; this file is the full body.

**A load-bearing premise must be observed, not inferred.**

## Pattern

Every piece of work stands on a few premises that decide its shape: the trust boundary two
operations share, a dependency's readiness, what the consumer actually sees, how each artifact class
is stored, the architectural target a plan is built on. Each surface makes inferring the premise feel
locally safe: the plan says so, the sibling does it that way, the higher-layer signal is green, the
tool presents one surface so the backends must match. So each surface produces its own incident, and
the family grows without the pattern ever being named.

The economics are constant across every surface: the direct observation costs seconds to minutes (a
probe, a question, opening the artifact), while the inferred-wrong premise costs a review cycle, a
descope, or weeks of silent drift. A premise is load-bearing exactly when its falsity would
restructure the work, and at that threshold the observation is never optional polish.

## The surfaces

| Surface | The sentence applied there |
|---|---|
| service topology / trust boundaries | "these operations share a security posture" is examined per operation, not inferred from code locality |
| PR scoping | "this sub-feature is implementable" is observed end-to-end today, not projected onto an undeployed dependency; a stub in a shipped PR is a premise nobody observed |
| phase verification | the rendered artifact or substrate is opened and checked, not vouched for by green higher-layer signals |
| plan mode | the plan's architectural premise is confirmed with the user and the codebase before code exists |
| migrations | each artifact class's storage model is probed separately, not assumed shared because one tool fronts both |
| canon (ledgers, PRDs, named constants) | a substrate claim cites the observation that grounds it, not a spec, sibling or design doc |
| delegation boundaries | assert only what you observed; everything else crosses as a question with a demonstration requirement, and everything returning is checked against its artifact, not its summary |
| resuming a session whose agents died | the work a dead agent's transcript narrates is reconciled against disk before anything builds on it |
| a report's reasons | a causal justification is checked by running its counterfactual; green gates cannot see it |
| reporting a state change | the action you took is an intent until the tool's receipt or the counterparty's hand-back confirms it; quote it, or say attempted / proposed |
| issue state at the start of work | the issue is fetched live, comments and parent included, before planning and at every hand-back; a paste is a snapshot of the description, not the issue |

Reach for the meta-pattern directly when no surface fits the one in front of you.

## Applying it on a new surface

1. Name the premises the work stands on: anything whose falsity would restructure the work, not
   just re-parameterize it.
2. For each, ask: have I *observed* this, or inferred it from a document, a green signal, a sibling,
   or a habit?
3. Find the cheapest direct observation (probe the system, open the artifact, run the one-line
   authoritative check, ask the person who owns the decision) and run it *before* building on the
   premise. **When the premise is about runtime behaviour, reading the source is still inference;
   executing it is the observation.** Source is authoritative about what is written and silent about
   what happens: a dependency's interceptor ordering, what a value holds at a given point, whether a
   body can still be read. The cheapest observation there is a twenty-line script, not a careful read
   of the right file.
4. Record what was observed, so the next reader inherits an observation instead of re-inheriting the
   inference.

## Red Flags — class level

- "should be", "presumably", "the plan says", "it'll be ready by then", attached to something whose
  falsity restructures the work.
- Confidence sourced from a document or a green higher-layer signal rather than from the substrate
  itself.
- A verification list that exercises everything *around* the premise but never the premise.
- You cannot name the single observation that would falsify the premise, which means you haven't
  looked for it.

## Sibling

[`diagnose-from-observation-not-prior.md`](~/.claude/rules/diagnose-from-observation-not-prior.md)
governs the causal hypothesis a diagnosis starts from; this rule governs the premises work is
*built* on. Same invariant, opposite directions.

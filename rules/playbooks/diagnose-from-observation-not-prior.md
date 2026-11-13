# Diagnose From Observation, Not the Prior

> **Playbook for** [`diagnose-from-observation-not-prior.md`](~/.claude/rules/diagnose-from-observation-not-prior.md): the resident core carries the statement, trigger and red flags; this file is the full body.

Sibling of [`premise-observed-not-inferred.md`](~/.claude/rules/premise-observed-not-inferred.md):
that rule governs the premises work is *built* on; this one governs the causal hypothesis a
*diagnosis* starts from. Same invariant, observation beats inference, applied in opposite directions.

**Set the diagnosis from the cheapest direct observation, not from the prior you walked in with.**

## Pattern

Every diagnostic surface hands you a prior for free: your own first guess, a reviewer's plausible
theory, what the code "should" do, the reputation of the host or author, the memory of a similar
incident. Confirming that prior is always cognitively cheaper than observing, so each surface
produces its own incident and the family grows without being named.

The economics are constant: the direct observation costs seconds (`ls` the output dir, run the
failing command, diff the working sibling, one `get-iam-policy`, one correlation query) while the
confirmed-wrong prior costs a shipped non-fix, a wasted debugging pass, or a false triage verdict.
The compounding cost is worse: a prior that gets *documented*, in a code comment, a ticket RCA or a
case determination, outlives the incident and misleads the next responder, converting one wrong
guess into an institutional wrong fact.

Two disciplines recur on every surface:

1. **The evidence in hand already discriminates.** Outputs, status codes, a working sibling, alert
   topology: the symptom usually carries a free signal that names which axis to check first. Read it
   before theorizing.
2. **Name the observation that would falsify your hypothesis**, then run it. If you can't name one,
   you don't have a diagnosis; you have a prior.

## The surfaces

| Surface | The sentence applied there |
|---|---|
| bug fixes in code or hooks | check what the system *actually produced* (outputs, logs, a manual run) before editing anything |
| debugging in an established codebase | the cheapest observation is the working sibling: diff broken against it before hypothesizing from first principles |
| discriminating error signals (status codes, infra/IAM) | the status code names the axis; run the one authoritative check on that axis before shipping or documenting any fix, and at an enforcement point check its mode before its rules |
| detection / triage | the true-positive prior comes from the correlation pass, never from host or user reputation |
| your own tooling misbehaving (hangs, timeouts, runaway repeats, orphans) | the anomaly is written down and explained by observation before anything scales up, never dismissed as "TTY", "stale" or "busy box" |

## Applying it on a new surface

1. Notice the prior you're carrying: the hypothesis you'd bet on before running anything. It usually
   arrived from outside the evidence (a reviewer, a memory, a reputation, a plan).
2. Read the discriminating signal already in hand: what does the error code, output shape or
   co-occurrence pattern rule out on its own?
3. Find the cheapest authoritative observation on the axis that signal points to, and the nearest
   working sibling to diff against.
4. Run the observation *before* acting on or writing down the prior. Until it has run, label the
   prior "hypothesis" in anything you write, never "cause".

## Red Flags — class level

- Your reasoning contains "probably", "should be", "I know this host/user/tool", or a hypothesis
  someone handed you, and no observation has run yet.
- You're about to document a root cause (comment, RCA, case determination) you have inferred but not
  observed.
- A discriminating signal is present (status code, missing output, working sibling) and your
  reasoning never mentions which causes it rules out.
- Your investigation plan consists only of steps that would *confirm* the prior, none that could
  falsify it.
- The determination you're writing would read identically if you had run no checks at all.

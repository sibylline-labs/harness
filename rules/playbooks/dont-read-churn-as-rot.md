# Don't Read Churn as Rot

> **Playbook for** [`dont-read-churn-as-rot.md`](~/.claude/rules/dont-read-churn-as-rot.md): the resident core carries the statement, trigger and red flags; this file is the full body.

A component that has been remodelled many times, kept a quirky name, or branches on many small
conditions is not therefore "debt." Surface churn is not the diagnosis. Before calling something rot
or recommending a teardown, locate the *structural* cause and check whether each change solved a real
emergent problem.

## Pattern

Frontier work on a genuinely hard problem looks like repeated remodels: the model ships before the
problem is fully understood, then reality arrives and each iteration closes a real sub-problem.
Iteration count, a persistent name, an audit with findings, or many small branches are *surface
metrics*. Pattern-matching "lots of changes to one thing = thrashing" is the standards-obsessed
reflex: it mistakes the *receipts of solving hard problems* for evidence of sloppiness.

The tell: you're about to describe a working, load-bearing component as "debt / premature /
overloaded / thrashing" based on *how much it changed* or *how it looks*, not on a structural cause
you've actually located.

## DO

- Ask "did each change close a real emergent problem?" before "there are too many changes." (For an
  authorization primitive: moving from a login-message signature to typed-data signing solved agent
  signing; the scope catalog is a capability grammar; audience plus a trusted execution environment
  solved multi-tenancy and the trust boundary. Each was a real problem, not thrash.)
- Separate "this surface looks churny / quirky" from "here is the structural cause." Name the cause
  before proposing change.
- Weigh whether the thing is a genuine *asset* (does it solve a problem peers only name?) before
  recommending its replacement.
- Propose change at the level of the cause, not the surface.

## DON'T

- Score iteration count, a persistent name, an audit's existence, or branch count as debt.
- Infer strategic intent from a naming choice (a name kept for a joke is not a "strategic
  primitive").
- Recommend replacing a primitive with a "simpler" thing because the simpler thing is easier to
  reason about. That's the same bias one level down; it throws away properties the primitive earned.
- Treat "I'd have built it differently" as "it's wrong."

## Red Flags

- Your write-up uses "thrashing," "premature," "overloaded debt," or "perpetual retrofit" about a
  component that is *working in production*.
- Your evidence is a count (6 remodels, N branches) rather than a located structural cause.
- You're recommending a teardown or replacement and haven't named what each iteration was solving.
- You inferred intent from a name.

## Companion

[`break-the-false-binary.md`](~/.claude/rules/break-the-false-binary.md): a first reframe can itself
carry this bias.

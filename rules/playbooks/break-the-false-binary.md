# Break the False Binary — Reframe the Axis When Every Option Is Bad

> **Playbook for** [`break-the-false-binary.md`](~/.claude/rules/break-the-false-binary.md): the resident core carries the statement, trigger and red flags; this file is the full body.

When the choices in front of you are "a bad hack or an even worse one," that's usually a signal the
decision was framed on too narrow an axis. Reframe the axis up a level before choosing. But beware:
your *first* reframe can carry the same bias that produced the binary. Verify you've reached the
structural cause, not just a different-shaped guess.

## Pattern

A bad-vs-worse binary means the candidate solutions all live on one axis, and the axis is probably
wrong. The way out is to reframe one level up ("what *kind* of problem is this really?") until a
non-bad option appears. The failure mode is reframing to a *different surface* rather than the
*structural cause*: jumping to "the simpler thing" (a database row instead of a token, a rewrite
instead of the existing system) is itself a bias (see
[`dont-read-churn-as-rot.md`](~/.claude/rules/dont-read-churn-as-rot.md)), not a real reframe.

## DO

- When you're ranking bad-vs-worse, stop and reframe the axis up a level ("is this even a token
  problem? a consent problem? a routing problem?").
- Push the reframe until you reach a *structural cause*, not just a different mechanism. In one
  consent-token design, the real axis was not "which token mechanism for consent" but "caller context
  is inferred from a header matrix and enforcement is fail-open." That is where the non-bad options
  live.
- Sanity-check your reframe against `dont-read-churn-as-rot`: if your "better option" is just "the
  simpler/newer thing," you've reframed to another surface, not the cause.

## DON'T

- Accept the binary as the nature of the problem.
- Treat your first reframe as automatically correct; it can carry the original bias.
- Reframe toward "tear it down and do the simple thing" without locating the structural cause.

## Red Flags

- "a bad hack or an even worse one" (or internally ranking bad-vs-worse).
- Your reframe lands on "replace X with a simpler Y"; check it's not churn-as-rot bias.
- You proposed a third option but can't name the structural cause it addresses.
- The design needs a large hand-maintained list or map that partitions some identifier space by a
  property (retryable/terminal, public/internal). Ask whether the identifier or type can carry the
  property itself. The list is transport; the property belongs to the thing it describes. A
  557-entry partition collapsed once the error code itself carried a retryable suffix.

## Source shape

A consent-token design was presented as "overload an existing token for consent (bad) vs an
unconsented passthrough or a new primitive (worse)." The first reframe, "use a database consent row",
was itself the churn-as-rot bias: simpler is not correct, and it threw away the token's cryptographic
portability. The real reframe was structural, prompted by asking why the audience claim had been so
load-bearing.

# Work at the Owning Layer

> **Playbook for** [`work-at-the-owning-layer.md`](~/.claude/rules/work-at-the-owning-layer.md): the resident core carries the statement, trigger and red flags; this file is the full body.

**Do the work at the layer that owns it. When the owning layer is out of reach or broken, move the
work or fix the layer; never bypass it, re-implement it, or delete it.**

## Pattern

Every capability has an owning layer: the SDK owns database access, the workflow infrastructure owns
retries and dead-lettering, the platform owns egress and credentials, the redundant path owns its own
defect. The owning layer is always one seam away (a context you can't reach from where you're
standing, a repo that isn't the one you have open, an infra behaviour you don't control) and the
workaround is always locally cheaper: a raw `text()` query, an env-var pop, a try/except, a hand-rolled
HTTP client, a deleted fallback. Each stays inside the file you're already editing, so each surface
mints its own incident, and the family grows un-named.

What the workaround actually does is fork ownership. Two layers now do one job, and the owning layer's
guarantees (pooling, tracing, retries, dead-letter queues, credential storage, resilience) no longer
apply to your fork. The cost lands later as drift, a leak surface, or a silent failure. Crossing the
seam today (refactor into a dependency, an SDK fix, an IAM binding, a connector config) is a one-time
cost; owning a second implementation is forever.

The economics never favor the bypass, because the bypass *feels* like less work only while the seam is
in view. This holds with extra force for internal SDKs, shared tooling, workers and platform config:
they are all ours, so "the owning layer is another repo" is never "the owning layer is someone else."

## The surfaces

| Surface | The sentence applied there |
|---|---|
| database access | the ORM or SDK owns DB access; when it's out of reach, move the code to where it is, and never bypass it with raw SQL or direct engine access |
| HTTP concern placement | route-scoped work belongs at the dependency layer where the request context is in reach; middleware placement forces the raw-SQL bypass |
| internal SDK defects | the SDK owns its bugs, and it's ours: fix at source, never an app-side workaround |
| redundant / fallback paths | the broken path owns the defect: repair it; don't delete the redundancy to route around it |
| workflow failure handling | the workflow engine's retry and dead-letter queue own failure handling: raise and let it; don't re-implement it with `success=False` result objects |
| external integrations | the platform's connector layer owns egress, credentials and retries: configure it; don't hand-roll a client and a new secret |
| invariants a plan or dispatch brief introduces | the highest ladder rung that holds an invariant owns it: name it in the plan's rung table, and a test row says why no rule can |
| conversational scope hypotheses under a speed mode | a user's shorthand ("feels like a skill fix") is tested against the ladder, never used to ship prose for a runtime or mechanical defect; push back in one line when prose cannot hold it |
| React components and hooks | the auth SDK, router and query layer own their state: read it during render; an effect only syncs with a system React doesn't own |

## Applying it on a new surface

1. Name the layer that owns the capability or the defect: SDK, ORM, workflow infra, platform, the
   sibling path that actually broke.
2. Say what that layer owns that your workaround would have to re-own: credentials, retries, pooling,
   tracing, dedup, resilience.
3. If the layer is out of reach, move the work to it (a dependency instead of middleware, a service
   instead of a script). If it's broken, fix it there: internal layers are our own lift, not a vendor
   blocker.
4. Replace or remove an owning layer only when the *design* is wrong, not its implementation, and state
   the trade-off out loud before doing it.

## Red Flags — class level

- You're writing a second implementation of something a layer you already use does: retries, egress,
  failure handling, SQL execution, secret storage, fallback routing.
- The justification is reach ("can't get `ctx` here"), ownership ("that's the SDK / another repo"), or
  blame ("this path caused the bug"), none of which is a design argument.
- A "temporary until X" comment attached to a bypass of a layer you own.
- Proposing to delete a fallback, replica or second provider because its implementation broke.
- A new `*_TOKEN` / `*_KEY` env var for a system that a platform you already operate integrates with
  natively.

## Related

[`break-the-false-binary.md`](~/.claude/rules/break-the-false-binary.md) and
[`dont-read-churn-as-rot.md`](~/.claude/rules/dont-read-churn-as-rot.md) govern the
*replace-it-with-something-simpler* reflex one level up;
[`close-the-blast-radius.md`](~/.claude/rules/close-the-blast-radius.md) governs change completeness,
not change placement.

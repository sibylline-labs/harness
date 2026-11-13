# Work at the Owning Layer

**Do the work at the layer that owns it — when the owning layer is out of
reach or broken, move the work or fix the layer; never bypass it,
re-implement it, or delete it.**

Fires when the cheap fix stays in your file but duplicates a job another layer
owns: SQL, retries, egress, credentials, fallbacks, type checking. Name the
owning layer and what your workaround would re-own. Then move the work to that
layer or fix it there. Internal SDKs, shared tooling and platform config are
ours: "another repo" is never "someone else's". Playbook:
[`~/.claude/rule-playbooks/work-at-the-owning-layer.md`](~/.claude/rule-playbooks/work-at-the-owning-layer.md),
for the mechanism, the new-surface procedure and the surfaces it governs.

## Red Flags

- You are re-implementing what a layer you already use does.
- The justification is reach ("can't get `ctx` here") or ownership ("that's the SDK"), not design.
- A "temporary until X" comment on a bypass of a layer you own.
- Deleting a fallback or second provider because its code broke.
- A new `*_TOKEN` / `*_KEY` for a system a platform you run already integrates with.

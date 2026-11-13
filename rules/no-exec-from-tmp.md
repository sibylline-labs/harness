# Never Write-And-Execute Scripts From /tmp (or World-Writable Temp)

**Never exec an ad-hoc script from a world-writable temp dir; when your tooling
trips a security detector, fix the tooling, never suppress the detector.**

Fires whenever you are about to write a script or query file and run an
interpreter on it, or when you brief a subagent that will. Exec-from-temp plus a
network call is a classic attacker TTP, and endpoint security rightly flags it.
The playbook,
[`~/.claude/rule-playbooks/no-exec-from-tmp.md`](~/.claude/rule-playbooks/no-exec-from-tmp.md),
holds the full pattern and the safe alternatives.

## DO

- Prefer an in-process tool (a repo CLI, an SDK call) over an ad-hoc file.
- When a file is needed, write it to a gitignored repo working dir (e.g. `data/scratch/`)
  and run it from there, or pipe a single-quoted heredoc to the interpreter (`python3 - <<'PY'`).
- Put the no-`/tmp` instruction explicitly in subagent dispatch prompts.

## Red Flags

- `mktemp`, or a write to `/tmp`, `/var/tmp`, `/private/tmp` or `$TMPDIR`, followed by an interpreter call.
- A detector fired on your own automation and your first instinct is an allowlist or exclusion.
- "`$TMPDIR` isn't literally `/tmp`, so it's fine."

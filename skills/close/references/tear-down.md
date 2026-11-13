# Stage: tear-down

Every profile. Remove a worktree only when all four hold: its branch is merged (or its PR is merged
or closed) on the remote (observed), `git status --porcelain` is empty, nothing is unpushed, and it
maps to *this* work by the loop hand-back's `worktree: <abs path>` line, branch, or issue key. Other
jobs share the machine, and a worktree they own is not yours to remove. `cd <main checkout>` first so
your shell cwd is outside the worktree, then run `git -C <main checkout> worktree remove <path>`
(never `--force`) and keep the branch. Your own session worktree goes last, through `ExitWorktree`
with `remove` when `EnterWorktree` created it, or
`cd <main checkout> && git -C <main checkout> worktree remove <path>` for a plain git worktree.

The four conditions decide, not `ExitWorktree`: it acts only on a worktree this session's
`EnterWorktree` created (a no-op in a session resumed inside an earlier session's worktree), and it
has refused a clean worktree whose commits were all on `origin/main` once its branch was renamed.
When it refuses or does nothing and the four conditions hold, don't retry with
`discard_changes: true`; keep the worktree. If `ExitWorktree` with `keep` takes the session out, run
`git -C <main checkout> worktree remove <path>` yourself. If the session can't leave, the worktree is
its working directory and removing it would strand every later command: record the row as
`kept: session cwd`, with that command as its receipt, and list it in the final report under
`follow-ups:` for cleanup after the session ends, never under `needs input:` (removing a clean
worktree is not a human-only action). The command is the receipt that completes the row, and it is
not a hold: the work is merged and clean.

Tear a workbench down with the command that brought it up, in reverse: for an `eris workbench`, that
is `eris workbench down <name>`, then `eris workbench rm <name> --yes`. Never pass `--force`: when
the tool refuses because a worktree holds real work, that work is a hold.

**Done when:** `git worktree list` (and `eris workbench list`, if one was used) no longer show the
rows you removed, and every row you kept says why.

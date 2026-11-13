# Merging a loop's PR

Read before any `gh pr merge` the TPM runs.

## Merge preflight

Before any `gh pr merge`, run `eris ask list --issue <KEY> --open` and read the issue's latest
hand-back comment (`list_comments` on the issue, newest first). Refuse to merge while any of these
holds, and route each unrouted question by creating an `eris ask` (`--recommend <id>`, `--blocking`
when one-way or tier-1) or filing an issue related to the target issue:

- `eris ask list --issue <KEY> --open` lists an open ask bound to the issue;
- a hold: "leaving the merge to you", "do not merge", or a merge asked of a human;
- a question in prose in the hand-back with no ask id and no answer from the human after it in the
  thread;
- a diff on a tier-1 surface (auth, secrets, webhooks, tenancy).

Green checks never override a hold. A PR merged seconds after a hand-back that held the merge loses
its tier-1 question with the Done move, so the preflight stands alongside any required `asks / open`
ruleset check.

## Merge and train

Once the merge preflight passes on a ready PR, enable auto-merge with
`gh pr merge <n> --repo <owner/repo> --auto --squash --match-head-commit <sha>` (use `--merge`
instead of `--squash` where the repo disables squash merge; never use `gh pr merge --admin`, and
never rebase or force-push PR branches). Keep at most one PR in flight per repo: after each merge
notification, update the oldest `BEHIND` auto-merge PR with `gh pr update-branch <n>` (a merge
commit), and report `DIRTY` PRs that need their session to merge `main` in.

## Merge → close-out

Under gated autonomy, a TPM merge of a loop's PR (`<repo>#<n>` at merge commit `<sha>`) counts as
the review grant for that loop's `/close-out`. The grant runs the close on profile `tpm-merge`: the
`terminus` stages plus the doctrine close stages (`improvement-loop`, `lift-to-sdk`), once, in the
loop. `tpm-report` stays with you, and the profile forbids it in the loop. Immediately after
`gh pr merge` succeeds:

1. Message the session that built the PR with
   `/close-out <PR> -- authorized: TPM merge <repo>#<n> <sha>` (`SendMessage` to the live session).
   The loop then tears down its worktree and workbench, updates Linear, files the doctrine stages'
   suggestions and stops its own session last.
2. When the loop's close-ledger comment lands on the issue, take its `follow-ups:` line (filed
   follow-ups, `dispatch: allowed` improvement suggestions, `follow-up:` lift lines) as Delegate rows
   under your own decision rights. Never send `/close-next` for a PR you merged: it would run the
   doctrine stages a second time and a second TPM pass beside you.
3. For loops that are dead or never answer, remove their clean merged/closed worktrees by hand
   (`git worktree remove`, never `--force`) and stop the sessions.

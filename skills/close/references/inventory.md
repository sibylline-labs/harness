# Stage: inventory

Every profile. Resolve the scope, claim the close-out and open the ledger.

Resolve the scope from the argument, or else from the session: the branch's PR
(`gh pr view --json number,state,isDraft,mergeable,headRefOid,body,reviews,comments`), its issue
key, the repo's worktrees (`git worktree list`), and the active workbench, if the run used one
(`eris workbench list`). Read any standing operating notices first, since a focus or platform
notice can change what "done" means.

Read the PR timeline since the LGTM. A new commit or review comment after it is a hold.

## Claim the close-out before `land`

Two runs on one PR would both merge, deploy and release. The claim lives in the thread where
`close-ledger` posts: the primary Linear issue, or the PR when there is no issue. Every run must pick
the same thread, so the primary is the issue key in the PR's head branch name, else the first
`Fixes`/`Closes`/`Part of` key in the PR body, else the PR itself. Mint the run id once:
`close-out-$(date -u +%Y%m%dT%H%M%SZ)`.

1. Read the **whole** thread oldest first: `list_comments` with `orderBy: createdAt`, `limit: 250`,
   following `cursor` until `hasNextPage` is false (on the PR,
   `gh api --paginate repos/<owner>/<repo>/issues/<n>/comments`). A **live claim** is a comment
   containing `close-out claim · <PR url>` with no `## Close-out — <PR url>` audit log after it. A
   live claim from another run is a hold: stop before `land`, post nothing to the thread (an audit
   log would release that claim), and report the hold naming the comment and its age. If that run is
   dead, the reviewer deletes the comment and re-runs. An audit log with no live claim after it means
   an earlier run closed this PR out: this run works only that log's held rows.
2. Post `close-out claim · <PR url> · run <run id> · profile <terminus|tpm-merge|next>`
   (`save_comment`) and record the comment's `id` and `createdAt`.
3. Re-read the thread. When another live claim has an earlier `createdAt` (a tie goes to the lower
   `id`), delete yours (`delete_comment`) and stop the same way: that run owns the close-out.

The `close-ledger` stage releases the claim. A run that ends before it deletes its claim comment
first. Work on held rows after an audit log, the posting run's own included, claims again first.

**Done when:** this run holds the earliest live claim (its comment id is in the ledger), and the
ledger has a row for the PR, for every Linear issue the work might close (see
[linear sweep](linear-sweep.md) for how to find them), for the deploy step or "none", for each
worktree and workbench mapped to this work, and for every deferred item in the PR body, review
threads and session.

# Linear sweep — every issue the work touched

The GitHub integration auto-closes the primary issue at best. A close-out finds every issue the
merged work affects and makes each one reflect it.

## Find the candidates

Union these sources, then de-duplicate:

1. **Magic words.** `Closes / Fixes / Resolves / Part of / Refs <KEY>` in the PR body, the PR title,
   and every commit on the branch (`git log <base>..<merge> --format=%B`).
2. **Bare keys.** Any issue key (`<TEAM>-<number>`) in the PR body, commits, review comments and code
   comments added by the diff (`gh pr diff <n> | rg '^\+.*\b[A-Z]+-[0-9]+'`).
3. **Relations.** The primary's parent, sub-issues, and `blocks` / `blocked by` / `related`
   (`get_issue` with relations).
4. **Siblings.** Other children of the primary's epic whose description names this change's surface.
5. **Session.** Issues worked, cited or filed earlier in this session.

## Judge each one

Read the issue's description **and its full comment thread**, because comments override the
description. Then compare against the merged diff:

| The merged diff… | Action |
|---|---|
| meets every acceptance criterion | Done, with a comment: `Closed by <PR> (<merge sha>)` plus one line on how |
| meets some criteria | Leave the status; comment with what landed and what remains |
| unblocks it | Comment on it; leave the status (re-prioritising is `/tpm`'s job) |
| doesn't touch it after all | Drop it from the ledger with a reason |

Judge from the criteria, not from the fact that the key appears in the PR. When the evidence is a
guess, choose partial-plus-comment and log the assumption.

Check the primary as well: when this PR closes the primary (`Closes` / `Fixes` / `Resolves <KEY>`,
not a contributing `Part of <KEY>` PR whose sibling PRs are still open) and the integration didn't
move it to Done, move it yourself and note in the log that the integration didn't fire.

## Record the actual effort

For each issue moved to Done (not partials), measure and write the actual (the `/linear-workflow`
§ Estimates contract):

1. `uv run --script "$HOME/.claude/skills/linear-workflow/scripts/active_time.py" --issue <KEY> --current`,
   adding `--session <id>` for any earlier session the ledger or handoffs name. Partial coverage is
   fine as long as the receipt says so; a recalled number is never fine.
2. Read the current `estimate` first: that is the `est` half of the receipt, unless an earlier
   `effort:` line exists (from PR open), in which case copy that line's `est`.
3. `save_issue estimate=<points>`, then post the `effort:` line (in the ledger comment for the
   primary, as a standalone comment on the others).
4. Walk up `parentId`: if the parent's estimate is now below the sum of its children, raise it to
   the sum snapped up and post an `effort:` line with `children <sum>`.

When the closing session didn't do the work and no session can be found, write
`effort: est <old> → actual unmeasured (<why>)` and leave the estimate as it is.

## Write correctly

Make every write through `/linear-workflow`. Use the status UUIDs of the issue's own team (read with
`list_issue_statuses` for that team): names resolve to the wrong team's states across teams. Re-read
each issue after writing it. The re-read is the receipt.

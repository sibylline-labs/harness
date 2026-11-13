# Stage: follow-ups

Every profile. Route every deferred item, nit, TODO, out-of-scope finding and review suggestion not
taken to its owner. A finding is discharged only when it reaches the actor who will close it, never
by being written down:

- other work goes to a Linear issue via `/linear-workflow`, related to the primary;
- harness friction goes to `eris yak`;
- a scope or policy call goes to the report as one line.

This stage files and routes. It never launches a session: under `terminus` a filed follow-up stays
filed for the reviewer or `/tpm` to pick up, under `tpm-merge` the ledger's `follow-ups:` line hands
it to the TPM that merged the PR, and under `/close-next` the scoped `/tpm` report
([`tpm-report`](tpm-report.md)) takes the rows as Delegate candidates. Post-merge verifications,
harness syncs, and kept session-cwd worktree cleanup commands go under `follow-ups:` in the report,
never under `needs input:` (reserved for human-only actions carrying `ask <id>`).

**Done when:** each follow-up row carries an issue key or a yak receipt. Prose with no receipt fails
this stage.

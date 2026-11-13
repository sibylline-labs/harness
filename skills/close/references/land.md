# Stage: land

Every profile. Merge the reviewed PR, or record the existing merge when the PR is already `MERGED`
(e.g. `/close-out` invoked by `/tpm` with `authorized: TPM merge <repo>#<n> <sha>`).

When `gh pr view <n> --json state,mergeCommit` already shows `MERGED`, record `mergeCommit` in the
ledger (confirming it matches `<sha>` when the grant names one) and skip the merge steps below.

When the diff changed an `eris.yaml` or a governance site (a config key, a service seam, a queue, an
event), run `eris lint --all --strict` on the branch first. A missing, stale or malformed pragma is
a governance fact, not behavior: fix it in a pragma-only commit (inline, naming specific paths, with
the repo's hooks intact), re-run the check, and log it as an assumption. A finding whose fix would
change code is a hold.

Merge with the merge recipe: a merge commit with `--match-head-commit <sha>`, the branch kept, never
`--admin`. A draft is covered by the LGTM: run `gh pr ready <n>` first. Then run
`gh pr checks <n> --watch` and merge. When the work spans several PRs (a workbench seam across
repos), merge them in dependency order, each one before the PR that consumes it.

On a conflict, update the branch from the base and resolve it so both sides' changes survive. Re-run
the repo's gates, push, watch CI once, and merge on the **new** head SHA. A conflict is mechanical
when both sides' intent survives unchanged; resolve it and log it. A conflict whose resolution would
change behavior the reviewer approved is a hold.

**Done when:** `gh pr view <n> --json state,mergeCommit` shows `MERGED`, and the merge SHA is in the
ledger.

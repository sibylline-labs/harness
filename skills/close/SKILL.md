---
name: close
kind: workflow
description: The close workflow, run after the reviewer's LGTM or a TPM merge by its two entry points — /close-out (profile terminus, or tpm-merge under a TPM merge grant) and /close-next (profile next). Lands the PR, deploys, sweeps Linear, files follow-ups, tears down, captures decisions with `eris socrates` and posts the audit log; tpm-merge also runs improvement-loop and lift-to-sdk, and next runs those plus a scoped /tpm report.
disable-model-invocation: true
---

# Close

The reviewer read the work and said **LGTM**, or a TPM session merged the loop's PR and passed
`authorized: TPM merge <repo>#<n> <sha>`. A close takes that reviewed work from an open or
just-merged PR to *nothing left behind*: merged, deployed, tracked, tidied and written down. It is
one Workflow with three profiles:

- **`terminus`** (`/close-out`): the work ends here. Follow-ups are filed and reported, never
  dispatched.
- **`tpm-merge`** (`/close-out` carrying `authorized: TPM merge <repo>#<n> <sha>`): everything in
  `terminus`, plus `improvement-loop` and `lift-to-sdk`. The TPM that merged the PR dispatches the
  follow-ups and runs its own `/tpm` pass, so this profile forbids `tpm-report`. The ledger's
  `follow-ups:` line hands it what to dispatch.
- **`next`** (`/close-next`): everything in `tpm-merge`, plus a scoped `/tpm` report.

**The LGTM (or `authorized: TPM merge <repo>#<n> <sha>` grant) is the approval for every stage
below.** Don't stop to ask. Pull the reviewer back in only for a **hold** (listed below). Every
judgement call you make instead of asking is an **assumption**: it goes in the audit log as
*assumed X because Y*. A senior engineer makes the call and writes down why. That is the mandate. A
commit a stage makes is covered by the same grant: commit inline, naming specific paths, with the
repo's git hooks intact.

Voice and rigor follow `/pls`. Output compresses to the floor and independent stages run in
parallel, but premise checks and verification are not compressed. The work was built with full
rigor, so it closes the same way.

User-invoked by design, through the two entry points. An LGTM on a plan or a draft must never trip a
merge, a deploy or a delete.

## The close ledger

Keep one ledger for the run. Each row is one thing the work touched: a PR, a Linear issue, a deploy
step, a worktree, a workbench, a follow-up, a Socrates capture or `/tpm` pass. Each row ends with a
**disposition** (done / held / not applicable) and a **receipt** (SHA, URL, issue key, removed path,
command output). The ledger becomes the audit log in `close-ledger`, so a row without a receipt is
unfinished.

`$RUN` is the run's scratch directory, `~/.claude/close/<run id>/` (`mkdir -p` it once the
`inventory` stage mints the run id). Receipt artifacts live there.

## Stages

Run them in order; a stage outside the run's profile is skipped. Each is a reference read when the
run reaches it. A stage with a receipt records `eris gate record <stage>` on the primary issue and
keeps the printed comment id for the final check.

| Stage | Profiles | Read |
|---|---|---|
| inventory | terminus, tpm-merge, next | [references/inventory.md](references/inventory.md) |
| land | terminus, tpm-merge, next | [references/land.md](references/land.md) |
| deploy | terminus, tpm-merge, next | [references/deploy.md](references/deploy.md) |
| linear | terminus, tpm-merge, next | [references/linear.md](references/linear.md) |
| follow-ups | terminus, tpm-merge, next | [references/follow-ups.md](references/follow-ups.md) |
| improvement-loop | tpm-merge, next | [references/improvement-loop.md](references/improvement-loop.md) |
| lift-to-sdk | tpm-merge, next | [references/lift-to-sdk.md](references/lift-to-sdk.md) |
| tear-down | terminus, tpm-merge, next | [references/tear-down.md](references/tear-down.md) |
| socrates | terminus, tpm-merge, next | [references/socrates.md](references/socrates.md) |
| tpm-report | next | [references/tpm-report.md](references/tpm-report.md) |
| close-ledger | terminus, tpm-merge, next | [references/close-ledger.md](references/close-ledger.md) |

`socrates` and `tpm-report` are independent: dispatch them in parallel.

**Doctrine `close.*`.** Before `improvement-loop` and `lift-to-sdk`, read the active posture's
`close:` map (`eris doctrine check`; the `policy:` block in the doctrine file). `off`: don't run the
stage, log `not run: doctrine <posture> close.<stage> off`, and record nothing; the final check
records the doctrine `SKIPPED` itself. `on` or `file-only`: run the stage's reference with that
mode. The doctrine is the one source of the mode, and each stage re-reads it.

## Profiles

[`profiles.yaml`](profiles.yaml) holds all three. `next` requires every stage that records a
receipt. Each other profile **forbids** every `next` gate it does not require: `terminus` requires
`close-ledger` and forbids `improvement-loop`, `lift-to-sdk` and `tpm-report`; `tpm-merge` requires
`improvement-loop`, `lift-to-sdk` and `close-ledger` and forbids `tpm-report`. Any receipt for a
forbidden gate on the primary issue makes the check print `<gate>\tforbidden\t<verdict>` and exit 3,
and re-recording never clears it. The run ends in `close-ledger` on

```bash
eris gate check --issue <primary> --profile <terminus|tpm-merge|next> \
  --profiles ~/.claude/skills/close/profiles.yaml --expect <the ids this run's record calls printed>
```

## Holds: the only reasons to pull the reviewer back

Finish every other row first. Then report each hold in one line naming the single action it needs:

- Another run holds a live close-out claim on the PR (`inventory`).
- The pre-release re-check finds the version already tagged, committed or published, or this run's
  claim no longer earliest (`deploy`).
- Commits or review comments landed after the LGTM.
- A conflict resolution would change reviewed behavior.
- CI is still red after one fix attempt, or branch protection can't be met without `--admin`.
- The deploy reaches past a local runbook into prod infra, migrations or destructive data.
- A worktree or workbench holds unmerged or unpushed work.
- A Linear or `/tpm` change sits in an **Ask the human first** row.
- An issue the work closes has an open blocking ask: Done is refused; answer or withdraw the ask.
- The profile check exits 3 (`close-ledger`).

A tier-1 surface is **not** a hold here, unlike under `/pls`: the review already covered it.

## Handoff

`close-ledger` ends the run: the audit-log comment on the primary issue (it releases the `inventory`
claim), the check's lines in it, and the same content as the final report.

## See also

- `/pls`: the voice this workflow borrows.
- `/linear-workflow`, `/tpm`; `eris socrates --help` for the capture verbs.
- `verification-before-completion`: every **Done when** in a stage is an observation.

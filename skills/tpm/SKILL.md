---
name: tpm
kind: workflow
description: >
  Technical project manager for Linear: owns how work is carved — epics, critical path,
  milestones, project boundaries, owning team, and the comms after a re-carve. Use when
  the user asks for a "PM pass", a hygiene sweep, to "project manage" or re-scope an
  epic/project, to break a PRD or plan into issues, for the critical path or "what's
  blocking what", or says they are drowning in what is where. Bare `/tpm` sweeps the
  active portfolio. Writes go through linear-workflow.
---

# TPM

`/linear-workflow` answers *is this issue filed correctly*. `/tpm` answers *is this work carved
correctly*: the right epics, the right path, the right projects, the right team, and the human told
about it. Run it so the human never has to name the defect themselves. Every correction a human
tends to make by hand is a check in [`references/checks.md`](references/checks.md).

## Scope

| Invocation | Scope |
|---|---|
| `/tpm` bare | The **active portfolio**: every `started` / `planned` project the user leads or holds issues in, read through the team's standing focus statement first, if it has one. A focus statement decides what may be *promoted* (a paused area gets hygiene only; nothing moves to Todo there). |
| `/tpm <project \| initiative>` | That container and every issue, milestone and sub-issue in it |
| `/tpm <EPIC-ID>` | That epic, its children, and anything blocked by or blocking them |
| `/tpm <PRD / doc / plan>` | **Decompose**: check for an existing `## PRD Review` section first (see **First-time PRD review** below) — run `/prd-review` only on the first pass, then carve the approved source into epics, slices, milestones and relations, and audit the result as if it already existed |

### First-time PRD review (on `/tpm <PRD>`)

Do not re-run `/prd-review` on every `/tpm` pass:

1. **Already approved without issue:** When the PRD already carries a `## PRD Review` section marked
   **Approved** with no open blocking issues, **skip `/prd-review`**, note any recorded guidance and
   steering in that section, and continue directly to Step 1.
2. **First review (clean or minor adjustments):** When no `## PRD Review` section exists (or a prior
   review is unapproved), run `/prd-review` once in the main loop and append a `## PRD Review`
   section outlining the review summary, steering guidance, and any required / requested / suggested
   changes. Once marked **Approved**, proceed to carve.
3. **First review (substantial issues):** When `/prd-review` surfaces substantial issues (unobserved
   or inverted load-bearing premises, a missing Gate-0 walking skeleton that reshapes the arc,
   cross-PRD conflicts, or major decision-register rework), **spare the PRD inline details and
   prose**. Append a brief summary under `## PRD Review` (`Status: Changes Requested — see the PRD
   review issue`), suggest creating a PRD review issue for that PRD, and place the full thoughts and
   commentary on that issue rather than carving premature Epics.

## Steps

### 1. Load the ground truth

Read the standing focus statement if there is one, the scope's project(s) (`get_project`: goal,
target date, lead, description, milestones), every issue with `parentId`, relations, status, labels
and team, and the project's latest pulse (`get_status_updates`). For a project enrolled in
`eris socrates`, run `eris socrates consult --canon` (or `--brief`, with `--project <name>`) for its
load-bearing decisions — a carve that contradicts a decision is a finding, not a fix. A refusal with
a settings link means no Canon is confirmed, which is a valid answer. For more than ~40 issues or 2+
projects, dispatch one `tpm-auditor` agent per project in parallel and merge their findings tables.

**Done when:** every issue in scope is loaded with its parent, relations and milestone, and each
project's goal/deadline is known or recorded as missing.

### 2. Audit against every check

Run every check in [`references/checks.md`](references/checks.md) against the loaded state — all
twelve, every time, not the ones that look relevant. Each finding names the check, the issues it
applies to, the evidence (field values), and the proposed fix. Before any fix that moves, re-teams
or recreates something, read [`references/linear-constraints.md`](references/linear-constraints.md).

**Done when:** each of C1–C12 has a result line (findings, or "clean" with the query that proved it).

### 3. Present the carve as one diff

One table, grouped by project: `check → issue(s) → now → proposed → rung` (rung per C12 for code-fix
rows). Split it by the decision rights below into **Will apply** and **Asks**. Lead with the
critical path as it will stand *after* the carve: the single next issue per lane, then the ordered
chain behind it. Add one **Delegate** row, `<ISSUE> → build session`, for each next issue to start
building. A row whose issue passes your team's delegation guards on its post-carve state goes under
**Will apply**; any other goes under **Asks**. The guards at minimum: the issue has no open ask, no
unreviewed tier-1 surface (auth, secrets, webhooks, tenancy), and a named sibling implementation to
copy. Implementation the TPM starts always goes to a fresh session running `/work`: never dispatch
`impl-*` Agent subagents for it. Those are only for a work loop's own Mode-2 phases.

For each **Asks** candidate, check Canon (`eris socrates consult --canon`) for a house default first:
a question a Canon house default settles becomes a **Will apply** row citing the default, not an
ask. Otherwise create the ask with
`eris ask "<question>" --issue <row's issue, else the epic or tracking issue> --option <id>[=<label>] … --recommend <id>`
(adding `--blocking` and `--door one-way` only for a one-way door or a tier-1 surface; if `eris ask`
fails `asks-store-unreachable`, run `eris ask list --issue` before re-asking) and show the row with
its ask id. Ask for one approval of the whole diff (the human may strike rows). When the human is
not in the session (a background loop), do not poll for their answer: end the turn after raising
the ask and let the harness re-invoke the session on an answer.

**Done when:** the human has approved the diff, struck rows are dropped, and every Asks row has an
ask id and the human's answer (from `eris ask list --issue` or in chat; an ask answered in chat
stays open in the store, so withdraw it with `eris ask withdraw <id>` and quote the chat answer in
the pulse).

### 4. Apply through `/linear-workflow`

Load `/linear-workflow` and write with its hard rules (UUIDs from the issue's own team,
`get_project` before setting a project, existing labels only, and Rule 5 for status writes: clear a
cycle in a second call, mark Duplicate with `duplicateOf` alone). Order: create containers first
(projects, milestones, epics), then move issues into them (under an epic: its UUID as `parentId`),
then relations, then statuses. Read back after the batch, not inline: a read straight after a write
can show the old state. Every moved, deferred, re-parented or canceled issue gets a one-line comment
naming why (`/tpm: off critical path for <milestone> — deferred`).

**Done when:** a re-read of the scope shows every approved row in its proposed state.

### 5. Close the loop

- **Pulse** every touched project (`save_status_update`): what moved, the new critical path, open
  questions for the human. Health from the evidence (C2), not optimism. Write dates unambiguously
  (`Oct-23`, never `10-23`).
- If the project description or PRD no longer matches the carve, update it through
  the Linear MCP.
- A skill, doc or rule the carve made stale (e.g. a moved project still named in a skill) is part of
  this pass, not a follow-up (C10).
- Launch each Delegate row the human approved, whether it sat under Will apply or Asks: start a
  fresh session on `/work plan <ISSUE>` for it, in the repo the issue names. This is the only way
  the TPM starts a build. Record its receipt line, `delegated <ISSUE> → <session id> · because
  <reason>`, in the pulse and the final message. A launch that fails is reported there and never
  blocks the pass. Move the launched issue and its unstarted parent epic to In Progress (C3) in the
  same pass, so the epic never sits in Todo while a session works its child.
- **Merging a loop's PR.** Before any `gh pr merge`, run the merge preflight in
  [`references/merge.md`](references/merge.md): it refuses a merge while an ask is open or a hand-back
  holds it. After the preflight passes, the same file covers auto-merge, the train and the
  `/close-out` grant that follows a TPM merge.
- Every state change you report to the human or a peer TPM (launched, merged, closed, folded) quotes
  its receipt (a comment id, a SHA, a session id); without one it is *attempted* or *proposed*.
  Every absence you report names its search and a positive control: "no yak matched" is only
  evidence if the same query finds a known one.
- A recurring yak watch follows [`references/yak-watch.md`](references/yak-watch.md): hot clusters
  by observation count as well as new arrivals.

**Done when:** each touched project has a pulse newer than the carve, every approved Delegate row
has a receipt line or a failure line, every merge has a preflight that found no hold, and the human
has the critical path in the final message.

## Decision rights

| Apply after the batch approval | Ask the human first, every time |
|---|---|
| Detach non-technical children from an epic; relate them instead (C1) | Set or change a project **goal, target date or milestone date** — if missing, ask for it (C7) |
| Todo ↔ Deferred by critical path, inside the stated objective (C3) | Pull **any** deferred, undecided or focus-paused scope into Todo or a cycle (C5) |
| Add missing blocked-by relations the scope makes explicit (C4) | Spin off a **fast-follow / sibling project**, or move scope or a milestone into any other project (C2) |
| Create the milestones the chains imply (names, order, membership) and the v-next backlog milestone (C6) | Milestone **dates**; deleting a milestone |
| In a focus-paused area: Todo → Deferred and clear the cycle; promote nothing (C5) | Move issues to **another team** (C9) — name the target team and the field losses; no fitting team → ask where |
| Mark superseded issues Duplicate with a chip to the survivor (C8) | Cancel work that is not clearly superseded |
| Close In Review children whose PR merged; move an epic to In Progress once any child is In Progress or In Review (C3); after a TPM merge of a clean loop PR, trigger `/close-out` on the loop session with `authorized: TPM merge <repo>#<n> <sha>` (profile `tpm-merge`) | Change an epic's or project's stated objective |
| Estimate unestimated children; raise a parent to the sum of its children (C11) | Lower an estimate someone set by hand, other than recording an actual |
| Comments, pulses, description refreshes | |
| Launch an approved **Delegate** row as a fresh `/work` session (a session cannot be recalled). Under a `/close-next` brief the review grant does not cover it: return the row as a question | Delegate a build whose issue fails a delegation guard (still to a `/work` session, never an `impl-*` subagent) |

A carve never invents a decision: when the evidence for a row is a guess, it is an ask row
(`eris ask`). **Recorded intent wins over a check**: an issue the project description, PRD or a
pulse names as committed (e.g. "Day-1 issues") is an ask row even when C3 says defer it.

## Shape vocabulary

- **Epic** — a parent issue holding *technical delivery only*: a contextual description (the arc as
  ordered chips, the exit bar, the PRD chip, an **External gates** section naming the business,
  legal or ops issues it waits on) and 2–3 implementation sub-issues per phase. One epic per phase
  or wave, sequenced by blocked-by.
- **Gate issue** — business development, legal, ops, a partner or a counterpart (one issue per host
  / counterparty). Stands alone, labelled with the team's business-development label where the team
  has one; any retired function labels are never applied. It `blocks` the slice(s) it gates, or the
  epic itself when it gates the epic's exit bar. Never a child of a technical epic; its own children
  (a ToS spike, a walkthrough) stay under it.
- **Lane** — one project. Each exit chain has exactly one **next item**: the unblocked Todo issue at
  the head of the chain. A lane with parallel exit chains lists each chain's head, ordered by
  milestone. A focus-paused lane has none.
- **Fast-follow** — a sibling project that takes non-essential scope (with its milestones) out of a
  swelling project, under the same initiative.

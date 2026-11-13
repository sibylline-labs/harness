# Linear constraints that shape a carve

What Linear does to structure when you move it or write its status. Read before any team move,
project split, milestone change, bulk re-parent, status write or label-group swap.

## Team moves

Source: Linear docs, "Move an issue to another team".

| Property | On move |
|---|---|
| Issue ID | **New** identifier. The old ID and URL keep resolving and redirect; old-ID search finds the issue. |
| Inline references (`ABC-123` in other descriptions) | Redirect when clicked; the text still shows the old ID. |
| Relations | Kept |
| Priority | Kept |
| Project | **Removed**, unless the destination team is added to the project *before* the move |
| Team labels | **Removed**; workspace labels stay. Re-apply the destination team's label by UUID. |
| Cycle | May be cleared. Into a team with auto-add-to-cycle an open issue lands in that team's active cycle (see Status writes). |
| Status | Mapped to the closest status; into a team with Triage, an open issue moved by an outsider lands in Triage |

So "moving teams breaks references" is false: decline a move on its merits, not on that. Before a
bulk move, add the destination team to the project, then re-apply labels and status by the
destination team's UUIDs (`/linear-workflow` Hard Rule 4).

## Milestones

The API cannot move a milestone between projects. Recreate it in the destination (`save_milestone`:
name, description, target date, order), move its issues, then delete or empty the original. Linear's
UI "convert milestone into project" is the manual equivalent for whole-milestone lifts.

## No critical-path label

A workspace usually has no critical-path or dependency label, and `/linear-workflow` Hard Rule 1
forbids creating one. The critical path is expressed as: `blocks` relations, plus Todo vs Deferred
status, plus milestone membership.

## Mentions create relations

Mentioning an issue in another issue's description auto-creates a **related** link. An epic's chip
list therefore relates every chip; that is fine for the arc, but a chip to a non-child (an external
gate) must carry the explicit `blocks` relation too, or it reads as merely related.

## Swapping an issue relation takes two calls

Observed: passing `removeBlocks: [X]` and `relatedTo: [X]` for the same target issue `X` in a single
`save_issue` call fails to update the relation until split into two separate calls. Unlike
single-select label swaps (`removeLabels` + `addLabels` below, which succeed in one call), Linear
stores at most one relation row per issue pair and does not sequence `removeBlocks` ahead of
`relatedTo` inside one `save_issue` payload.

- Send `save_issue(id: <source>, removeBlocks: [X])` first, then send a second
  `save_issue(id: <source>, relatedTo: [X])`.
- Inferred, not observed: the symmetric relation-type swaps on the same issue pair
  (`removeBlockedBy: [X]` + `relatedTo: [X]`, `removeRelatedTo: [X]` + `blocks: [X]` or
  `blockedBy: [X]`) share the same one-relation-per-pair constraint — split remove and add into two
  sequential `save_issue` calls there too.
- After the batch, re-read with `get_issue(includeRelations: true)` to confirm the old relation
  cleared and the new one landed.

## Status writes

Two behaviours of `save_issue` that each cost retries in a `/tpm` apply. After the batch, read each
issue back once (`get_issue`: `cycleId`, status) instead of trusting the response, and see "A
read-back can lag a write" below for why not inline.

**An active status adds the active cycle, and the add beats `cycle: null` in the same call**, on a
team with cycle automation "Auto-add active issues to current cycle" (Linear docs, "Cycles"). Setting
a status of type unstarted or started put the issue into the team's active cycle even when the call
also sent `cycle: null`. The same happens to an open issue moved into such a team. The setting is
per team, so on another team check `cycleId` after the first write before assuming it behaves the
same. To take an issue out of the cycle, write the status, then send a second `save_issue` with only
`cycle: null`.

This is also how a Deferred issue re-enters a cycle, besides cycle rollover and bulk edits. C5 checks
for it every pass; do not treat a Deferred issue in a cycle as a decision unless the human has said
so.

**Duplicate needs the relation first.** `state: <Duplicate UUID>` together with `duplicateOf` in one
call returns 400 ("only moved to a duplicate state when a duplicate issue relation exists"). Send
`duplicateOf: <identifier>` alone: Linear sets the team's Duplicate status itself.

## Single-select label groups

A workspace can define a label group set to single-select: `list_issue_labels` returns the child's
`parent` and `parentGroupType: singleSelect`. An issue carries at most one child of such a group.

**`addLabels` alone fails once the issue already has a label from the group.** `addLabels: [<new>]`
on an issue carrying a sibling returns 400 `The label '<old>' is in the same group as '<new>'. Only
one label in a group can be applied to an issue.`

**Swap in one call.** Send `removeLabels: [<old UUID>]` and `addLabels: [<new UUID>]` together in the
one `save_issue`: the response came back with the new child and no old one. Do not use `labels` for
it, which replaces the whole set.

- Read each issue's current label from `get_issue` before the batch. An issue with none needs only
  `addLabels`; do not guess the old label from its project.
- Inferred, not observed: a team move keeps a workspace-wide group's label, since workspace labels
  stay (see Team moves).

## A read-back can lag a write

Observed in a `/tpm` apply: the `save_issue` responses and an immediate `get_issue` returned the
pre-write state for four issues, so writes that had landed looked like silent no-ops. A re-read
afterwards showed all four.

- Write the whole batch, then re-read each touched issue once and compare against intent.
- A pre-write read straight after a write is not evidence the write failed. Re-read before retrying,
  and retry only what the second read still shows unwritten.
- A repeated status or field write is harmless. A repeated `patch` is not: per the `save_issue`
  schema its ops apply to the current content in order, so `append` and `insert_*` write their text
  twice, and a `replace` whose old text is already gone aborts the whole save.

## A parent created moments ago resolves by UUID

Observed: `parentId: ABC-123`, an issue created seconds earlier, failed with `Could not find issue
ABC-123 for parentId`; the same call with its UUID worked. When a carve creates a container and then
its children (containers first, as `/tpm` step 4 orders it), take the container's `uuid` from the
create result and pass that as `parentId`. Only `parentId` was seen failing this way; if `blocks`,
`blockedBy`, `relatedTo` or `duplicateOf` does the same on a fresh issue, use the UUID there too.

## A description patch can drop emphasis next to an issue chip

Observed: a `save_issue` `patch` that edited one unrelated acceptance-criteria line also rewrote
`**Delete** ABC-123**'s in-run daily re-search**` (an issue chip with a bold run starting at its
edge) and dropped the bold on that run. Patching the bold back stored literal `\*\*` instead. The
cause is not found.

- Leave bold and italics off any run that starts or ends at a chip. Unbolded text is the only form
  seen to hold.
- After a description patch on an issue with chips, `get_issue` and compare the lines around each
  chip with what they were, since the patch can change text outside its anchors. It can also turn
  chips into links: compare every chip, per the next section.
- If emphasis was dropped, accept the unbolded text: re-patching `**` stored literal asterisks.

## A description patch can turn chips into markdown links

Observed in a `/tpm` apply: `save_issue` `patch` ops on three issues rewrote chips **outside** the
patch anchors. Issue chips stored as `<issue id="…" label="ABC-123" href="…" />` came back as
a markdown link whose text is `ABC-123`, and document chips as markdown links: dead hyperlinks, no live title. Patching
them back to bare identifiers did not fix them; the next read showed a different set of chips as
links. The cause is not found.

- Before a `patch` on a description that carries chips, keep the `get_issue` description as the
  before-text.
- After the batch (see "A read-back can lag a write"), re-read and compare the chips, not just the
  patched lines: a markdown link to a Linear URL that the before-text did not have is a converted
  chip.
- Do not re-patch converted chips one by one: that flipped which chips were links instead of
  restoring them.
- Keep edits off the description when the change is not description content: a relation (`blocks`,
  `relatedTo`), a label, a status or a comment carries it without touching chips.
- To restore, send the whole description once as `description` (not `patch`), built from the
  before-text with the intended edit applied, chips in the self-closing `<issue … />` /
  `<document … />` form the read returned. Inferred, not observed: a full write was not tried. Read
  it back; if it converts too, leave the links (they still navigate) and say so in the apply report.

## Projects with several teams

A project can span teams; one is the lead team (decides project statuses). Splitting a project: the
fast-follow inherits the initiative(s) and lead team, gets its own goal and target date (ask), and
the original's description chips the fast-follow.

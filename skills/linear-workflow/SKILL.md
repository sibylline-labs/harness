---
name: linear-workflow
kind: workflow
description: >
  Creating, updating and managing Linear issues. Use when the user asks to file a ticket,
  create an issue/task/bug, add something to Linear or the backlog, or says work "should be
  tracked". Team, user, status and label IDs are read from Linear with the MCP before each
  write, never from memory; project status is confirmed before each write. How work is carved
  (a PM pass, breaking a PRD into issues, epics, critical path, re-scoping a project) is the
  tpm skill, which writes through this one.
---

# Linear Workflow

Every issue lands in a state where someone can pick it up without follow-up questions.

This skill files issues correctly. Deciding the *shape* — which epics, which milestones, what is on
the critical path, which project or team owns it — belongs to `/tpm`. A request to decompose a PRD
or plan into 3+ issues, run a "PM pass", or re-scope an epic or project starts in `/tpm`; it calls
back here for every write.

## The Two Acceptable Outcomes

Every issue this skill creates ends up in **exactly one** of these states:

1. **Fully formed** — owner, project, complete description, labels, estimate, priority. Lands in
   **Triage** (default) or the status the user explicitly asked for.
2. **Triage stub** — title + whatever context is available, in **Triage**, when any "fully formed"
   input can't be inferred or confirmed.

Supply everything, or leave it as a stub for human triage.

## Hard Rules

Non-negotiable — push back if the user asks otherwise.

1. **Use only existing labels.** Never call `create_issue_label`; never create labels by hand. If
   nothing fits, pick the closest or omit labels.
2. **Prove the project is open before writing to it.** Before any `save_issue` that sets a
   `project`, call `get_project` on that exact ID and read `status.type`: `started` / `planned` /
   `backlog` → fileable; `completed` / `canceled` → take the successor the project names (re-check
   it), else no project + Triage. Any project list you remember is a cache; this call is what makes
   the rule true.
3. **Default to Triage.** When in doubt, Triage. A team with no Triage status uses Backlog.
4. **Status and labels by UUID, read from the issue's own team.** Before the first write on a team,
   call `list_issue_statuses` and `list_issue_labels` for that team and use the UUIDs they return.
   IDs are team-specific: a foreign-team ID fails with `Workflow state not in same team as issue`
   or `Entity not found`. The MCP resolves status *names* by type then alphabetically, so
   "Canceled" can resolve to "Duplicate". Never hardcode an ID in a file; teams rename and retire
   statuses and labels.
5. **Status writes have side effects, and a read-back can lag; read the issue back once, after the
   batch.** Where a team auto-adds active issues to the current cycle, setting a status of type
   unstarted or started adds the issue to the active cycle even when the same call sends
   `cycle: null`: write the status, then send `cycle: null` alone. `state: Duplicate` together with
   `duplicateOf` returns 400: send `duplicateOf` alone. Passing `removeBlocks: [X]` and
   `relatedTo: [X]` in the same `save_issue` call fails to update the relation: send
   `removeBlocks: [X]` first, then `relatedTo: [X]` in a second call. A `save_issue` response, or a
   `get_issue` straight after it, can show the pre-write state of a write that landed: re-read
   before retrying. A parent created moments ago goes in `parentId` by its UUID; its identifier can
   fail with `Could not find issue … for parentId`. Detail: the `/tpm` skill's
   `references/linear-constraints.md`.

## Choosing the Team

Call `list_teams` once and pick the team that owns the **outcome**, not the repo the code lives in.
Tooling the product depends on but doesn't ship to users, product-facing work, reliability and
observability work, and business-side work each belong to different teams where the workspace has
them. A team's own description and existing projects are the evidence; read them.

- Teams for business, marketing, finance or operations work are for explicit requests only; an
  engineer's ticket does not go there.
- Genuinely ambiguous: ask. If the user can't be reached, use the workspace's default engineering
  team and file to Triage.

## Identifying the Current User

The default assignee is **the human operating this Claude instance**. Resolve them with `whoami`
(or match their email from CLAUDE.md / context against `list_users`). Not found → leave the
assignee blank, route to Triage, and say so. If the user names someone else, use that person.

## Workflow Decision Tree

1. **Team** — pick it (above) and read its statuses and labels (Hard Rule 4). Can't tell → the
   default engineering team + Triage.
2. **Project** — best match from `list_projects` for that team, then `get_project` per Hard Rule 2.
   A close name match to a closed project is a reason to run the check, because the project names
   its successor. Nothing fits → no project + Triage.
3. **Owner** — current user if it's their work; the named person if named; the project lead if
   obvious; otherwise none + Triage.
4. **Description** — enough context → full Context/Scope/AC (below); otherwise title-only stub +
   "needs scoping" note + Triage.
5. **Labels** — from the team's `list_issue_labels`; no good fit → omit.
6. **Estimate** — hours of active time, snapped to the scale; a parent is never below the sum of
   its children. See [Estimates](#estimates).
7. **Priority** — 1 Urgent (blockers), 2 High, 3 Normal (default), 4 Low.
8. **Status** — the team's Triage UUID, unless the user said otherwise.

Items 2–6 not confidently fillable → Triage stub; never invent context, a project, or a stretched
label.

## Estimates

**1 point = 1 hour of active time**: inference plus human attention on the work. Time the session sat
idle while the human was elsewhere doesn't count, because it isn't wall time. Estimates feed a
regular "we thought X, it was Y" calibration, so the unit has to stay the same from filing to close.

- **Scale:** `1, 2, 4, 8, 16`. Linear quantizes anything else (`3` → `4`), so pass a scale value.
  Under an hour → `1`. Unsure → `2`. Above 16, write `32` and read it back. If Linear stores
  something else, keep what it stored and put the true hours in the receipt.
- **Parent floor:** an issue with sub-issues (an `[EPIC]` or any other parent) has an estimate
  **≥ the sum of its children's estimates**, snapped *up* to the next scale value. Integration and
  review overhead can sit above the floor; nothing sits below it. Estimate unestimated children
  first. Re-check the floor whenever a child is added or re-estimated, or an actual lands at
  close-out, and raise the parent in the same pass. Raising a parent to its floor never needs to ask.
- **Actuals at PR / close-out:** when work ships, the issue's estimate is overwritten with what it
  actually took, measured and never recalled:

  ```bash
  uv run --script "$HOME/.claude/skills/linear-workflow/scripts/active_time.py" \
    --issue <KEY> --current [--session <id> ...]
  ```

  It sums transcript time on the issue's branch plus the named sessions, drops any gap over 15 min
  as idle, and counts parallel subagents once (`active_h`). Pass `--current` always, and `--session`
  for any earlier session that worked the issue on `main`. `--current` needs
  `CLAUDE_CODE_SESSION_ID`. It prints `points` already snapped. A transcript another session deleted
  mid-scan is skipped, not fatal; the output names the count (`skipped`) when it is nonzero. Write
  `points` to `estimate`, then (in the same pass) propagate the parent floor.
- **The receipt is the dataset.** Overwriting `estimate` erases the original, and Linear keeps no
  estimate history the MCP can read. So every actual write posts this exact line in an issue comment
  (the close-out ledger, the PR-open comment, or on its own):

  ```
  effort: est <old points|none> → actual <new points> (active <h>h, agent <h>h, gap 15m, sessions <n>)
  ```

  Keep the format fixed so the calibration pass can `list_comments` and regex it. On a parent, add
  `children <sum>` so a floor bump isn't read as a miss. `est` is always the estimate from before
  the *first* actual: when the issue already has an `effort:` line (written at PR open, re-measured
  at close-out), copy its `est` forward rather than the provisional number now in the field.

## Writing the issue

Descriptions, chips (mentions) and epic structure live in
[`references/descriptions.md`](references/descriptions.md): read it before the first `save_issue`
that carries a description, links another Linear resource, or creates a parent `[EPIC]` with
slices.

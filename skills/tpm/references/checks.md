# TPM checks

Twelve checks, run all twelve on every pass. Each is a Linear observation, not a judgement call: the
**Observe** line is the query, **Violation** is what counts as a finding, **Fix** is the default
carve. The **Why** line is the correction a human would otherwise make by hand.

Status names differ by team: one team's off-path status is **Deferred**, another's is
**Deprioritised**. "Deferred" below means whichever the issue's team has.

## C1 — Epic purity

**Why:** an epic is reserved for the technical delivery work it names. Deal, filing and comms tasks
inside it distort its progress.

- **Observe:** children of every issue labelled `Epic` or titled `[EPIC]`; their labels.
- **Violation:** a gate issue sitting as a child: one whose scope is a deal, filing, registration,
  contract or comms task. Scope decides, not the label: it may carry the team's business-development
  label, a retired function label from before the retirement, or none. Also: an epic with one child,
  or more than ~6 direct children in one phase (too dense to execute against); a phase carried in a
  title prefix (`W1`, `Phase 2:`) instead of `parentId`. Too dense means more than ~6 direct
  children, or two or more independent sub-chains in one epic.
- **Fix:** detach the child (its own children stay under it); leave it standalone with the team's
  business-development label if it has one (never a retired label) and a `blocks` relation to what
  it gates (see Gate issue in SKILL.md); add or update the epic's **External gates** section. Split
  a dense epic per phase or per independent sub-chain; one issue per external counterpart.
  Non-delivery children (retro requests, review containers) are detached and related too.

## C2 — Project swell and seams

**Why:** non-essential work belongs in a fast-follow project with its own milestones and deadlines;
a project that keeps swelling ends up tracking two different seams on one surface.

- **Observe:** per project, issues created vs completed over the last two cycles (ISO weeks when
  cycle history is unavailable or the project is younger than that); open issues outside any
  milestone; distinct repos / surfaces the open issues touch; project health in the latest pulse.
- **Violation:** creation outpacing completion for two cycles; open scope that no milestone before
  the target date needs; open scope past a passed target date; two separable seams (different repos,
  different users, different exit bars) in one project.
- **Fix (ask first):** move the scope into an existing fast-follow under the same initiative if
  there is one, else propose a new one, taking whole milestones with it (see
  `linear-constraints.md` — milestones are recreated, not moved).

## C3 — Critical path decides status

**Why:** work that doesn't need to sit on the critical path is deferred, so Todo stays focused.

- **Observe:** the blocked-by graph from each milestone's exit issue backwards; status of every issue
  on and off that chain; In Review issues whose linked PR is merged; each epic's status against its
  children's.
- **Violation:** a Todo issue not on any open milestone's chain; a Deferred / Backlog issue the chain
  needs; a lane with zero or several equally "next" items; an In Review issue whose PR merged; an
  epic still in Todo, Backlog or Deferred while a child is In Progress or In Review, so it jumps
  from Todo to Done and the board hides live work.
- **Fix:** on-path → Todo, off-path → Deferred; name the single next item per lane; close merged In
  Review issues to Done; an epic with a child In Progress or In Review → In Progress, and never back
  to Todo while a started child is open.

## C4 — Blocking is modelled

**Why:** nobody should have to click through issues to understand what is blocking what.

- **Observe:** `blocks` / `blocked by` relations; descriptions that say "after", "once", "depends
  on", "needs", "requires" next to an issue chip; epic→epic ordering.
- **Violation:** a dependency stated in prose with no relation; consecutive phase epics with no
  epic→epic `blocks`; a gate issue with no relation to what it gates; a cycle in the graph.
- **Fix:** add the relation; there is no critical-path label, so relations plus status plus
  milestone *are* the critical path.

## C5 — The sprint holds one objective

**Why:** a deferred item that quietly re-enters a sprint, with no recorded decision, undoes the
deferral.

- **Observe:** the current cycle's issues; the stated objective (the focus statement, project goal,
  the user's words this session); issues the human moved to Deferred and when.
- **Violation:** a cycle issue serving no stated objective; a Deferred issue that has re-entered a
  cycle or Todo without a recorded decision; focus-paused work promoted.
- **Fix:** propose its removal from the cycle. Re-promoting deferred scope is always an ask row.
  Deferred issues the human keeps in a cycle on purpose ("they serve a separate purpose") stay — ask
  once, then record the answer in the pulse.

## C6 — Milestones are complete and sequenced

**Why:** every open issue belongs to the right milestone, and the milestones are in a sensible
order.

- **Observe:** project milestones, their target dates and order; each open issue's milestone;
  blocked-by edges that cross milestones.
- **Violation:** an open issue with no milestone; an issue in an earlier milestone blocked by one in
  a later milestone; milestones with no target date; no home for v-next scope.
- **Fix:** assign to the milestone its chain implies; add a final `v-next backlog` milestone for
  deliberate later scope; propose dates (ask).

## C7 — Goal and deadline exist

**Why:** governance over goals, milestones and deadlines is part of the scope. An undefined goal is
an input to ask for, then set.

- **Observe:** project `summary`, description goal line, `targetDate`, lead.
- **Violation:** any of them missing or contradicting the latest PRD.
- **Fix:** always an ask row: ask, with a recommended goal drawn from the PRD.

## C8 — Supersede, absorb, or reference

**Why:** new scope must properly supersede, absorb or reference scope that is already there.

- **Observe:** for each new or proposed issue, and each Todo issue in scope, a `list_issues` text
  search on its key nouns across the team(s) and sibling projects under the same initiative, open
  and recently closed.
- **Violation:** two open issues with the same deliverable; a new issue that restates an older one
  without a relation; a PRD change that obsoletes open issues still in Todo.
- **Fix:** mark the loser `Duplicate` with a chip to the survivor, or absorb its AC into the
  survivor and relate them.

## C9 — Work lives with its owning team

**Why:** the team that owns the outcome owns the issue, wherever the code happens to live.

- **Observe:** each issue's team vs the team that owns its *outcome* (`/linear-workflow` "Choosing
  the Team"; business-development, legal and ops outcomes belong to a business team, not
  engineering).
- **Violation:** tooling work in the product team; product work in the tooling team; business work
  in an engineering team.
- **Fix (ask first):** move, after reading `linear-constraints.md` § Team moves. The repo the code
  lives in never decides the team. When no team in the workspace owns the outcome, the row asks the
  human where it lives; never pick a team the workspace does not have.

## C10 — Comms and collateral follow the carve

**Why:** a changed project description or a new PRD deserves a new pulse, and every skill or doc
that names the old shape needs updating in the same pass.

- **Observe:** latest pulse date vs the latest structural change; project description vs the
  current milestones and epics; skills, docs and rules that name a moved or renamed project, epic or
  team (`rg` the harness for the old name).
- **Violation:** a structural change with no newer pulse; a description describing the pre-carve
  shape; a skill or doc naming the old home.
- **Fix:** pulse, refresh the description, and update the stale skill/doc in the same pass.

## C11 — A parent's estimate covers its children

**Why:** an issue with sub-issues must not carry an estimate below the sum of its sub-issues'
efforts.

- **Observe:** for every issue with sub-issues, its `estimate` and the sum of its direct children's
  estimates (`list_issues parentId=<key> fields=[estimate]`); children with no estimate.
- **Violation:** a parent estimate below the children's sum; an unestimated parent with estimated
  children; unestimated children under a parent being carved.
- **Fix:** estimate the children (hours of active time, `/linear-workflow` § Estimates), then raise
  the parent to the sum snapped up to the scale. Never lower a child to fit the parent.

## C12 — Every code-fix row names its rung

**Why:** a gap list that sizes each gap as a patch skips the question that matters: what makes the
defect's *class* fail?

- **Observe:** every issue in scope (or row in the diff) that fixes or prevents a code defect, and
  whether its description or AC names the rung that will make the defect's *class* fail, per the
  `test-driven-development` ladder: architecture → type → lint (built-in, then ast-grep) →
  boot/import check → behaviour test → docs.
- **Violation:** a code-fix row sized or ranked with no rung; an AC that only says the instance is
  fixed ("refuse X at mint") with no red-first artifact (a rule ID, type, boot assertion or test
  name); a rung lower than one the class fits (a test where a type or boot check would hold it).
- **Fix:** add a `rung` column to the diff table and a first AC line naming the artifact and that it
  is seen red on the unfixed tree. Re-size the issue after the rung is named, since the rung often
  changes the scope. A claim made to a third party (a pitch, a one-pager) cites the rung's artifact,
  not only the ticket.

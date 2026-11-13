---
name: prd-review
kind: gate
description: Pre-carve adversarial audit of a PRD or RFC — checks observed substrates vs inferred decisions, Gate-0 walking-skeleton blockers, derive-don't-restate and deletion inventories, invariant enforcement rungs, boundary-testing spike ACs, and decision-register one-way doors before locking decisions or carving Epics in /tpm.
---

# PRD Review

Audit a drafted or updated PRD / RFC in the main agent loop before locking its decision register, recording it in Socrates, or carving it into Epics with `/tpm`. Surface ceremony (having a decision table, Mermaid diagrams, or a `## Non-goals` heading) predicts nothing about delivery churn; delivery is governed by the five structural checks below. Worked examples live in [`references/evidence-and-examples.md`](references/evidence-and-examples.md).

## Step 0 — Check for an Existing `## PRD Review` Section (Run Once)

Before running the audit, inspect the PRD for an existing `## PRD Review` section:

- **Present and marked `Approved` without open issues:** **Stop.** Do not run `/prd-review` again. Read the section, note any recorded guidance and steering for downstream carving or implementation, and continue with the caller's loop (`/tpm` or `/work plan`).
- **Absent or marked unapproved (`Changes Requested`):** Run Steps 1–5 below and record the outcome in `## PRD Review` at the end of the PRD.

**Done when:** either an existing `Approved` review section's steering notes are loaded into context (and Steps 1–5 are skipped), or the PRD is confirmed ready for its first review pass.

## Step 1 — Observed Substrate & Scale Baseline

Extract every decision and architecture claim that depends on how an external API, chain precompile, browser/host iframe (CSP and `Permissions-Policy` of the embedding host), or internal framework or runtime behaves, plus every codebase scale claim.

1. **Observed substrate:** For every checkable claim, run or cite a live probe (`eth_call`, endpoint fetch, `rg`/AST count, `main` SHA + date) directly in the PRD's `## Context` or `## Interface` section.
2. **Gate-0 binding:** Any substrate claim that requires a deployed Worker or host harness to observe cannot be locked as an unconditional decision — bind it to a **Gate-0 Walking Skeleton or Spike** (Step 2) and write the fallback path if the probe inverts.

**Done when:** every external, runtime, and scale claim in the PRD is listed with either its cited live observation (`SHA / command → reading`) or its blocking Gate-0 issue ID; zero inferred substrate claims remain locked as unconditional decisions.

## Step 2 — Walking Skeleton & Boundary-Testing Spike ACs

1. **Walking skeleton (`Deliverable #1 / Gate 0`):** Identify the single highest-risk unconfirmed end-to-end premise and make it Deliverable #1, with downstream implementation Epics carrying `blockedBy` on it.
2. **Host/consumer boundary ACs:** Audit every `[SPIKE]` in the PRD. Its acceptance criteria must exercise the **real end-to-end user or host boundary** (e.g. a browser passkey claim in the host iframe, execution inside a real consumer repo with its hooks active) rather than only backend REST mechanics, and must treat **falsification** ("premise inverted → amend decision `Dn` to fallback Y") as a first-class passing outcome.

**Done when:** Deliverable #1 is named with its downstream `blockedBy` fan-out, and every spike's AC specifies both the end-to-end host/consumer boundary it probes and the decision amendment if falsified.

## Step 3 — "Derive, Don't Restate", Deletions, Enforcement Rungs & Derived Authority

1. **Derive, don't restate:** Challenge every proposed annotation, config list, or side-by-side metadata store. Wherever the fact already exists in types, AST call sites, or a single code funnel, derive it rather than maintaining a parallel declaration.
2. **Deletion & supersession inventory:** Require an explicit table naming (a) exact code paths, flags, routes, or `ast-grep` rules deleted in the same change, and (b) exact prior PRD decision IDs or Socrates entries superseded. Any transitional fallback must state a code-observable deletion trigger.
3. **Invariant enforcement rungs:** Every domain invariant, security boundary, or state-machine completion requirement ("every account owes a signing key before onboarding completes", "workers own byte-level crypto") must name the **Enforcement Rung** (`Architecture / Type Funnel → Lint Rule → Boot/State Gate`) that makes violating it impossible — never prose alone.
4. **Derived authority:** Every role, scope or entitlement the PRD copies from an external identity (an IdP flag, a tracker `admin`, a token claim) gets a row in a **Derived Authority** table: every source field it is computed from, its refresh trigger (`insert only`, `every sign-in`, `webhook`), its revocation path (what demotes or removes it, and when) and its enforcement rung. A mapping such as "tracker admin → our admin" is not a row: it names one source and no lifecycle. On a tier-1 surface (auth, accounts, billing, signing), a missing table or a missing cell is **BLOCKING**, and so is a refresh trigger of `insert only` with no stated reason. Write it as a finding, never as a question.

| Authority | Source fields | Refresh trigger | Revocation path | Enforcement rung |
|---|---|---|---|---|
| `members.role = admin` | IdP `viewer.admin`, `viewer.owner` | every sign-in | sign-in after losing both flags sets `member` and emits `member.role_changed` | `Org.join` funnel; `principal.role` read per request |

**Done when:** the PRD contains an Invariant → Enforcement Rung table, a What Gets Deleted / Superseded inventory (or an explicit "greenfield: nothing superseded"), and a Derived Authority table with every cell filled (or an explicit "no authority derived from an external identity").

## Step 4 — Day-0 Contracts, Multi-Consumer Seams & Estate Hygiene

1. **Shared platform seams:** When $\ge 2$ products, workers, or consumers touch a surface (auth, token leases, rate limits, billing, Durable Object quotas), place the shared seam in Gate 0 / Milestone 1 rather than embedding it inside one product Worker and deferring extraction.
2. **Day-0 contract & fake:** When $\ge 2$ implementation lanes run in parallel across services, specify a Day-1 typed contract package (RPC entrypoint types / schema / OpenAPI) **plus an in-memory fake**.
3. **Estate hygiene:** Every new repo or Worker includes CI, the repo's governance config linted strictly, and route-level auth + rate-limit posture in Milestone 1.

**Done when:** shared seams with $\ge 2$ consumers, parallel-lane contract fakes, and Day-0 CI/governance-config/rate-limit posture are assigned to Gate 0 / Milestone 1.

## Step 5 — One-Way Doors & Bounded Open Questions

Audit every row of the PRD's decision register and Open Questions list:

1. **One-way doors only:** Keep only irreversible, cross-boundary decisions (security model, system of record, wire/schema contract, public product promise).
   - *Two-way operational practices* (team hygiene, dogfood budgets, cutover posture) → move to the project's **Practices** doc.
   - *Temporary choices* (`"until X"`, `"for Phase 1"`) → move to Milestone scope.
   - *Facts owned by another artifact* (lockfiles, `wrangler.jsonc`, CI config) or *module-local implementation details* → remove from the register.
2. **Conflicts & supersessions:** Flag any contradiction with another project's locked PRD or Canon as an explicit **Conflict** or **Supersession** row citing both authoritative sites.
3. **Bounded open questions:** Never force false certainty by closing open questions prematurely. Keep genuine unknowns open and bind each one to the specific spike, lane, or milestone that resolves it (*"Resolve in the auth spike before M2"*).

**Done when:** every surviving register row is a true one-way door, two-way practices and conflicts are separated, and every open question names its resolving spike or milestone.

## What This Review Never Flags

Empirical non-predictors — do **not** add churn by policing these:
- Presence or exact naming of boilerplate headings (`## Non-goals`, `## Milestones`) when the content is already clear.
- Word-count floors or ceilings: long and short PRDs both deliver when their structural checks hold.
- Having open questions at PRD lock, provided each is bounded to a resolving spike or milestone.

## Output — Append `## PRD Review` & Route Substantial Issues

Upon completing the first review, append a `## PRD Review` section to the bottom of the PRD:

1. **When Approved (clean, or minor/self-contained adjustments folded in):**
   Append `## PRD Review` with `**Status:** Approved`, the 5-row scorecard below, and a concise **Guidance & Steering** list for downstream `/tpm` and implementation agents. Future `/tpm` or planning passes that see `**Status:** Approved` read the steering notes and skip re-running `/prd-review`.
2. **When Substantial Changes or Issues Exist:**
   **Spare the PRD inline details and prose.** Append a brief `## PRD Review` section (`**Status:** Changes Requested — See review issue` plus 2–3 bullets naming the blocking themes), open a review issue for this PRD (a Socrates review issue when the org enrols it), and put the full thoughts, trade-offs, and detailed commentary there rather than bloating the PRD document or carving Epics prematurely.

| Step | Verdict (`PASS` / `AMENDED` / `BLOCKING`) | Summary / Steering note |
|---|---|---|
| 1. Observed substrate & scale baseline | … | … |
| 2. Walking skeleton & boundary spike ACs | … | … |
| 3. Derive-don't-restate, deletions, rungs & derived authority | … | … |
| 4. Day-0 contracts, shared seams & hygiene | … | … |
| 5. One-way doors & bounded open questions | … | … |

## Rubrics the review leans on

The plan a PRD turns into is judged later by `plan-shape@1` (`/plan-review`), and the delivered change by `user-impact@1` and `unit-test-admission@1` (`verification-before-completion`). A PRD that names its one-way doors, its enforcement rungs and the evidence each user-impact class needs gives those gates something to check.

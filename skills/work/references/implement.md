# Stage: implement

You are tasked with implementing an approved technical plan(s) (the `work` implement stage) from the current continuity ledger. These plans contain phases with specific changes and success criteria.

## CRITICAL: Plans Are Intent, Not Copy-Paste Source

Plan code blocks show WHAT to build. The CODEBASE shows HOW to build it.

Before implementing any task:
1. Read the reference implementations cited in the plan header
2. Match their conventions (enums, typed models, logging, error handling)
3. If the plan code diverges from codebase patterns, follow the codebase

**If a hook blocks your code, that's a signal.** Read the existing code to find the right pattern — don't fight the linter.

## Execution Modes — Divide by Context, Not Problem Type

Fold planning, gate reviews (`/premise-gate`, `/plan-review`), and small or tightly coupled sequential changes into the **main agent loop**. The agent that authored and gated the plan already holds the shared context and can revise the plan mid-turn without lossy "telephone game" handoffs. Spawn subagents only when **dividing by context** earns the separate window:

### Mode 1: Direct Implementation in the Main Loop (Default for 1–3 tasks or tightly coupled edits)
- Implement each phase directly in the main loop when phases share the same files/context or total $\le 3$ tasks.
- When committing per phase, commit each phase as soon as its gate goes green, before editing shared files for the next phase; when tightly coupled phases share files and are built red-to-green together, make a **single commit** covering the coupled phases rather than reconstructing intermediate file states by hand from snapshots or hunks (`git add -p` and `git rebase -i` are interactive and unavailable to an agent).
- Revise the plan in place as findings arrive; still run `verify-adversarial` as the fresh-context black-box gate before opening the PR.

### Mode 2: Agent Orchestration (For 4+ independent phases with clean interfaces)
- When a plan has 4+ distinct phases with clean boundaries and a single loop would hit context bloat, act as a thin orchestrator and dispatch each phase to its surface `impl-*` agent with a fresh context window and compact handoff.
- Use `Explore` / `research-agent` for parallel read-only lookups and `verify-adversarial` for black-box verification.

---

## Getting Started

When given a plan path:
- Read the plan completely and check for any existing checkmarks (- [x])
- Read the reference implementations cited in the plan header
- Read the original ticket and all files mentioned in the plan
- **Read files fully** - never use limit/offset parameters, you need complete context
- Think deeply about how the pieces fit together
- Create a todo list to track your progress
- Start implementing if you understand what needs to be done

If no plan path provided, ask for one.

## Implementation Philosophy

Plans are carefully designed, but reality can be messy. Your job is to:
- Follow the plan's intent while adapting to what you find
- Implement each phase fully before moving to the next
- Verify your work makes sense in the broader codebase context
- Track progress in your todos and the continuity ledger, never in the plan file (see below)

**The reviewed plan is frozen.** `/plan-review` records a `gate-receipt@v1` that binds the plan's
sha256, and the loop's `eris gate check` reports `drift` (exit 3) if a single byte changes, checkboxes
included. Do not edit the plan while implementing. If reality forces a design change, say so, amend the
plan, commit and push the amendment as a new commit, and re-run `/plan-review`, which records a fresh receipt.

**Accrue on the issue's single draft PR.** The `plan` stage already pushed the
branch and opened the issue's draft PR (`gh pr create --draft`). Push implementation commits to that
same branch and PR — never open a second PR for the issue in the same repo, and never rebase or force-push the branch
after a gate receipt is recorded (`refs/pull/<N>/head` keeps every receipted commit SHA reachable
after squash merge and branch deletion). When an issue spans multiple PRs (for example `cross-repo` work), only the final PR that completes `<KEY>` writes `Closes <KEY>` in its body (`type: "closes"`); every contributing PR starts its body with `Part of <KEY>` and attaches in Linear as `contributes`. `final-gates` flips the draft PR ready (`gh pr ready`)
when the profile check exits 0. On a **`linear-only`** run (no git repo diff), there is no draft PR and no git commit: execute the planned Linear or operator-file writes in the main loop, verify each write by reading the live record back, and leave `$G/plan.md` frozen.

When things don't match the plan exactly, think about why and communicate clearly. The plan is your guide, but your judgment matters too.

If you encounter a mismatch:
- STOP and think deeply about why the plan can't be followed
- Present the issue clearly:
  ```
  Issue in Phase [N]:
  Expected: [what the plan says]
  Found: [actual situation]
  Why this matters: [explanation]

  How should I proceed?
  ```

## Verification Approach

After implementing a phase, run the FULL verification suite — not just the phase's success criteria.

**The repo's own commands win.** When the target repo declares its verification (an `AGENTS.md` / `CLAUDE.md` command list, or `ci.local` gates in its root `eris.yaml`), run those commands, in the repo's order, and skip the block below. The block is the default for a Python repo with no such declaration; it does not apply to a Go, Nx or yarn repo.

```bash
# 1. Run the full test suite (not just changed tests)
pytest tests/unit/ -x -v

# 2. Lint all changed files
uv run ruff check --fix .
uv run ruff format .

# 3. Type check changed files
uv run ty check <changed_files>

# 4. AST-grep scan all PR-touched files (not just the focal module)
ast-grep scan <all_changed_files>
```

**Verification scope = the PR, not the plan task.** Run the repo's checks (for the default block: ast-grep/ruff/ty) across ALL files touched in the branch, not just the module you just edited. Adjacent files in the same PR can have violations too.

After automated verification:
- Fix any issues before proceeding
- Update your progress in your todos and the continuity ledger (not the plan, which is frozen)
- **Pause for human verification**: After completing all automated verification for a phase, pause and inform the human that the phase is ready for manual testing

If instructed to execute multiple phases consecutively, skip the pause until the last phase. Otherwise, assume you are just doing one phase.

do not mark manual testing steps done in your todos until confirmed by the user.


## If You Get Stuck

When something isn't working as expected:
- First, make sure you've read and understood all the relevant code
- Consider if the codebase has evolved since the plan was written
- Present the mismatch clearly and ask for guidance

Use sub-agents for clearly defined tasks: implementing a phase, running tests, fixing lint. The main context stays clean; sub-agents do the heavy lifting.

**Dispatch each implementation phase to the implementation agent for the surface** (`impl-generic`,
or your harness's repo-specific `impl-*` agent). They preload the spine, the language skills and the
toolchain, so you hand them task context — not a wall of pasted skills. Give each a task, a
reference implementation to mirror, the files to read fully, and its handoff path.

## Resuming Work

If the plan has existing checkmarks:
- Trust that completed work is done
- Pick up from the first unchecked item
- Verify previous work only if something seems off

Remember: You're implementing a solution, not just checking boxes. Keep the end goal in mind and maintain forward momentum.

---

## Agent Orchestration Mode

When implementing larger plans (4+ tasks), use agent orchestration to stay compaction-resistant.

### Why Agent Orchestration?

**The Problem:** During long implementations, context accumulates. If auto-compact triggers mid-task, you lose implementation context. Handoffs created at 80% context become stale.

**The Solution:** Delegate implementation to agents. Each agent:
- Starts with fresh context
- Implements one task
- Creates a handoff on completion
- Returns to orchestrator

Handoffs persist on disk. If compaction happens, you re-read handoffs and continue.

### Setup

1. **Create handoff directory:**
   ```bash
   mkdir -p thoughts/handoffs/<session-name>
   ```
   Use the session name from your continuity ledger.

2. **Read the implementation agent's definition** (`agents/impl-generic.md`, or the repo-specific
   agent you dispatch) so the handoff you ask for matches the one it writes.

### Pre-Requisite: Plan Review Gate (Main Loop, Run Once)

Before implementing, check the plan for an existing `## Gate Amendments (premise-gate + plan-review)` section:
- **Already present with verdict `PASS`:** Note any recorded constraints or steering and proceed directly without running `/premise-gate` or `/plan-review` again.
- **Absent, incomplete, or without a `**Verdict:** PASS` line:** Load and run `/premise-gate` and `/plan-review` (the skills themselves, not a section written from memory) directly in the main loop (never via a separate validator subagent or `validation-*.md` handoff file) and fold any required amendments into the plan before dispatching implementation phases.

### Orchestration Loop

For each task in the plan:

1. **Prepare agent context:**
   - Read continuity ledger (current state)
   - Read the plan (overall context)
   - Read previous handoff if exists (from thoughts/handoffs/<session>/)
   - Identify the specific task
   

2. **Dispatch to the implementation agent for the surface.** `impl-generic` discovers the repo's
   stack and CI gate for itself; if your harness defines a repo-specific `impl-*` agent for the
   surface, use that one instead. You supply task context, not pasted skills:

   ```
   Agent(
     subagent_type="impl-generic",   # or the repo-specific impl-* agent for this surface
     prompt="""
     ## Your Task
     Task [N] of [Total]: [Task description from plan]

     ## Reference implementation (mirror it)
     [path/to/sibling] — [the convention to follow]

     ## Invariants this phase introduces
     [the phase's rows from the plan's "Invariants and Their Rung" table, verbatim, or "none".
      Hold each at its named rung or higher; never prescribe a test for a lint or type row.]

     ## Read first (fully)
     - Plan phase [N] section
     - Previous handoff: thoughts/handoffs/<session>/task-<N-1>-*.md (or "first task")

     ## Handoff
     thoughts/handoffs/<session-name>/task-[NN]-[short-description].md
     """
   )
   ```

   Each agent names its own CI gate as its definition of done and creates the handoff on
   completion. Choose the agent by `subagent_type` and **never pass a model on the call**: an
   override runs the other model at this agent's pinned effort.

   **Raise effort per phase, never lower it.** Pass `effort: "high"` on the call when the phase
   touches a substrate (schema, auth, a contract, a cross-repo seam) or edits many files across
   modules; otherwise omit it and the agent runs at its pinned effort.

   **Never leave `subagent_type` unset.** An unset type silently resolves to `general-purpose`,
   which inherits this session's model. If no surface-specific agent fits, the answer is
   `impl-generic`, not the default.

   **A phase a lighter-tier agent implemented must pass a review gate, and that gate is never
   skipped.** Before the PR, run `verify-adversarial` over every phase built on a lighter tier, and
   record in the PR which phases those were.

3. **Process agent result:**
   - Read the agent's handoff file
   - Update ledger checkbox: `[x] Task N` (never the plan's: it is frozen)
   - Continue to next task

4. **On agent failure/blocker:**
   - Read the handoff (status will be "blocked")
   - Present blocker to user
   - Decide: retry, skip, or ask user
   

### Recovery After Compaction

If auto-compact happens mid-orchestration:

1. Read continuity ledger (loaded by SessionStart hook)
2. List handoff directory:
   ```bash
   ls -la thoughts/handoffs/<session-name>/
   ```
3. Read the last handoff to understand where you were
4. Continue spawning agents from next uncompleted task

### Example Orchestration Session

```
User: /work implement thoughts/shared/plans/PLAN-add-auth.md

Claude: I'll use agent orchestration for this plan (6 tasks).

Setting up handoff directory...
[Creates thoughts/handoffs/add-auth/]

Task 1 of 6: Create user model
[Spawns agent with full context]
[Agent completes, creates task-01-user-model.md]

✅ Task 1 complete. Handoff: thoughts/handoffs/add-auth/task-01-user-model.md

Task 2 of 6: Add authentication middleware
[Spawns agent with previous handoff]
[Agent completes, creates task-02-auth-middleware.md]

✅ Task 2 complete. Handoff: thoughts/handoffs/add-auth/task-02-auth-middleware.md

--- AUTO COMPACT HAPPENS ---
[Context compressed, but handoffs persist]

Claude: [Reads ledger, sees tasks 1-2 done]
[Reads last handoff task-02-auth-middleware.md]

Resuming from Task 3 of 6: Create login endpoint
[Spawns agent]
...
```

### Handoff Chain

Each agent reads previous handoff → does work → creates next handoff:

```
task-01-user-model.md
    ↓ (read by agent 2)
task-02-auth-middleware.md
    ↓ (read by agent 3)
task-03-login-endpoint.md
    ↓ (read by agent 4)
...
```

The chain preserves context even across compactions.

### When to Use Agent Orchestration

| Scenario | Mode |
|----------|------|
| 1-3 simple tasks | Direct implementation |
| 4+ tasks | Agent orchestration |
| Critical context to preserve | Agent orchestration |
| Quick bug fix | Direct implementation |
| Major feature implementation | Agent orchestration |
| User explicitly requests | Respect user preference |

### Tips

- **Keep orchestrator thin:** Don't do implementation work yourself. Just manage agents.
- **Trust the handoffs:** Agents create detailed handoffs. Use them for context.
- **One agent per task:** Don't batch multiple tasks into one agent.
- **Sequential execution:** Start with sequential. Parallel adds complexity.
- **Update ledger:** After each task, update the continuity ledger checkbox.
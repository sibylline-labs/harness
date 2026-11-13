# Stage: plan

You are tasked with creating detailed implementation plans (the `work` plan stage) through an interactive, iterative process. The plan you write is judged against `plan-shape@1` ([`plan-shape`](../../plan-shape/SKILL.md)) by `/plan-review`. You should be skeptical, thorough, and work collaboratively with the user to produce high-quality technical specifications.

## Initial Response

When this command is invoked:

1. **Check if parameters were provided**:
   - If a file path or ticket reference was provided as a parameter, skip the default message
   - Immediately read any provided files FULLY
   - Begin the research process

2. **If no parameters provided**, respond with:
```
I'll help you create a detailed implementation plan. Let me start by understanding what we're building.

Please provide:
1. The task/ticket description (or reference to a ticket file)
2. Any relevant context, constraints, or specific requirements
3. Links to related research or previous implementations

I'll analyze this information and work with you to create a comprehensive plan.

Tip: You can also invoke this command with a ticket file directly: `/work plan thoughts/shared/tickets/abc-123.md`
For deeper analysis, try: `/work plan think deeply about thoughts/shared/tickets/abc-123.md`
```

Then wait for the user's input.

## Process Steps

### Step 1: Context Gathering & Initial Analysis

1. **Read all mentioned files immediately and FULLY**:
   - Ticket files (e.g., `thoughts/shared/tickets/abc-123.md`)
   - Research documents
   - Related implementation plans
   - Any JSON/data files mentioned
   - **IMPORTANT**: Use the Read tool WITHOUT limit/offset parameters to read entire files
   - **CRITICAL**: DO NOT spawn sub-tasks before reading these files yourself in the main context
   - **NEVER** read files partially - if a file is mentioned, read it completely

2. **Spawn initial research tasks to gather context**:
   Before asking the user any questions, use specialized agents to research in parallel:

   - Spawn **`Explore`** agents (read-only, cheap) to locate the files related to the
     ticket/task and to explain how the current implementation works — one per question,
     in parallel. `Explore` is the right agent for every locate-and-report question here;
     it reads excerpts rather than whole files, so it finds code without burning context.
   - If relevant, spawn an **`Explore`** agent over `thoughts/` for existing research,
     plans, or decisions about this feature.
   - If a Linear ticket is mentioned, read it yourself in the main context via the Linear
     MCP tools — ticket text is short and load-bearing, and it belongs in your context,
     not a subagent's.

   These agents will:
   - Find relevant source files, configs, and tests
   - Identify the specific directories to focus on (e.g., if the web UI is mentioned, they'll focus on its package directory)
   - Trace data flow and key functions
   - Return detailed explanations with file:line references

3. **Read all files identified by research tasks**:
   - After research tasks complete, read ALL files they identified as relevant
   - Read them FULLY into the main context
   - This ensures you have complete understanding before proceeding

4. **Analyze and verify understanding**:
   - Cross-reference the ticket requirements with actual code
   - Identify any discrepancies or misunderstandings
   - Note assumptions that need verification
   - Determine true scope based on codebase reality

5. **Present informed understanding and focused questions**:
   ```
   Based on the ticket and my research of the codebase, I understand we need to [accurate summary].

   I've found that:
   - [Current implementation detail with file:line reference]
   - [Relevant pattern or constraint discovered]
   - [Potential complexity or edge case identified]

   Questions that my research couldn't answer:
   - [Specific technical question that requires human judgment]
   - [Business logic clarification]
   - [Design preference that affects implementation]
   ```

   Only ask questions that you genuinely cannot answer through code investigation.

### Step 2: Research & Discovery

After getting initial clarifications:

1. **If the user corrects any misunderstanding**:
   - DO NOT just accept the correction
   - Spawn new research tasks to verify the correct information
   - Read the specific files/directories they mention
   - Only proceed once you've verified the facts yourself

2. **Create a research todo list** using TodoWrite to track exploration tasks

3. **Spawn parallel sub-tasks for comprehensive research**:
   - Create multiple Task agents to research different aspects concurrently
   - Use the right agent for each type of research:

   **For deeper investigation** — all of these are `Explore` agents; vary the prompt, not
   the agent type:
   - Find more specific files (e.g., "find all files that handle [specific component]")
   - Understand implementation details (e.g., "analyze how [system] works")
   - Find similar features we can model after, so the plan mirrors an existing pattern

   **For historical context** — also `Explore`, scoped to `thoughts/`:
   - Find research, plans, or decisions about this area
   - Extract the key insights from the most relevant documents

   **For related tickets:**
   - Query Linear directly in the main context via the Linear MCP tools (`list_issues`) to find similar issues or past implementations

   **For external documentation (if needed during planning):**
   - Use web search directly in the main loop for quick lookups during planning, and verify unfamiliar library/API choices during `/plan-review` Step 1 rather than handing off to a separate validator subagent.
   - A plan that adds, upgrades or newly calls a library goes through the emerging-tech research stage next ([research.md](research.md)): list each library with the version it will run.

   Each agent knows how to:
   - Find the right files and code patterns
   - Identify conventions and patterns to follow
   - Look for integration points and dependencies
   - Return specific file:line references
   - Find tests and examples

3. **Wait for ALL sub-tasks to complete** before proceeding

4. **Present findings and design options**:
   ```
   Based on my research, here's what I found:

   **Current State:**
   - [Key discovery about existing code]
   - [Pattern or convention to follow]

   **Design Options:**
   1. [Option A] - [pros/cons]
   2. [Option B] - [pros/cons]

   **Open Questions:**
   - [Technical uncertainty]
   - [Design decision needed]

   Which approach aligns best with your vision?
   ```

### Step 3: Plan Structure Development

Once aligned on approach:

1. **Create initial plan outline**:
   ```
   Here's my proposed plan structure:

   ## Overview
   [1-2 sentence summary]

   ## Implementation Phases:
   1. [Phase name] - [what it accomplishes]
   2. [Phase name] - [what it accomplishes]
   3. [Phase name] - [what it accomplishes]

   Does this phasing make sense? Should I adjust the order or granularity?
   ```

2. **Get feedback on structure** before writing details

### Step 4: Detailed Plan Writing

After structure approval:

1. **Ensure directory exists**: Run `mkdir -p thoughts/shared/plans` (or `G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"; mkdir -p "$G"` on a `linear-only` run)
2. **Write the plan** to `thoughts/shared/plans/YYYY-MM-DD-<KEY>-description.md` (or to `$G/plan.md` when `understand-scope` marked `scope: linear-only`)
   - Format: `YYYY-MM-DD-<KEY>-description.md` where:
     - YYYY-MM-DD is today's date
     - <KEY> is the ticket key (omit if no ticket)
     - description is a brief kebab-case description
   - Examples:
     - With ticket: `2025-01-08-ABC-123-parent-child-tracking.md`
     - Without ticket: `2025-01-08-improve-error-handling.md`
2. **Use this template structure**:

````markdown
# [Feature/Task Name] Implementation Plan

## Overview

[Brief description of what we're implementing and why]

## Current State Analysis

[What exists now, what's missing, key constraints discovered]

## Desired End State

[A Specification of the desired end state after this plan is complete, and how to verify it]

### Key Discoveries:
- [Important finding with file:line reference]
- [Pattern to follow]
- [Constraint to work within]

## What We're NOT Doing

[Explicitly list out-of-scope items to prevent scope creep. Every row that names a
**defect** — as opposed to a feature simply not in this plan — carries where it went:
a filed issue ID, or an explicit "not filed because ___". A deferral with no
destination is deleted, not tracked: the plan is archived on merge and nothing
re-reads it.]

| Out of scope | Why | Destination |
|---|---|---|
| [defect or feature] | [not this ticket / not ready / …] | [filed ABC-123 \| not filed because …] |

## Implementation Approach

[High-level strategy and reasoning]

## Invariants and Their Rung

[One row per invariant this plan introduces or relies on a new check for. The rung is the
highest of architecture → type → lint → test that holds it. A lint
row names the rule id, `severity: error`, its `ast-grep test` cases and the CI job. A test
row's "why not higher" cell says which property no parser or checker can see. Write "none"
if the plan adds no invariant.]

| Invariant | Rung | Artifact | Why not higher |
|---|---|---|---|
| [what must always hold] | [arch / type / lint / test] | [structure, type, rule id + CI job, or test seam] | [why the rung above cannot hold it] |

## Mirrored-field write paths

[`plan-shape@1` criterion 8. One row per external field the plan stores (a Linear name,
an identity-provider role, a token scope); mark authority fields (role, scope, entitlement). Each path is a
`file:function` or `none (reason)`. A plan that mirrors nothing writes `none`.]

| Field | Insert | Update (trigger) | Revoke |
|---|---|---|---|
| [`members.role` (authority)] | [`Org.join` INSERT] | [`Org.join`, every sign-in] | [`Org.join` demotes when the source flags clear] |

## Escape Catalogue (detector or lint plans only)

[Delete this section unless the plan builds a detector, lint rule or static check. List
at least 15 shapes the check must catch or must not flag: generics, nesting, inference,
library types, narrowing, aliases, re-exports. Before any code is written, have an agent
red-team this catalogue (not the implementation) and fold its additions in. Then fill in
the source table: remove each source at the layer that owns it, and detect only the
residue: a source removed at its owning layer needs no detector.]

| # | Shape | Must flag? | Example |
|---|---|---|---|
| 1 | [shape] | [yes / no] | [snippet] |

| Source | Owning layer | Removed by |
|---|---|---|
| [where the bad value enters] | [types / lint config / declaration / custom residue] | [the change, or "residue: detected by <rule>"] |

## Phase 1: [Descriptive Name]

### Overview
[What this phase accomplishes]

### Changes Required:

#### 1. [Component/File Group]
**File**: `path/to/file.ext`
**Changes**: [Summary of changes]

```[language]
// Specific code to add/modify
```

### Success Criteria:

#### Automated Verification:
- [ ] Migration applies cleanly: `make migrate`
- [ ] Unit tests pass: `make test-component`
- [ ] Type checking passes: `npm run typecheck`
- [ ] Linting passes: `make lint`
- [ ] Integration tests pass: `make test-integration`

#### Manual Verification:
- [ ] Feature works as expected when tested via UI
- [ ] Performance is acceptable under load
- [ ] Edge case handling verified manually
- [ ] No regressions in related features

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 2: [Descriptive Name]

[Similar structure with both automated and manual success criteria...]

---

## Testing Strategy

### Unit Tests:
- [What to test]
- [Key edge cases]

### Integration Tests:
- [End-to-end scenarios]

### Manual Testing Steps:
1. [Specific step to verify feature]
2. [Another verification step]
3. [Edge case to test manually]

## Performance Considerations

[Any performance implications or optimizations needed]

## Migration Notes

[If applicable, how to handle existing data/systems]

## References

- Original ticket: `thoughts/shared/tickets/<key>.md`
- Related research: `thoughts/shared/research/[relevant].md`
- Similar implementation: `[file:line]`
````

3. **Commit the plan first, push, and open the issue's single draft PR**:
   - Stage and commit the plan on the issue branch (before any gate-review amendments or implementation commits), push to `origin`, and open the single draft PR titled with `<KEY>`:
   ```bash
   git add thoughts/shared/plans/<plan>.md
   git commit -m "docs(plan): add implementation plan for <KEY>"
   git push -u origin HEAD
   gh pr create --draft --title "<type>(<scope>): <summary> (<KEY>)" \
     --body "Closes <KEY> — Plan: \`thoughts/shared/plans/<plan>.md\`"
   ```
   - **Multi-PR issues (closing vs contributing):** When `<KEY>` ships across multiple PRs (for example `cross-repo` work or phased PRs), only the **final PR** that completes `<KEY>` writes `Closes <KEY>` in `--body` (`type: "closes"` in Linear `get_diff` `issueLinks`). Every other PR is a **contributing PR**: its `--body` starts with `Part of <KEY>` (`--body "Part of <KEY> — Plan: \`thoughts/shared/plans/<plan>.md\`"`, keeping `<KEY>` in its branch name and `--title`) and its Linear diff link is verified as `type: "contributes"` via `get_diff` (`issueLinks`) or set via `update_diff` (`addedIssueLinks: [{ issue: "<KEY>", type: "contributes" }]`), so merging an earlier phase PR never auto-closes `<KEY>`.
   - All subsequent gate notes, plan amendments (`## Gate Amendments`), and implementation commits accrue on this one draft PR (`final-gates` flips it ready with `gh pr ready` when `eris gate check --profile` exits 0). Never open a second PR for the issue in the same repo, and never rebase or force-push the branch after recording a gate receipt (`refs/pull/<N>/head` keeps every receipted `blob/<sha>/<path>` permalink reachable after squash merge and branch deletion).
   - **`linear-only` runs skip commit, push, and draft PR:** When `understand-scope` marked `scope: linear-only` (no git repo diff), the plan lives at `$G/plan.md` (`G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"`). Do **not** run `git add`, `git commit`, `git push`, or `gh pr create --draft`; go straight to Step 5, where each gate binds its own artifact under `$G/` (`{ _tag: "file" }` with a stored `artifact.copy`).

### Step 5: Gate Review & Iteration

1. **Run the pre-implementation gates on the written plan** before presenting it for approval (each gate commits and pushes its write-once artifact before calling `eris gate record`):
   - Run `/premise-gate` to verify every load-bearing substrate premise is observed on its runtime path, writing `thoughts/shared/premise/<YYYY-MM-DD>-<KEY>.md`, committing and pushing it, and binding its receipt to that note (never the plan).
      - On the `deep` profile, run `sdk-check` ([sdk-check.md](sdk-check.md)), committing and pushing its artifact before recording its receipt.
   - Run `/plan-review` to audit the six design invariants (class closure & type monotonicity, static rung & red-on-main proof, gate delta-invariance, remediation round-trip survival, $k$-step state/TOCTOU interleavings, loop-invariant oracle budgets) and the active stack checklist, folding `## Gate Amendments (premise-gate + plan-review)` directly into `thoughts/shared/plans/<plan>.md`, committing and pushing that amendment as a **new commit** on the draft PR branch (`plan-review` is the only gate that binds `thoughts/shared/plans/<plan>.md`), and linking both `blob/<sha>/thoughts/shared/plans/<plan>.md` and `pull/<N>/files` in its receipt.
      - Run `eris lint --all` when the plan touches a governance site (a config key, service seam, queue, event or object act) and record the result in the plan's current-state section.

2. **Present the gated plan location**:
   ```
   I've created and gated the implementation plan at:
   `thoughts/shared/plans/YYYY-MM-DD-<KEY>-description.md`

   Please review it and let me know:
   - Are the phases properly scoped?
   - Are the success criteria specific enough?
   - Any technical details that need adjustment?
   - Missing edge cases or considerations?
   ```

3. **Iterate based on feedback** - be ready to:
   - Add missing phases
   - Adjust technical approach
   - Clarify success criteria (both automated and manual)
   - Add/remove scope items

4. **Continue refining** until the user is satisfied

## Important Guidelines

1. **Be Skeptical**:
   - Question vague requirements
   - Identify potential issues early
   - Ask "why" and "what about"
   - Don't assume - verify with code

2. **Be Interactive**:
   - Don't write the full plan in one shot
   - Get buy-in at each major step
   - Allow course corrections
   - Work collaboratively

3. **Be Thorough**:
   - Read all context files COMPLETELY before planning
   - Research actual code patterns using parallel sub-tasks
   - Include specific file paths and line numbers
   - Write measurable success criteria with clear automated vs manual distinction
   - automated steps should use `make` whenever possible - for example `make -C <package> check` instead of `cd <package> && bun run fmt`

4. **Be Practical**:
   - Focus on incremental, testable changes
   - Consider migration and rollback
   - Think about edge cases
   - Include "what we're NOT doing"

5. **Track Progress**:
   - Use TodoWrite to track planning tasks
   - Update todos as you complete research
   - Mark planning tasks complete when done

6. **No Open Questions in Final Plan**:
   - If you encounter open questions during planning, STOP
   - Research or ask for clarification immediately
   - Do NOT write the plan with unresolved questions
   - The implementation plan must be complete and actionable
   - Every decision must be made before finalizing the plan

## Success Criteria Guidelines

**Always separate success criteria into two categories:**

1. **Automated Verification** (can be run by execution agents):
   - Commands that can be run: `make test`, `npm run lint`, etc.
   - Specific files that should exist
   - Code compilation/type checking
   - Automated test suites

2. **Manual Verification** (requires human testing):
   - UI/UX functionality
   - Performance under real conditions
   - Edge cases that are hard to automate
   - User acceptance criteria

**Format example:**
```markdown
### Success Criteria:

#### Automated Verification:
- [ ] Database migration runs successfully: `make migrate`
- [ ] All unit tests pass: `go test ./...`
- [ ] No linting errors: `golangci-lint run`
- [ ] API endpoint returns 200: `curl localhost:8080/api/new-endpoint`

#### Manual Verification:
- [ ] New feature appears correctly in the UI
- [ ] Performance is acceptable with 1000+ items
- [ ] Error messages are user-friendly
- [ ] Feature works correctly on mobile devices
```

## Common Patterns

### For Database Changes:
- Start with schema/migration
- Add store methods
- Update business logic
- Expose via API
- Update clients

### For New Features:
- Research existing patterns first
- Start with data model
- Build backend logic
- Add API endpoints
- Implement UI last

### For Refactoring:
- Document current behavior
- Plan incremental changes
- Maintain backwards compatibility
- Include migration strategy

## Sub-task Spawning Best Practices

When spawning research sub-tasks:

1. **Spawn multiple tasks in parallel** for efficiency
2. **Each task should be focused** on a specific area
3. **Provide detailed instructions** including:
   - Exactly what to search for
   - Which directories to focus on
   - What information to extract
   - Expected output format
4. **Be EXTREMELY specific about directories**:
      - If the ticket mentions "the web app", specify `apps/web/`
   - If it mentions "the worker", specify `services/worker/`
   - Never use generic terms like "UI" when you mean one specific app
   - Include the full path context in your prompts
5. **Specify read-only tools** to use
6. **Request specific file:line references** in responses
7. **Wait for all tasks to complete** before synthesizing
8. **Verify sub-task results**:
   - If a sub-task returns unexpected results, spawn follow-up tasks
   - Cross-check findings against the actual codebase
   - Don't accept results that seem incorrect

Example of spawning multiple tasks:
```python
# Spawn these tasks concurrently. Codebase research is read-only locate-and-report
# work — always name Explore; never leave subagent_type unset, which silently
# defaults to general-purpose and inherits this session's (expensive) model.
tasks = [
    Task(subagent_type="Explore", description="Research database schema", prompt=db_research_prompt),
    Task(subagent_type="Explore", description="Find API patterns",        prompt=api_research_prompt),
    Task(subagent_type="Explore", description="Investigate UI components", prompt=ui_research_prompt),
    Task(subagent_type="Explore", description="Check test patterns",      prompt=test_research_prompt),
]
```

Example of spawning research-agent for external docs:
```
Task(
  subagent_type="research-agent",
  model="sonnet",
  prompt="""
  ## Your Research Task

  **Question:** What are best practices for implementing WebSocket connections with reconnection logic in TypeScript?

  **Context:** Planning a real-time notification system. Need to understand:
  - Library options (socket.io vs ws vs native)
  - Reconnection patterns
  - Error handling best practices

  **Handoff Directory:** thoughts/handoffs/notification-feature/

  **Handoff Filename:** research-01-websocket-patterns.md

  ---

  Execute your research and create your handoff.
  """
)
```

After research-agent returns, read its handoff before finalizing your plan.

## Example Interaction Flow

```
User: /work plan
Assistant: I'll help you create a detailed implementation plan...

User: We need to add parent-child tracking for sub-tasks. See thoughts/shared/tickets/abc-123.md
Assistant: Let me read that ticket file completely first...

[Reads file fully]

Based on the ticket, I understand we need to track parent-child relationships for sub-task events in the worker service. Before I start planning, I have some questions...

[Interactive process continues...]
```
# Linear Traversal Cookbook

Which calls fetch which surface, and what to pull from each. Pass 1 runs on every retro; pass 2 is signal-gated (signals listed in SKILL.md Step 3).

## Resolving the anchor

- From branch: Linear's branch convention embeds the identifier (`alice/abc-123-...` → `ABC-123`).
- From PR: `gh pr view --json title,body,headRefName` — identifier in title/body, or Linear attachment on the issue side.
- Fetch: `get_issue` with `includeRelations: true`.

## Pass 1 surfaces

| Surface | Call | Pull |
|---|---|---|
| Anchor issue | `get_issue` (includeRelations) | description, state + dates, relations, attachments (PR links) |
| Comment trail | `list_comments` (issueId) | full thread incl. inline `quotedText` comments — decision points, corrections, scope churn |
| Parent / blocking / related / duplicates | `get_issue` per relation | state + description; their comments only if the anchor's trail references them |
| Project living docs | `list_documents` (projectId) → `get_document` | `<project> - Load-Bearing Decisions`, `<project> - Key Assumptions` — entries that led to or constrained the anchor |
| Git / PR | `git log --oneline origin/main..HEAD`, `gh pr view --json files,reviews,comments` | commits, review threads, diff shape |
| Session artifacts | `thoughts/` — retros, plans, ledgers | prior retros on the same surface; the plan that drove the work |

## Pass 2 surfaces

| Surface | Call | When |
|---|---|---|
| Initiative docs (PRDs, Canon once it exists) | `list_documents` (initiativeId) → `get_document` | the chain points above the project |
| Sibling issues in project | `list_issues` (project) | recurrence check within the project |
| Cross-project pattern sweep | `list_issues` (query) | recurrence beyond the project |
| Upstream comment trails | `list_comments` on parent/related issues | scope churn originates upstream of the anchor |
| Prior-retro / rules corpus sweep | grep `thoughts/retros/`, `~/.claude/rules/` | pattern seen before, name unknown |
| External | exa / vendor docs | dependency or vendor behaviour is a rung |

## Timeline discipline

Date-stamp every event. Interleave Linear events (comments, state changes, doc edits) with git events (commits, reviews, merges) into one chronology. The **first divergence** is the earliest event where the actual path departed from the expected one — it is rarely the discovery moment, and the gap between the two is itself evidence for the behavioural rung.

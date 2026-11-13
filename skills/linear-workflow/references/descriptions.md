# Descriptions, mentions and epics

## Writing Good Descriptions

Enough context to start work without asking questions — comprehensive but concise.

**Good**: "Implement the `/v0/user/me/bank/accounts` endpoint that exchanges a bank-link public token
for an access token, stores the linked account, and returns the account details. Must handle
provider errors with RFC 7807 responses."
**Bad**: "Add bank account endpoint" (what does it do?), or three paragraphs of background before the
point (mention the doc instead).

```markdown
## Context
[Why this exists; mention PRDs, docs, parent issues as chips.]

## Scope
[What specifically happens — files, endpoints, contracts, components if known.]

## Acceptance Criteria
- [ ] [Specific, testable condition]

## Notes
[Edge cases, dependencies. Optional.]
```

### Mentions, not links

Point at other Linear resources with **mentions** — they render as chips and create backlinks. A
markdown link or pasted Linear URL renders as a dead hyperlink.

| Resource | Write exactly this |
|---|---|
| **Issue** | the bare identifier — `ABC-123` — no `@`, no link |
| **Project** | `<project id="<uuid>" label="Project Name" href="<project url>" />` |
| **Document** | `<document id="<uuid>" label="Doc Title" href="<document url>" />` |
| **Initiative** | `<initiative id="<uuid>" label="Initiative Name" href="<initiative url>" />` |
| **Person** | `@Display Name` |

Always use the **self-closing `label="…"` (`/>`) form** above on the Linear MCP (`save_issue`,
`save_document`, `save_project`, `save_initiative`, `save_comment`), XML-escaping `&` as `&amp;` and
`"` as `&quot;` in `label=`. Never write paired opening/closing `<project>` or `<document>` tags: the
MCP converts paired tags into dead markdown links. (Direct Linear GraphQL uses plain markdown links
instead.)

Before saving, scan the description for markdown links whose target is a Linear workspace URL: every
hit becomes a mention. External links (GitHub, docs sites) stay markdown. Long-form content (PRDs,
specs, project descriptions) use the editor's richer blocks (tables, diagrams, collapsibles) rather than a wall of text.

Leave bold and italics off any run that starts or ends at a chip (`ABC-123**'s re-search**`): a
`patch` to the description can drop the emphasis there, and re-adding it stores literal asterisks. A
`patch` can also turn chips outside its anchors into markdown links, and re-patching them one by one
does not restore them. After a description patch, `get_issue` and compare every chip against the
pre-patch read, not just the patched lines. Detail: `/tpm` `references/linear-constraints.md`.

### Sub-issues

Children inherit the parent's context: a couple of sentences plus acceptance criteria.

### Phased / waved work: one epic per phase

For 3+ related slices landing in phases or waves, create a parent `[EPIC]` issue per phase/wave and
file each **technical** slice as a sub-issue (`parentId`) of its wave epic. Blocker relations
complement the hierarchy (critical path, epic→epic chaining); they never replace it.

- An epic holds technical delivery only. Business-development, legal, ops and partner work is filed
  standalone, related to the epic with `blocks`, and named in the epic's **External gates**
  section — never as a child (`/tpm` check C1). The `blocks` relation and that section mark a gate
  issue, not a label. Label a gate with the team's business-development label where the team has
  one; otherwise give it no function label.
- A title prefix like `W1.0` / `Phase 2:` / `P0 —` is a parent epic trying to exist — the hierarchy
  lives in `parentId`.
- The epic description carries the arc (ordered slice chips), the exit bar, and the PRD/doc chip.
- Create the wave epics first, then slices with `parentId` set at creation, passing each epic's
  UUID rather than its identifier (Hard Rule 5).

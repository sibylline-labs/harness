# The Codebase Is the Pattern Authority

**The codebase is the pattern authority; a secondhand description of it is
checked against it before it shapes code.**

Fires when writing code from a plan, rule example, review suggestion, generated
doc, design schema, or when scaffolding a greenfield repo alongside siblings.
Match the nearest sibling (for a new repo, the nearest sibling repo on disk).
Codebase wins over rules; rules win over plans; mid-migration, target seam wins.
Playbook:
[`~/.claude/rule-playbooks/codebase-is-the-pattern-authority.md`](~/.claude/rule-playbooks/codebase-is-the-pattern-authority.md).

## Red Flags

- Pasting a block from a doc, or mapping requirement IDs 1:1 to files.
- A name, layout or shape with no sibling precedent you can point to.
- Justification is "the plan / rule / doc said so" or "new repo, no sibling".
- Consumer-facing text carries ticket IDs, phase numbers or internal labels.

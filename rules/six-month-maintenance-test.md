# The Six-Month Maintenance Test

**Every artifact you produce is inventory the team looks after. Before producing
one, ask: is this really worth the effort of looking after in six months' time?**

Fires before creating any test, abstraction, config knob, doc or helper. The
metric is confidence or capability per maintenance minute, never artifact count.
The process stays the authority: when following guidance faithfully keeps
producing artifacts that fail the test, flag the guidance to its owner in one
line. The playbook,
[`~/.claude/rule-playbooks/six-month-maintenance-test.md`](~/.claude/rule-playbooks/six-month-maintenance-test.md),
holds the full pattern and DO/DON'T.

## Red Flags

- You can't name the consumer or failure mode of the thing you're about to create.
- The justification is "the checklist says so" with no six-month answer behind it.
- You're on the Nth near-identical artifact this session and haven't asked whether the class is worth it.
- "Just in case" or "might need it later" appears in your reasoning.

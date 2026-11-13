# Plan Before Code, Not After

**A plan committed after the code it describes is documentation, not planning;
the plan must precede the first commit it describes.**

Fires when a plan lands in `thoughts/shared/plans/` or `thoughts/plans/`,
especially mid-PR after a scope change. Under `/work plan` this is structurally
satisfied (the `plan` stage commits the plan first and opens the draft PR before
review and code); on ad-hoc branches or pivots outside `/work`, verify the plan
commit precedes the code or label it retrospective. Playbook:
[`~/.claude/rule-playbooks/plan-before-code-not-after.md`](~/.claude/rule-playbooks/plan-before-code-not-after.md).

## Red Flags

- You are writing a plan to "explain what happened".
- The plan is being added after review feedback already shaped the code.
- The plan ratifies an architectural choice nobody validated up front.

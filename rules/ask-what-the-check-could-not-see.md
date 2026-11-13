# Ask What the Check Could Not See

**A discipline's output is evidence about what was inside its frame. It is never
evidence that the frame was the right size.**

Fires right after any coverage-producing check: a premise table, a green test run,
a lint pass, an audit, a verification. Spend one beat naming what it could not
have seen. Two frames account for most cases: the other operand of a compare,
join, sync or diff, and the instrument's environment. Then close the gap or
report the work as unverified. Read the playbook,
[`~/.claude/rule-playbooks/ask-what-the-check-could-not-see.md`](~/.claude/rule-playbooks/ask-what-the-check-could-not-see.md),
for the mechanism, DO/DON'T and the surfaces it governs.

## Red Flags

- A diff / reconcile / sync / migrate has no premise about the other side's identity.
- You cannot say how you knew the N entries in your table were enough.
- A capability branch (`command -v`, feature-detect, try/except import) sits in the path under test and you measured one side.
- You are reporting a number without the environment that produced it.
- The thoroughness of the check is doing the work of arguing it was complete.

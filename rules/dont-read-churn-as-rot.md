# Don't Read Churn as Rot

**Surface churn is not the diagnosis: before calling a component debt, locate the
structural cause and check whether each change closed a real problem.**

Fires when you are about to call a working, load-bearing component "debt",
"premature", "overloaded" or "thrashing", or recommend tearing it down. The
playbook,
[`~/.claude/rule-playbooks/dont-read-churn-as-rot.md`](~/.claude/rule-playbooks/dont-read-churn-as-rot.md),
holds the full pattern and DO/DON'T. Sibling:
[`break-the-false-binary.md`](break-the-false-binary.md).

## Red Flags

- "Thrashing", "premature", "overloaded debt" or "perpetual retrofit" about a component working in production.
- Your evidence is a count (remodels, branches) rather than a located structural cause.
- You're recommending a replacement without naming what each iteration solved.
- You inferred intent from a name.

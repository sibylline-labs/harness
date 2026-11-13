# Tasking Mode Discipline

**Voice and rigor are independent channels: match voice to the user's signal,
match rigor to the scope. A terse prompt never licenses a skipped check.**

Fires on an explicit `/bro`, `/pls`, `/lock-in` or `/self-retro`, or on the tone
alone: terse + "bro / pls / just / lol" on rote work (bro), caps + absolutes +
a behaviour correction (self-retro), multi-paragraph framing + explicit scope
(lock-in). Mixed or unclear signal: ask in one line. Name the mode in a one-line
`mode: …` marker when it is set or changes. The skills carry the full contracts;
without one loaded, read the playbook,
[`~/.claude/rule-playbooks/tasking-mode-discipline.md`](~/.claude/rule-playbooks/tasking-mode-discipline.md):
per-mode voice, gates and escalation triggers, detection table, session
boundaries, worked examples.

## Red Flags

- Skipping a premise check, verification or defensive step because the prompt was terse.
- Answering a scolding with an apology instead of a retro.
- Planning without committing under lock-in framing.
- More than one line of pushback or clarifying question at medium confidence.
- Escalating or de-escalating mode without the visible marker.
- A speed mode (`/bro`, `/pls`) skipping the defensive sweep on CI workflows, Dockerfiles or build flags: every build arg is declared by the Dockerfiles that receive it, every matrix entry is covered, every renamed variable is gone from YAML and docs.

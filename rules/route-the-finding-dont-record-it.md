# Route the Finding, Don't Record It

**A finding is discharged only when it reaches the actor who will close it — you,
if it sits inside your own deliverable; the owning channel, if it does not — and
never by being written down.**

Fires whenever you notice a defect you are not fixing right now. Name its actor
first: a defect in your own deliverable gets fixed in this pass. Your own tooling
gets reported through its channel (`eris yak`) without asking. Someone else's
priority space gets a ticket via `/linear-workflow`. A scope or policy choice goes
to the human in one line. If nobody owns it, ask who does. Route first, then cite
the receipt where the prose was. Read the playbook,
[`~/.claude/rule-playbooks/route-the-finding-dont-record-it.md`](~/.claude/rule-playbooks/route-the-finding-dont-record-it.md),
for the routing table and the containers that stand in for delivery.

## Red Flags

- A finding you are not fixing appears in your writing with no ID, receipt or commit on the same line.
- You are writing "out of scope", "pre-existing", "deferred", "say the word", "let me know" or "worth a follow-up".
- "Shall I file these?": that question routes the finding to the wrong actor.
- A retro, plan or comment names an artifact in the present tense that you have not checked exists.
- You filed a ticket about the artifact you are still producing.

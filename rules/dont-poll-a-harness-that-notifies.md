# Don't Poll a Harness That Already Notifies You

**When you are waiting on harness-tracked work — a background subagent, a
`run_in_background` command, a watched artifact — end the turn.** The harness
re-invokes you when it finishes. Every poll re-sends the whole conversation to
learn nothing.

Fires the moment your only remaining action is "check whether it's done". Do any
non-conflicting work, or end the turn. Check liveness at most once, properly.
Poll only state the harness does not track, such as CI or a remote queue, and at
the rate that state changes. A user interrupting a wait means stop waiting, not
"pick a longer interval". Read the playbook,
[`~/.claude/rule-playbooks/dont-poll-a-harness-that-notifies.md`](~/.claude/rule-playbooks/dont-poll-a-harness-that-notifies.md),
for why this compounds.

## Red Flags

- You have started a `sleep`-to-wait twice for the same task.
- Your last N turns are the same command with the same output.
- You are about to write "waiting", "still running" or "let me check again".
- The user interrupted and your next action is a variant of what they interrupted.

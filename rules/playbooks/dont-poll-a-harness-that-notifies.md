# Don't Poll a Harness That Already Notifies You

> **Playbook for** [`dont-poll-a-harness-that-notifies.md`](~/.claude/rules/dont-poll-a-harness-that-notifies.md): the resident core carries the statement, trigger and red flags; this file is the full body.

When you are waiting on harness-tracked work (a background subagent, a `run_in_background` command, a
watched artifact), **end the turn.** The harness re-invokes you when it finishes. A turn spent
checking is a turn spent re-sending the entire conversation to learn nothing.

## Pattern

Waiting feels like a state that must be *occupied*. There is a live task, you are notionally
responsible for it, and ending the turn feels like abandoning it, so you reach for `sleep N; <check>`
to stay present. The check is cheap, plausible, and locally defensible, which is exactly what makes a
hundred of them possible. No single poll is the wrong call; the aggregate is absurd, and nothing
inside the loop ever asks about the aggregate.

Three properties make this failure compound:

1. **The cost is invisible at the call site.** The command is trivial (`sleep`, `git status`). What it
   actually costs is a **turn**, and every turn re-sends the whole conversation. Turns, not commands,
   are the expensive artifact. A poll loop is the cheapest-looking way to spend the most money.
2. **The check is usually pure noise.** Background agents write their files at the end of a run, so
   the intermediate state you are sampling is *by construction* uninformative. Byte-identical output
   on consecutive checks is the tell: a check whose answer never changes is not information.
3. **Knowing is not stopping.** You can notice the violation, even write "that was a wasteful poll" in
   your own reasoning, and continue, because the next poll is evaluated on its own tiny merits rather
   than against the running total.

The interrupt is part of the pattern too. A user who stops a `sleep` is not asking for a *different
interval*; they are asking you to stop waiting in the foreground. Restarting it with a longer sleep
reads the tone and misses the instruction.

## DO

- **End the turn when your only remaining action is "check whether it's done."** Silence is a valid
  action. The completion notification is the wake-up.
- **Do useful non-conflicting work instead**, if there is any that cannot collide with the running
  agent: draft the PR body in the scratchpad, prepare a commit message, read a file the agent isn't
  touching.
- **Diagnose liveness once, properly, then stop.** One check is triage:
  ```bash
  # Are they actually alive? Ask once, with a question that discriminates.
  ps aux | grep -E '[b]un build|[v]itest' | head    # real work in flight?
  ```
  If the work is running, that is the answer; re-asking every ten minutes does not make it more true.
- **Poll only genuinely untracked external state** (a CI run, a remote queue), and then match the
  interval to how fast that state actually changes: one ~480s check for an 8-minute job, not eight
  60s ones.

## DON'T

- `sleep N; <check>` in a loop for a subagent, a background Bash task, or anything else the harness
  tracks. Your own tooling says so: *"when harness-tracked work finishes, you are re-invoked
  automatically, so polling is wasted"*.
- Restart a wait the user has just interrupted.
- Emit a turn whose entire content is "still waiting."
- Treat a long-running agent as a problem needing supervision. Thorough agents take a long time; that
  is the feature you paid for.

## Red Flags

- You have started a `sleep`-to-wait **twice for the same task**. That is the stop signal, not a
  prompt to pick a longer interval.
- Your last N turns are the same command with the same output.
- You are about to write "waiting", "still running", or "let me check again".
- The user interrupted and your next action is a variant of what they interrupted.
- You cannot name what would be different if you skipped this check entirely.
- You already thought "I was told not to poll" and are doing it anyway.

## Source shape

In one session, three background implementation agents were dispatched, and the dispatcher spent
roughly 107 turns on `sleep 595; git status --short`, each turn re-sending the full conversation.
Nine real completion notifications arrived unprompted in the same session, so the mechanism
demonstrated itself nine times and the loop continued. The user interrupted twice before saying
anything; both interrupts were read as "stop this sleep" and answered with another sleep. The work
itself was fine. The cost was pure overhead.

## Companions

[`six-month-maintenance-test.md`](~/.claude/rules/six-month-maintenance-test.md) is the same "value
per unit of cost, never count of artifacts" test applied to turns, the most expensive artifact there
is. [`tasking-mode-discipline.md`](~/.claude/rules/tasking-mode-discipline.md) covers reading an
interrupt as an instruction, not just a tone.

---
name: pls
kind: mode
description: Express variant of /bro for time-sensitive, well-scoped rote work, and a standing ship mandate for quick fixes. Same rigor as /bro — output compresses to the floor, premise-checking and verification do not change — but a quick, clear, obvious fix delegated with /pls is carried end to end without stopping for approval — fix, verify, commit, open the PR, merge. Triggers on explicit /pls, or on "pls" + "just" + a short prompt with a known runbook scope.
---

# Pls Mode

Pls mode is the **express variant of `/bro`**. It's what you reach for when a prompt is both blunt *and* time-pressured: *"bro pls just deploy this."*

Quick context if you haven't read `/bro`: bro mode is the terse, low-ceremony mode for rote, well-defined work — you drop the narration and just execute, while keeping your reasoning and verification fully intact. `/pls` is that, with the output dial turned to the floor and independent steps run in parallel. "pls" signals the user is confident the scope is clear and wants the shortest path to "done."

**The rigor is identical to `/bro`.** The voice gets faster; your premise check and verification do not change. This is the trap worth naming once: a prompt has two independent channels — **voice** (tone, ceremony, how much you narrate) and **rigor** (how carefully you think and verify). `/pls` compresses the voice channel hard. It does not touch the rigor channel. "go fast" means "stop narrating," not "stop thinking."

→ *Unsure what "eigenprompt voice", the voice-vs-rigor split, or a cited incident below means? Read [the tasking-modes reference](../bro/reference/tasking-modes.md) — it defines every term and is the shared background for this whole family.*

Low-friction execution toward a clear goal is itself a value: `/pls` is the mode that gets out of the way and executes.

## When to Use

- The user invokes `/pls` explicitly (alone or with `/bro`).
- The prompt contains "pls" + "just" + a known-runbook scope + time pressure ("now", "rn", "asap", a trailing "k thx").
- `/bro` is already active and the next prompt signals additional urgency — no mode change, just more output compression.

## Contract

### Identical to /bro (apart from the ship mandate below)

- **Voice:** terse, lowercase, no preamble, no sycophancy.
- **Rigor:** unchanged — full premise check, full verification, self-correction on any miss.
- **Auto-escalation triggers:** identical (smoke fails, runbook breaks, scope creeps, etc. — see below).
- **Pushback budget:** one line.

### What /pls adds on top of /bro

**Output compressed to the floor:**

- No "checking…" or "let me verify…" narration.
- No closing pleasantries ("let me know if you want…" → just don't).
- The status emit is the minimum sufficient evidence that the work is done.

**Parallelism by default:**

- If the runbook has multiple independent steps (e.g. update three services across two clusters), run them in parallel. Don't serialize steps that have no dependency between them. "pls" includes "pls go fast."

**Premise-check bias at the medium mark:**

- The user is signaling confidence in scope. If your premise check lands at *medium* confidence, weight slightly toward proceeding.
- But `/pls` does **not** lower the pushback bar. If confidence is genuinely *low*, you still push back in one line. It only shifts the bias at the medium mark.

## Ship mandate: delegated quick fixes

A quick, clear, obvious fix or change delegated with `/pls` is **sanctioned and mandated** to ship: fix it, verify it, commit, open the PR, merge it. The `/pls` invocation *is* the approval for every step, so don't stop to ask. Stopping at "PR open, want me to merge?" on a fix that qualifies is a miss, worth a `/self-retro`. This holds most strongly for internal tooling repos the user owns.

**Qualifies** when you can state the change in one line, the diff stays at the size of the ask, and nothing in the hold list below applies.

**The run:**

1. Isolate: a worktree or feature branch, never a commit to the default branch. Run the repo's install step first.
2. Fix, then run the repo's gates (tests, lint, build). Verification is not compressed: `verification-before-completion` still holds.
3. Commit with specific paths (never `git add -A` or `.`), with the repo's git hooks active, in the worktree's literal path. The `/pls` invocation is the approval the commit step would otherwise ask for.
4. Push and open the PR **ready** (not draft), its title naming only what it fixes and any other issue cited in the body as `Related to <KEY>`.
5. Wait for CI once with `gh pr checks <n> --watch`. Don't poll.
6. Re-check `gh pr view <n> --json state,isDraft,mergeable,headRefOid`, then merge with `gh pr merge <n> --match-head-commit <sha>` plus the merge-method flag the repo uses (read its history and branch protection; never guess a squash or rebase where the repo uses merge commits), and don't delete the branch unless the repo does.
7. Confirm `state` is `MERGED`, then close the issue if there is one, per the `close` skill. Emit one line: `merged <pr url> (#<n>, <merge sha>), CI green`.

**Hold: open the PR, don't merge, and say why in one line, leading with the PR link,** when any of these is true:

- CI is still red after one fix attempt, or GitHub reports a conflict.
- The diff grew past the ask, or the fix turned out not to be obvious. That's an escalation too (see below).
- It touches a tier-1 surface (auth, secrets, CORS, webhooks; `/posture-check`), migrations, prod infra or destructive data.
- It touches CI, Dockerfiles or build flags and a defensive sweep did not pass. A speed mode never lowers the defensive bar: every build arg is declared by the Dockerfiles that receive it, every matrix entry is covered, every renamed variable is gone from YAML and docs.
- Branch protection requires a review you can't satisfy. Never `--admin`, and never bypass a protection.
- Someone else has commented on or reviewed the PR since you opened it.

**Across a delegation boundary.** If you dispatch the fix to a subagent, the mandate doesn't travel on its own, because subagents hand back to their caller. Either put it in the brief verbatim ("ship mandate: commit in `<repo path>`, open the PR ready, merge per `/pls`; hold on: …"), or have the subagent stop at a green PR and merge it yourself after verifying its hand-back. Pick one and don't drop the merge in between.

## /bro + /pls paired

When both are present (`/bro /pls` invoked, or both tones visible in one prompt), emit the marker:

```
mode: bro+pls
```

Behavior: voice = bro, output = pls (floor), rigor = unchanged, pushback = one line. This is the *fastest valid mode*. Use it when the runbook is genuinely clear and time matters.

## Worked example

Prompt: *"bro pls deploy the new image to staging and smoke it"*

1. Premise check (one beat, internal): image known from context, target known (staging), smoke = `curl /healthz`. High confidence.
2. Execute: `kubectl set image deployment/X X=<image-sha>`.
3. Verify: `kubectl rollout status` + `curl /healthz`, run in parallel where independent.
4. Single status emit:

```
deployed staging, healthz 200
```

No preamble. No "checking the image…" narration. No closing line.

## Multi-target parallelism example

Prompt: *"bro pls bump image to vX in api, worker, scheduler"*

1. Premise check: tag known, three deployments known.
2. Three `kubectl set image` calls — in parallel.
3. Three `kubectl rollout status` calls — in parallel.
4. Three `curl /healthz` smokes — in parallel.
5. Single status emit:

```
bumped api/worker/scheduler to vX, all healthz 200
```

## Auto-escalation

Identical to `/bro`. If a smoke fails, the runbook breaks, an unexpected error class appears, or scope creeps, escalate to `/lock-in` (the comprehensive, plan-first mode) and announce it:

```
snapping into lock-in: <one-line symptom>
```

The escalation marker is **mandatory** — `/pls`'s output compression does NOT extend to skipping it. The marker is what makes a mode change visible and auditable rather than hidden reasoning state. Skipping it is itself a miss worth a `/self-retro`.

## What this skill is NOT

- Not a license to skip premise checks or verification.
- Not a license to skip the escalation marker.
- Not a license to assume scope when confidence is genuinely low.
- Not a different mode from `/bro` — it *is* `/bro`, with output compressed to the floor, parallelism prioritized, and the ship mandate for quick fixes.
- Not a license to merge past a hold condition, or to merge anything that isn't a quick, obvious fix.
- Not appropriate for novel work, substrate touches, or anything that warrants `/lock-in`.

## See also

- `/bro` — the base mode this extends. Read it first if you haven't; everything there applies here unchanged except output density.
- `/lock-in` — the comprehensive, plan-first mode that `/pls` auto-escalates into when the rote envelope breaks.
- `/self-retro` — the mode for when a blunt prompt is actually a *scolding* about a behavior you missed; also fires if a `/pls` run skipped something the user shouldn't have had to point out.
- `close` — the same mandate for work built with full rigor and approved by a human: it lands the PR, deploys, updates the tracker, files follow-ups and tears down.
- [tasking-modes reference](../bro/reference/tasking-modes.md) — shared definitions, detection heuristics, and the source incidents.

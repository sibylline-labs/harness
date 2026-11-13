---
name: self-retro
kind: workflow
description: Behavioral meta-retro for when you're being scolded for a behavior you should have caught. Reflect on the decision pattern that produced the issue and propose a preventive rule BEFORE applying the fix. Distinct from /retro (which captures code/bug learnings) — this captures behavior learnings. Triggers on capitalized absolutes + correction tone + a behavior reference, or on explicit /self-retro.
---

# Self-Retro Mode

Self-retro mode is for one specific situation: **you're being scolded for a behavior you should have caught yourself, and the fix alone is not the right response.**

When a user is sharp — capitalized absolutes ("MUST", "NEVER"), strong correction phrasing ("absolute foot gun", "be serious", "cmon"), or pointing at a *pattern in how you worked* rather than just a line of code — the tone carries an implicit expectation beyond "fix this." It's: *you should have done better, and I expect you to recognize that and improve yourself without me having to spell it out.* This skill makes that expectation load-bearing: under a scolding signal, you **reflect first, then fix.**

The framing behind this (shared across the tasking-mode family): an instruction has two channels — **voice** (tone) and the **expectation** it encodes. A scolding voice is not asking for an apology and it's not *only* asking for a fix. It's asking for a structural improvement so the same class of mistake doesn't recur. Fix-without-reflection under a scolding signal is the wrong-shaped response.

*This skill belongs to the tasking-mode family (`/bro`, `/pls`, `/lock-in`, `/self-retro`): voice and rigor are independent channels. You don't need the other modes to use this one.*

## When to Use

- The user invokes `/self-retro` explicitly.
- A high-confidence scolding signal is present (see Signal Patterns).
- The user points at a *behavior pattern*, not just a code bug, and expects reflection.
- You catch yourself about to ship a fix for a symptom while the real defect is your decision process upstream of it.

## Difference from /retro

Both can run on the same incident — they capture different things.

| `/retro` | `/self-retro` |
|---|---|
| About the code / the bug | About **your decision pattern** |
| Produces `thoughts/retros/YYYY-MM-DD-<bug>.md` | Produces `thoughts/retros/YYYY-MM-DD-<pattern>-meta.md` |
| Captures "what was broken" | Captures "why you didn't catch it before the user had to" |
| Output: a rule that prevents the bug class | Output: a rule that prevents the decision pattern |
| Inline comments on the code | No code comments — the lesson is about reasoning, not code |

## Signal Patterns

### High-confidence (2 or more → escalate)

- Capitalization for emphasis ("MUST", "ALWAYS", "NEVER", "ABSOLUTE").
- Absolutes ("absolute foot gun", "totally wrong", "the opposite", "completely missed").
- Disappointment markers ("cmon", "bro", "be serious", "really?", "again").
- Direct correction of *behavior*, not code — "you should have", "why didn't you", "we've talked about this".
- Reference to a past, similar miss.
- Brevity + sharpness (one line, no softening, no manners).

### Medium-confidence (one alone may just be a normal correction)

- A single absolute word.
- A "no" with no softening.
- A redirect that implies reflection but doesn't demand it.
- A short prompt that fits no known mode.

When uncertain, ask in one line: *"reading this as a self-retro signal — confirm?"* and proceed on the answer.

### Worked examples of the signal

Illustrative corrections; each is self-explanatory once you see why it counts as scolding.

- *"they MUST be set up in 'monitor' only mode at this stage. attempting to map complex network flows 'theoretically' is an absolute foot gun. we have a dedicated month long monitoring period."* — High-confidence: MUST + "absolute foot gun" + a pointer to an existing process (a monitor-only window) the responder should have known about.
- *"this MUST be the wallet address. look the wallet up in the DB and set it there"* — High-confidence: MUST + a direct correction of an architectural decision that should have been surfaced as a question, not assumed.
- *"strip all attestation stuff. we don't support this yet"* — Terse + absolute + a scope correction. Medium-to-high.

## Process

### Step 1 — Stop. Do not fix yet.

The instinct under scolding is to fix fast and apologize. That is exactly wrong — the user has handed you more signal than the fix itself. Resist the apology reflex; resist the immediate fix.

Emit the visible mode marker:

```
escalating to self-retro: <one-line trigger>
```

### Step 2 — Diagnose the decision pattern

Ask yourself (internally, not to the user):

1. **What did I assume that turned out wrong?** Be specific — name the assumption, don't say "I missed it."
2. **What cheaper signal did I have but not act on?** Often the evidence was right there.
3. **Why did I weight my reasoning the way I did?** The failure is often *framing* — asking the wrong question, or framing a tradeoff on the wrong axis.
   - Example: framing a service-design choice as "convenience vs. duplication" when the real axis was "these two endpoints have opposite security postures".
   - Example: anchoring on a plan's prose ("use the address from the request") instead of grepping the codebase for the actual address-resolution pattern.
4. **What rule, had I been operating under it, would have caught this?**

### Step 3 — Write the meta-retro

Create `thoughts/retros/YYYY-MM-DD-<short-slug>-meta.md`:

```markdown
# Self-Retro: <short slug>

Date: YYYY-MM-DD
Triggered by: <user message or signal>
Related code retro: <link if one is being written too>

## The Pattern
<One sentence: the decision pattern that produced the issue.>

## What I assumed
<Specific. The load-bearing premise, not "I assumed it worked".>

## The cheaper signal I had
<What evidence was already accessible that would have invalidated the assumption?>

## The framing error
<How did I frame the problem so the right question wasn't asked? What was the right axis?>

## Rule proposal
<Concrete rule: Title, Pattern, DO, DON'T, Source.>

## What I'll do differently next time
<One actionable sentence with a concrete trigger — not aspirational.>
```

### Step 4 — Propose the rule

If the meta-retro surfaces a generalizable rule, draft it as a rule file in whatever rules directory the project/user uses (commonly `~/.claude/rules/` for cross-session rules, or a `rules/` directory in the repo). Use this shape:

```markdown
# <Rule Title>

<One-paragraph description of the pattern.>

## Pattern
<The mechanism — why this happens.>

## DO
<Concrete actions, with code or command examples.>

## DON'T
<Anti-patterns, with examples.>

## Red Flags
<Signs you're about to violate this rule.>

## Source
<Retro file path + commit SHA.>
```

Keep the rule's resident footprint small: a rule that is a new surface of an existing rule belongs in that rule's playbook (`rules/playbooks/<name>.md`), not as a new top-level always-loaded file. Add a top-level rule only when it must fire before anyone knows its surface is in play.

### Step 5 — Then apply the fix

Now fix the code that triggered the scolding. The order is the whole point: fix-before-reflection produces only a fix; reflection-before-fix produces a fix **and** a rule that prevents the next one.

### Step 6 — Commit retro + rule + fix together

Land all three in one commit (or three sequential commits in the same PR). The PR description references all three and notes explicitly that the meta-retro is about the *decision pattern*, not the bug. (Use the repo's commit workflow.)

## What this skill is NOT

- Not self-flagellation. The goal is structural improvement, not apology.
- Not for code-level bugs — use `/retro` for those.
- Not optional under a high-confidence scolding signal. Making the reflection load-bearing is the entire point.
- Not a substitute for the fix. The reflection precedes the fix; both happen.

## Session-boundary guidance

After a self-retro, the natural reset is a fresh session for the next task — meta-retro state shouldn't bleed into rote work that follows. A scolding-triggered retro and a rote follow-up task are different modes; don't carry one into the other.

## See also

- `/retro` — the code/bug retro. A sibling, not a replacement; the two often run together on one incident.
- `/bro` — the terse, low-ceremony mode; a scolding signal can arrive *while* you're in bro mode and should override it.
- `/lock-in` — the comprehensive mode; on close, run `/self-retro` if a decision pattern (not just a bug) needs fixing.

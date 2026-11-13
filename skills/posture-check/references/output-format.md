# Output Format — the bounded 3-line shape

The skill's output is a **gate on a PR review**, not a report. It rides in a PR comment or a review
turn. Long output gets ignored — and an ignored gate is worse than no gate, because it teaches the
team the output doesn't matter. The 3-line cap is load-bearing.

## The contract — six shapes

### Shape 1 — Silent (no class instance found)

**No output.** Empty stdout, empty PR comment. Most changes that touch a tier-1 surface still
introduce no class instance; silence is the correct signal.

### Shape 2 — New instance of a class

3 fixed lines:

```
⚠ posture-check (<surface>): new instance of <class-id> — <class-name>
  <file>:<line> — <one-line excerpt of the offending code>
  why this matters: <one sentence lifted verbatim from the vocabulary's Why it kills>
```

Worked example:

```
⚠ posture-check (auth): new instance of A1 — Empty-string env default
  src/settings/secrets_signing.py:47 — signing_key: SecretStr = Field(default="", ...)
  why this matters: empty-string default survives missing config without surfacing the absence; the service will boot, then sign with a corrupted key
```

### Shape 3 — Combined instance (diff × existing state)

3 fixed lines; line 2 names *both* the diff's added line AND the pre-existing component it combines
with:

```
⚠ posture-check (<surface>): diff combines with existing state — <class-id> — <class-name>
  diff: <file>:<line> + existing: <other-file>:<line>
  why this matters: <one-sentence scenario>
```

Worked example:

```
⚠ posture-check (auth): diff combines with existing state — A4 — CORS credentials + wildcard origin
  diff: src/http/cors.py:88 (allow_credentials=True added to /webhook/* route) + existing: src/http/cors.py:23 (allow_origins=["*"] on the same router)
  why this matters: a CORS preflight from any origin will now succeed AND carry credentials; this is the spec-defined unsafe combination
```

### Shape 4 — Multiple findings, capped

More than one class fires → the top finding in full (Shape 2 or 3) plus one summary line:

```
+ 2 more findings on auth (A2 fail-open flag, A4 missing webhook dedup) — run `/posture-check auth` for full sweep
```

More than 3 surfaces touched → the final line escalates to a split recommendation:

```
+ this PR touches 4 tier-1 surfaces (auth, webhooks, api-mounting, feature-gates) — consider splitting before merge
```

### Shape 5 — Fail-closed (unknown surface)

When a run asserted to be surface-relevant (a named surface argument, or the user framed the change
as touching a tier-1 surface) matches no registered surface, the skill cannot silently pass:

```
⚠ posture-check: unregistered surface
  <file> changed but matches no surface in .claude/surfaces.yml
  → tag this surface (edit .claude/surfaces.yml) or mark explicitly out-of-scope (add 'posture-check: oos' to the PR description)
```

The opt-out is **explicit and visible** — `posture-check: oos` in the PR description, where
reviewers can see and challenge it. Silent escape is what fails the gate.

### Shape 6 — Budget exceeded

The cost ceiling triggers a single line:

```
⚠ posture-check (<surface>): budget exceeded — escalate to a full surface audit
```

A surface that consistently exceeds the per-PR budget is too big for per-PR gating; the remediation
is the full sweep, not a bigger budget.

## The ask (a `⚠` or `ⓘ` finding on a PR)

A top finding of severity `⚠` or `ⓘ` also goes out as `eris ask --blocking` (SKILL.md step 7). The
ask id is appended to the finding's first line; no line is added, so the 3-line cap holds:

```
⚠ posture-check (auth): new instance of A1 — Empty-string env default · ask 01J9X…
  src/settings/secrets_billing.py:12 — billing_api_key: SecretStr = Field(default="", ...)
  why this matters: empty-string default survives missing config without surfacing the absence; the consumer will run with no key
```

Only the top finding is asked; the `+ N more` line is unchanged. A low finding, the fail-closed
line, the budget line and any run with no PR (a sweep) send no ask, and a failed ask leaves the
finding as prose with an "ask not filed" note.

## Severity prefix

The leading glyph reflects the highest-severity finding:

| Glyph | Severity | When |
|---|---|---|
| `⚠` | High or Critical | New or combined instance of a high/critical class |
| `ⓘ` | Medium | New instance of a medium-severity class (informational) |
| `·` | Low | Suppressed by default; emits only under `severity_floor: low` |

Severity is **read** from the vocabulary entry's `Typical severity` — this skill never assigns its
own.

## What this output is NOT

- **Not a fix recommendation.** It names the class instance and points at the line; choosing the fix
  is the human's job, informed by `Why it kills`.
- **Not a tracker issue.** Filing is a human or sweep decision; this skill is read-only.
- **Not review approval/rejection.** It emits a comment, period; what the team requires from it is a
  CI-policy choice.
- **Not prose.** No paragraphs. A finding that *needs* more than 3 lines means the vocabulary's `Why
  it kills` line needs rewriting, not the cap relaxing.

## Worked end-to-end — a PR touching secrets and CORS

The diff adds a secret loader and a CORS allowlist entry:

```diff
+ # src/settings/secrets_billing.py
+ billing_api_key: SecretStr = Field(default="", description="Billing API key")
+
+ # src/http/cors.py
+ "https://newpartner.example.com",   # added to allow_origins
```

The skill emits:

```
⚠ posture-check (auth): new instance of A1 — Empty-string env default
  src/settings/secrets_billing.py:12 — billing_api_key: SecretStr = Field(default="", ...)
  why this matters: empty-string default survives missing config without surfacing the absence; the consumer will run with no key
+ 1 more finding on auth (CORS allowlist entry — semantic eval needed) — run `/posture-check auth` for full sweep
```

The deterministic finding (Rule A1) gets the full Shape-2 treatment; the LLM-judgment finding folds
into `+N more` because the bounded format favors the higher-confidence deterministic finding. The
escape hatch is the sweep.

## Anti-patterns in output

- **Restating the diff.** The output names what changed *about the surface*, not the patch.
- **Emoji beyond `⚠ / ⓘ / ·`.** A gate, not a notification system.
- **Multi-line "why this matters".** One sentence, verbatim from the vocabulary; fix long ones there.
- **Citing audits, PRs or tickets.** The output is self-contained; citations live in the vocabulary
  file the registry points at.

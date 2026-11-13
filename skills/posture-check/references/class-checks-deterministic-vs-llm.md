# Class Checks — Deterministic vs LLM Judgment

The load-bearing **cost discipline**: mostly deterministic, a small remainder LLM-judgment. Drift
toward LLM-heavy and the per-PR gate stops being cheap, developers ignore it, and the skill
collapses into security theater.

The rule: **try the ast-grep rule first; promote to LLM only when the class genuinely can't be
expressed syntactically.** A class that *could* be a rule but nobody wrote it is not an LLM class —
it's an unwritten rule.

## Class entry format

Each entry in a surface vocabulary (`thoughts/vocabulary/<surface>.md`) has:

- **Name** and **ID** (the surface's letter prefix + integer: `A1`).
- **Shape:** the syntactic or semantic signature, in one or two lines.
- **Why it kills:** one sentence, quoted verbatim in the output.
- **Typical severity:** `critical` / `high` / `medium` / `low`.
- **Check mode:** how the class is classified:
  - `deterministic` — the class has an ast-grep rule (first section below)
  - `llm` — the class needs an LLM pass (second section below)
  - `hybrid` — the rule catches the *primary* shape; an LLM pass catches the residual (a fail-open
    gate has a clean rule for the kwarg, but "is this gate one that *should* fail open?" is LLM
    territory)

Assign the mode from whether the `Shape:` line is syntactically graspable. *"Missing argument"* and
*"polarity inversion of a kwarg"* are deterministic; *"the allowlist excludes the production
domain"* is LLM.

---

## Deterministic checks — five starter auth classes

Each maps to a class in an auth taxonomy. Patterns are starting points: tune them as real fires
accumulate. Each is an `ast-grep run` invocation, so it lifts straight into a script. Patterns use
meta-variables (`$X`, `$$$`) for arbitrary subtrees, and these are Python-specific; TS/JS
equivalents belong in a separate vocabulary.

### Rule A1 — Empty-string env default (`default=""` on a required secret)

**Maps to:** *an empty-string default on a config-required secret survives missing config without
surfacing the absence*.

```bash
ast-grep run -l Python -p 'Field(default="", $$$)' --paths src/settings/
```

**False-positive guardrail:** only fields typed `str` or `SecretStr` and not `Optional[...]`. The
pattern catches the syntactic shape; a second pass reads the surrounding context and drops
genuinely-optional fields. **Diff scope:** fire only when the matched line is **added**
(`git diff -U0 main...HEAD` against the file).

### Rule A2 — Fail-open feature-gate polarity (`default_if_unavailable=True`)

**Maps to:** *a feature gate fails open on outage instead of closed; the intended safety behavior is
inverted*.

```bash
ast-grep run -l Python -p 'check_gate($$$, default_if_unavailable=True, $$$)'
ast-grep run -l Python -p 'check_experiment($$$, default_if_unavailable=True, $$$)'
```

The failure mode is literally the kwarg value `True`. The semantic question (*should* this gate
fail open?) is the hybrid residual. **Diff scope:** added lines only. A pre-existing `=True` is
status quo; the gate is for *new* instances and *new combinations*.

### Rule A3 — Missing `verify_aud=True` on JWT decode

**Maps to:** *a JWT decoded without audience verification; a token issued for service A is silently
accepted by service B*.

"Call missing a kwarg" needs two passes: match all `jwt.decode($$$)` calls
(`ast-grep run -l Python -p 'jwt.decode($$$)' --json`), then filter out those whose kwarg list
contains `verify_aud=True`. A pragmatic single-pass alternative (known false-negative on multi-line
calls):

```bash
git diff main...HEAD | rg '^\+.*jwt\.decode\(' | rg -v 'verify_aud\s*=\s*True'
```

Whether *this* decode context needs audience verification (a test fixture doesn't) is the hybrid
escalation. **Diff scope:** added lines only.

### Rule A4 — Missing webhook event-id dedup (idempotency guard)

**Maps to:** *a webhook handler processes without checking the event id against a dedup store;
replays cause duplicate side-effects*.

Absence-detection, two heuristics combined:

```bash
# 1. Webhook route handlers with no reference to a known dedup helper
ast-grep run -l Python -p '@router.post($$$); def $H($$$): $$$' \
  --paths src/routes/webhooks/ --json \
  | jq '.[] | select(.text | test("was_processed|idempotency|mark_seen") | not)'

# 2. Handlers that accept event_id but never use it as a lookup key
ast-grep run -l Python -p 'event_id: str' --paths src/routes/webhooks/
```

The list of known dedup helpers is maintained *per repo*: it lives in the surface's vocabulary entry,
not in the rule. Whether a handler's side-effects warrant dedup at all is the hybrid escalation.

### Rule A5 — Sub-app missing parent middleware parity

**Maps to:** *a sub-app mounted at `/foo` doesn't inherit the parent app's middleware stack (auth,
CORS, rate-limit); requests to `/foo` bypass the parent's gates*.

```bash
ast-grep run -l Python -p 'app.mount("$PATH", $SUBAPP, $$$)'
# then compare $SUBAPP's middleware stack to the parent's
```

Mount-exists + middleware-count-mismatch is graspable from the AST. Whether the missing middleware is
load-bearing for *this* sub-app (health endpoints and static assets are intentionally unauthenticated)
is the hybrid escalation. **Diff scope:** fire when the diff *adds* a `.mount(...)` OR *removes
middleware* from an already-mounted sub-app.

---

## Skill-shipped class — `authority-mirrored-at-insert-only`

This class ships with the skill, not with a surface vocabulary, and applies on every tier-1 surface
whatever the repo's vocabulary says.

- **Shape:** a role, scope or entitlement copied from an external identity (an IdP flag, a tracker
  `admin`, a token claim) is written when the row is inserted, and no update path writes it again: no
  UPDATE, upsert (`ON CONFLICT … DO UPDATE SET`) or MERGE on that table sets the column.
- **Why it kills:** an authority copied from an external identity at insert never follows a later
  grant or revocation at its source, so a promoted user stays powerless and a demoted one keeps the
  power.
- **Typical severity:** High. Critical when the authority gates money, signing keys or data deletion.
- **Check mode:** hybrid.

**Deterministic half.** For each authority column the diff writes in an INSERT, search the repo for
a write of the same column on the same table by any other statement:

```bash
rg -n 'INSERT INTO <table>' src/                                  # the insert, with its column list
rg -n 'UPDATE <table>|ON CONFLICT.*DO UPDATE|MERGE INTO <table>' src/   # candidate refresh paths
```

A finding is new when the diff adds a line of the INSERT, or adds an UPDATE of the table that leaves
the column out (a refresh path built with the wrong field set). `SET col = COALESCE(col, ?)` and
`ON CONFLICT DO NOTHING` never overwrite, so they are not a re-sync. `.sql` files, `migrations/`
paths and seed files are never scanned: bootstrap rows are insert-only by design. A column the name
misleads on (a free-text descriptor, an append-only audit row nothing reads in a decision path) is
exempted by a `posture-ignore: authority-mirrored-at-insert-only` comment on the INSERT's lines or a
comment-only line directly above it.

**LLM residue** (one dispatch, the prompt below, when the diff writes an authority field the search
cannot see): ORM or query-builder writes (`db.insert(t).values({ role })`); column lists built at
runtime or SQL split across strings; an UPDATE of the column that exists but is unreachable from the
refresh path (an admin-only route); `CASE` updates; and tables where the role is an immutable fact by
design (history, audit, invites), which are a NO.

**Never a question on a tier-1 surface.** A fire of this class is a finding to fix in the PR, or an
issue filed and linked from the gate receipt or hand-back before the PR leaves review. Never phrase it
as "Should `join` re-sync the role on every sign-in?" in a hand-back: that question has no owner and
dies at the merge.

---

## LLM-judgment checks — the residual

Classes whose `Shape:` can't be expressed syntactically. The LLM's job is *narrow*: one yes/no
question per class, not a free-form audit.

### When to escalate

A class is LLM-mode when the shape requires any of:

- **Semantic intent** — is this gate one that should fail open? Is this CORS allowlist entry actually
  one of our domains?
- **Multi-component combination** — a new `allow_credentials=True` route in a file where
  `allow_origins=["*"]` already exists; neither line alone is wrong
- **Cross-tenant scope** — does this query filter by the tenant id in every code path?
- **Dataflow tracing** — does this user-controlled string reach a SQL query unsanitized?

### The dispatch

One focused subagent **per LLM-flagged class** in the touched surface's vocabulary, with this prompt
shape:

```
You are checking ONE class for ONE diff.

Class: <name and ID from the vocabulary>
Shape: <verbatim from vocabulary>
Why it kills: <verbatim>

The diff (added lines only):
<git diff -U0 main...HEAD on the surface files>

The surface as it currently stands:
<concatenated surface files OR pointer to read them>

Answer in one line + 1-line evidence:
1. Does this diff introduce a NEW instance of this class? YES / NO / UNCLEAR
2. Does it COMBINE with existing surface state to produce a new scenario?
   YES / NO / UNCLEAR
3. If YES to either: cite the file:line of the offending line(s).

Constraints: one yes/no per question, no preamble. UNCLEAR is valid — say
what would resolve it. If neither: emit nothing. Silence is the right output
for a clean diff.
```

### Cost discipline

- **One agent per class**, not per surface: the questions are independent, and per-class parallelism
  keeps wall-clock bounded.
- **Soft cap 5 LLM classes per surface per PR.** More than 5 flagged → top 5 by `Typical severity`
  run; the rest emit *"+N classes deferred — escalate to a full surface audit"*.
- **No retries.** A timed-out or garbled agent emits *"check timed out — escalate to a full surface
  audit"* and the skill moves on.

### Worked example — semantic CORS allowlist evaluation

The deterministic rule catches gross anti-shapes (`allow_credentials=True` + `allow_origins=["*"]`,
an unanchored regex). The LLM pass takes a new `allow_origins` entry and answers: a legitimate
domain the org owns (against the repo's known-domains reference)? A team-anchored preview URL? Or a
wildcard or external domain that shouldn't be there? Token cost is small, well under budget.

---

## Promotion / demotion

- **LLM → deterministic** — a hybrid class that fires 5+ times usually crystallizes a writable
  ast-grep shape. Move it.
- **Deterministic → LLM** — a rule with >30% false positives over its first 10 fires is too broad;
  narrow it with a second-pass filter or move it.

Both directions update the vocabulary's `Check mode:` field.

## Future ast-grep candidates

Worth writing once a surface vocabulary names them: a missing dependency annotation on a route handler
argument; a token validated with `verify=False`; a string secret with no `min_length=1` constraint; a
middleware registration order (CORS-before-auth vs after), which is syntactically observable.

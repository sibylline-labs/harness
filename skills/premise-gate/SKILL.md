---
name: premise-gate
kind: gate
description: Pre-scope premise-observation gate — before a plan is built, name the load-bearing premises and observe each one directly (a living-docs or Canon lookup, an on-chain eth_call, gh pr diff of a merged contract, a storage probe) so an inverted or unobserved premise surfaces before it shapes the work. Use before planning, before plan-review or prd-review, or when a plan rests on how a substrate behaves.
---

# Premise Gate

A **premise** is load-bearing when its falsity would **restructure** the work — not
re-parameterize it, restructure it. This gate makes the rule `premise-observed-not-inferred`
executable: every load-bearing premise carries an **observation**, or an explicit
`unobserved` tag, before a plan is built on it.

An **inverted premise** — the ticket says "unify on the `0x100` precompile", the chain says
`0x100` is dead — is the failure this gate exists to catch. It is cheap here (one `eth_call`)
and expensive later (a descope, a prod incident).

## Step 1 — Name the load-bearing premises

List the premises the plan will stand on. A premise is load-bearing when a NO answer changes
which files are touched, which service is called, where a trigger fires, or the response
shape — not a variable name. Where premises hide: how a verifier/precompile/contract behaves
on a specific chain; a cross-repo request/response contract; a dependency's on-disk or
runtime shape; a storage/namespace model; a trust boundary two operations share.

For a detector or lint plan, "the escape set is enumerated" is a load-bearing premise. Its
observation is the plan's escape catalogue (≥15 shapes), red-teamed by an agent before any
code, with a source table naming each source's owning layer (`work` plan template; rule
`work-at-the-owning-layer`). Without the catalogue, the premise is unobserved.

Done when: each premise is a falsifiable statement, it names the **runtime path** it must
hold on (the binding, driver, tree or environment the planned code will actually execute
through), and you can name the single observation that would falsify it. A premise you
cannot falsify is not yet named sharply enough.

## Step 2 — Consult the living docs first

When the org uses Socrates, run `eris socrates consult --canon` (or `--brief` for Canon, the
1-Pager, Load-Bearing Decisions, Key Assumptions, retro findings and practices; add
`--project <name>` when the org enrols several projects) and ask whether each premise is
already settled in the living docs or Canon — a **Load-Bearing Decision**, a **Key
Assumption**, or a Retro Finding — and whether that entry cites an observation or only a
spec/sibling/design doc. A substrate claim in Canon earns trust only when it cites the
observation that grounds it. An org with no Canon doc gets a refusal with a settings link:
"no Canon / not confirmed" is a valid answer, so treat every premise as absent and go to
Step 3; never invent a house default. A repo that does not use Socrates skips to Step 3.

- Cited by an observation → inherit it; record the citation as this premise's source, and
  compare the instrument it cites with this plan's runtime path (Step 3).
- Present but grounded only in a spec/PRD/sibling → treat as **unobserved**; it needs a fresh
  observation in Step 3.
- Absent → Step 3.

Done when: every premise is marked settled-by-observation, settled-by-inference, or absent.

## Step 3 — Observe the substrate

For every premise not already grounded by an observation, run the **cheapest authoritative
check on the substrate itself** — not the spec, not a sibling, not the plan:

- On-chain address / verifier / precompile → `eth_call` a **canonical known-valid vector** on
  the **target chain**; record the return. (`no-exec-from-tmp`: write any probe to
  `./data/scratch/`, run it there.)
- Cross-repo contract → `gh pr diff <n> --repo <owner>/<repo>` (or read the merged schema by
  SHA) for the request/response shape the plan sends.
- Storage / bucket / alias / namespace model → list the actual objects/aliases per artifact
  class; probe each class separately.
- A decision only a human owns → ask the owner, one line.

### Name the instrument

A reading is a fact about instrument plus subject. Beside every reading, record the
instrument that produced it (the exact command, client, driver or environment) and compare it
with the Step 1 runtime path on the dimensions the premise depends on: client or driver,
version, config, tree, privileges, data. Flag the comparison:

- **same** — the instrument is the runtime path, or differs only where the premise does not
  depend on it (say where, in a few words).
- **differs: `<how>`** — a plausibly different answer on a dimension the premise depends on.
- **unknown** — you cannot say what differs. Treat it as `differs`.

Clients over one engine disagree. With a trigger in play, an UPDATE whose AFTER UPDATE
trigger writes two more rows reads 1 through SQL `changes()` and a Python driver's `rowcount`,
and 3 through another runtime's `run().changes` (one probe, that trigger shape only). A value
measured through a deploy tool's CLI is not the Worker's database binding's value. So a
`differs` or `unknown` reading is evidence about the instrument, not the runtime: the premise
stays `unobserved`, the cell holds `<value> via <instrument>`, and the resolving check is the
same probe through the runtime path. A plan line copies the reading with its instrument,
never the bare value.

A **negative** (`no prior art`, `nothing calls X`, `no such export`) is a reading too, and
the weakest kind: a zero is a fact about the search's scope. Its row pastes the exact
command, the directory it ran in and the raw hit count. Where the target could sit outside
what the instrument sees (a glob, an ignore file, another repo, branch or generated tree),
also paste one control in the same scope that must hit; a zero without its control is
`unobserved`.

Tag each premise **observed** (instrument + command + result is its source, runtime path
`same`), **unobserved** (name the one check that would confirm it; includes a reading from a
different instrument), or **inverted** (the observation contradicts the premise).

Done when: every load-bearing premise carries an observation source with its instrument, or
an `unobserved` tag — none rest on inference.

## Step 4 — Verdict

Emit a **premise ledger** and a verdict (surface-specific design invariants and stack checklists run next in `/plan-review`):

| Premise (runtime path) | Observation source: instrument → reading | Instrument vs runtime path | Status |
|---|---|---|---|
| … | `eth_call … → 0x…01` · `gh pr diff #… → dat required` · Canon LBD #… | same | observed |
| `changes` is N (Worker D1 binding) | `wrangler d1 execute … → N'` | differs: CLI, not the binding | unobserved: re-run through the binding |
| nothing calls `sym` (`apps/`) | `rg -n sym apps/ → 0 hits`; control `rg -n <neighbour> apps/ → ≥1 hit` | same | observed |

The third column is `same` / `differs: <how>` / `unknown`; the last is `observed` /
`unobserved` / `inverted`.

- **CLEAR** — every load-bearing premise observed on its runtime path; safe to build the
  plan.
- **RESOLVE FIRST** — one or more premises inverted or unobserved (a reading through a
  different instrument counts as unobserved); name each and the check that resolves it.
  Planning on them now is building on inference.

When running on an issue `<KEY>`, write the premise ledger and verdict to
`thoughts/shared/premise/<YYYY-MM-DD>-<KEY>.md` in the target repo (or to `$G/premise.md`
where `G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"` on a `linear-only` run with no git
repo diff) — never inside the plan file, which `/plan-review` later amends.

## Step 5 — Record the Gate Receipt

Commit and push `thoughts/shared/premise/<YYYY-MM-DD>-<KEY>.md` on the issue's branch before
running `eris gate record` (it refuses an uncommitted in-repo artifact with `"commit and push
first"`), then record the receipt against that note (never the plan). The receipt binds the
note's sha256, so once recorded the note is write-once:

```bash
git add thoughts/shared/premise/<YYYY-MM-DD>-<KEY>.md
git commit -m "docs(premise): record premise ledger for <KEY>"
git push
eris gate record premise-gate --issue <KEY> --verdict <PASS|BLOCKING> \
  --artifact thoughts/shared/premise/<YYYY-MM-DD>-<KEY>.md \
  --doctrine <doctrine file> --impact <class> \
  --evidence "<N> premises observed on runtime path (<summary>)"
```

On a **`linear-only`** run (no git repo diff), write `$G/premise.md` inside the git dir
and record without `git commit` or `git push` (`eris gate record` stores `{ _tag: "file" }`
plus a gzip+base64 `artifact.copy` with the receipt):

```bash
G="$(git rev-parse --absolute-git-dir)/eris/<KEY>"; mkdir -p "$G"
eris gate record premise-gate --issue <KEY> --verdict <PASS|BLOCKING> \
  --artifact "$G/premise.md" \
  --doctrine <doctrine file> --impact <class> \
  --evidence "<N> premises observed on runtime path (<summary>)"
```

- `--verdict` is `PASS` for **CLEAR** and `BLOCKING` for **RESOLVE FIRST**.
- With no issue `<KEY>`, skip the receipt and say so in one line.
- Keep the comment id `record` prints for the run's final `--expect`.

## Boundary

This gate **reads** Canon and **observes** the substrate; it does not write Canon. When an
observation should become a Load-Bearing Decision, hand it to `eris socrates submit` (score it
first with `eris socrates classify`; `--title`, `--statement`, `--source <url>`, `--evidence <one line: why, then repo@sha:path#L or a PR link>`). The read-only
agent form of this gate never runs `submit`; it hands the decision to its parent. You surface
the premise; Socrates records it.

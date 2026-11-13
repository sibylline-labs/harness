# Surface Registry Format — `.claude/surfaces.yml`

The contract for declaring a tier-1 surface in a consuming repo. Lives at the repo root as
`.claude/surfaces.yml`. Read on every run to answer two questions:

1. **Did this change touch a surface I care about?** (file globs → surface name)
2. **What classes apply to that surface?** (surface name → vocabulary file)

Registering a surface here is the act that puts it under per-PR gating. That is deliberate:
fail-closed on unregistered surfaces means new code can't silently escape the gate.

## Schema

```yaml
# .claude/surfaces.yml

surfaces:
  <surface-name>:                     # short, lowercase, kebab-case
    paths:                            # repo-relative globs (non-empty)
      - <glob-1>
      - <glob-2>
    class_taxonomy: <path>            # vocabulary file
                                      # default: thoughts/vocabulary/<surface>.md
    severity_floor: <level>           # optional, default: "low"
                                      # "critical" | "high" | "medium" | "low"
    description: |                    # optional, free-form
      Why this surface is tier-1; non-obvious paths that belong to it.
```

Keep the file plain YAML: mappings, sequences, quoted or plain scalars, comments. No anchors or
aliases, no merge keys, no duplicate keys, no fields beyond those above. A registry that breaks
that is registry rot, and a run surfaces the parse error verbatim instead of guessing.

## Fields

### `<surface-name>`

Short, lowercase, kebab-case: `auth`, `webhooks`, `cors`, `feature-gates`, `api-mounting`,
`secrets`. Used as the argument to sweep mode (`/posture-check auth`), the vocabulary filename
(`thoughts/vocabulary/<name>.md`), and the label in the bounded output. Pick a name that reads
cleanly as a noun in all three. `auth` is fine; `auth-and-cors` is not (split it).

### `paths:`

Repo-relative globs, matched against the changed-file list from `git diff --name-only main...HEAD`.

- `*` matches within a single path segment (does NOT cross `/`)
- `**` matches zero or more path segments (DOES cross `/`)
- `?` matches a single character
- Brace alternation `{a,b}` is supported
- Case-sensitive
- A path may match multiple surfaces — the file is gated by all of them, by design (`cors.py` may
  be both `auth` and `cors`)
- Empty `paths:` is invalid; comment the surface out instead

### `class_taxonomy:`

Pointer to the vocabulary file loaded when this surface is touched. Default:
`thoughts/vocabulary/<surface-name>.md`. Its per-class entry format (Name, Shape, Why it kills,
Typical severity, Check mode) is in
[`class-checks-deterministic-vs-llm.md`](class-checks-deterministic-vs-llm.md). Class IDs use the
surface's single-letter prefix + integer (`A1`, `A2` for auth).

If the referenced file doesn't exist, the skill checks the skill-shipped classes only and emits a
warning line: *"surface 'auth' has no vocabulary at `thoughts/vocabulary/auth.md` — checking
shipped classes only."*

### `severity_floor:` (optional)

Quiet the skill below a given severity. Default `low` (everything emits); common production
setting `medium`. Values `critical` / `high` / `medium` / `low`.

### `description:` (optional)

Free-form prose (`|` block scalar). Read on registry inspection; not load-bearing.

## Worked example — an auth surface

```yaml
surfaces:
  auth:
    paths:
      - src/settings/secrets_*.py
      - src/http/cors.py
      - src/routes/webhooks/**
      - src/auth/deps.py
      - src/app/mount.py
    class_taxonomy: thoughts/vocabulary/auth.md
    severity_floor: medium
    description: |
      Tier-1 auth surface: secret loading, CORS middleware, webhook handlers, the auth
      dependency tree, and the sub-app mount point. The cumulative posture here is fragile
      even when individual diffs look clean.
```

**Tuning note — CORS regression detection.** If `cors.py` is already hardened (static allowlist,
anchored regex, HTTPS-only), rules on this surface fire on *introduced* anti-shapes
(`allow_credentials=True` + `allow_origins=["*"]`, an unanchored regex, an exposed sensitive
header), not on the existing hardened state. Semantic allowlist evaluation ("is the new entry
actually one of our domains?") stays LLM-judgment.

## Multi-surface changes

One bounded output **per touched surface** (3 surfaces → up to 9 lines, still bounded). Output on
3+ surfaces from a single PR is a strong split signal — the final line becomes: *"PR touches N
tier-1 surfaces — consider splitting before merge."*

## CI guards (recommended once the registry is live)

1. **Every `paths:` glob resolves to ≥1 file.** A glob matching nothing means the file moved
   (registry rot) or the glob is wrong. Fail CI.
2. **Every `class_taxonomy:` file exists.** A missing vocabulary silently demotes a surface to
   shipped-classes-only; the skill warns at runtime, but CI should catch the demotion.

## Anti-patterns

- **Over-registering.** A surface firing on >30% of PRs is too broad. Split it.
- **Under-registering.** A 1-glob surface (just `cors.py`) misses adjacent code (the allowlist, the
  regex helper). Scope from where the surface actually lives.
- **Overlapping names.** `auth` and `auth-deps` confuse; use orthogonal names or merge.
- **Taxonomy outside `thoughts/vocabulary/`.** The default path is load-bearing: the skill finds it
  there. Override only for legacy repos.

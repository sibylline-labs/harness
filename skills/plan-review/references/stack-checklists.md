# Stack Surface Checklist (`plan-review` Step 3)

The repo's own contract outranks this list. Read its `AGENTS.md` / `CLAUDE.md` and its root
`eris.yaml` `ci.local` before you judge a plan's verification, and run any repo-specific
checklist the repo ships (a `.claude/rules/` file, a docs page) in addition to this one.

## Any stack

- **Verification commands come from the repo.** Every automated success criterion in the plan
  names a command the repo already declares (`ci.local` gate, `AGENTS.md` command,
  `Makefile` / `package.json` / `pyproject.toml` / `go.mod` target), never `pytest` / `ruff` /
  `bun test` by habit. A command that no file in the repo defines is a failed criterion.
- **Install is part of the gate.** A dependency install, module download or cache restore lives
  inside the gate that needs it, or the plan names it as an explicit setup step.
- **Linters and type checks come from the repo.** Judge the plan against the repo's formatter and
  linter config. Adding a rule or tool follows the repo's existing config file, not a parallel one.
- **Path and shell hygiene.** Never hardcode a home-directory path (resolve siblings relative to
  `__file__` / `BASH_SOURCE[0]`); never write and execute scripts from `/tmp` or `$TMPDIR`; strip
  ANSI colour codes or use literal binary paths in test oracles; avoid shell function names that
  collide with common aliases (`run`, `f`).
- **Parser and config fidelity.** JSONC/YAML readers preserve BOMs, comments and trailing
  newlines where the upstream tool accepts them.
- **Cross-repo contracts.** A request/response contract owned by another repo is pinned by commit
  SHA or a contract test, never paraphrased.
- **Test isolation.** No process-global mocks of a shared module without restoring the real
  exports; prefer dependency injection or real pure functions.
- **Public surface changes.** A touched API route, schema or CLI flag regenerates its published
  spec or docs in the same change, and names the consumers that read it.
- **Security-sensitive surfaces.** A change touching auth, secrets, CORS or webhooks schedules
  `/posture-check`.
- **Frontend.** Cover empty, initial-loading, background-refresh and error-recovery states; no
  leftover mock data or fake timers; hydration-safe formatting; no interactive element nested in
  another interactive element.

## No sibling precedent

When the repo has no nearest sibling for the change, say so in the plan and take the shape of the
repo's closest existing module. Never take it from a plan, a rule's example or a design doc.

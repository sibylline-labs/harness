# Stage: emerging-tech research

A plan written from memory about a library the model can't know is the failure this stage stops. It runs after the plan stage has named its dependencies and before the premise gate.
It produces a cache and a receipt. `/plan-review` judges both against `emerging-tech-research@1`
([`emerging-tech-research`](../../emerging-tech-research/SKILL.md)).

## Trigger

List every library the plan adds, upgrades or calls an API it has not called before, with the
version it will run. Run the trigger from the target repo's root, against its lockfile:

```bash
uv run --script ~/.claude/skills/work/scripts/emerging_tech.py \
  --lockfile bun.lock effect@4.0.7 zod@4 httpx
```

- Each row reads `<lib>  fire|quiet  <reasons>  <installed>  <cache dir>  present|missing|-`. The
  reasons are `missing` (not in the lockfile), `major-above` (requested major over the installed one,
  0.x minors counted), `released-after-cutoff` and `release-unverified` (the registry lookup failed).
- Every row `quiet`: the stage is skipped. Say so in the premise ledger (`thoughts/shared/premise/<YYYY-MM-DD>-<KEY>.md`) with the command.
- Exit 1: a fired library has no cache. Build it below, then re-run until exit 0.
- `--offline` skips the date leg. Use it only when the registries are unreachable, and say so in the
  ledger: a skipped leg is not a quiet one.
- The lockfile's name picks the reader: `bun.lock`, `bun.lockb`, `yarn.lock` (classic or berry),
  `package-lock.json`, `pnpm-lock.yaml`, `uv.lock`, `go.mod` or `go.sum`. `bun.lockb` is binary and is
  read through `bun` (it must be on PATH). A Go library is its module path (`github.com/google/uuid@v1.6.0`).
  A lockfile holding several copies of a package counts its highest.
- A repo with several ecosystems (a Go service beside a yarn workspace) runs the trigger once per
  lockfile.

## Cache

One directory per fired library at `research/<lib>@<exact version>/` in the target repo:

- `README.md`: the pinned version, today's date, the load-bearing APIs the plan uses, and what the
  probe proved.
- Source excerpts, pruned to the passages the plan relies on, each with its URL and retrieval date.
  Prefer the package's own types (`.d.ts`, `py.typed` stubs) and changelog over blog posts.
- `probe.txt`: the probe command and its full output.

**Shared cache.** The trigger also accepts `<harness root>/research/<lib>@<exact version>/README.md`
(the harness checkout's `research/` directory; override with `--shared-research-dir`)
as present, and prints that path in the cache column. A library that fires in every repo (the
pinned `effect`, released after the model cutoff) is cached there once, so no product repo carries
a `research/` tree for it. The shared cache replaces the per-library docs and excerpts only: each
run still executes one load-bearing API for its plan, captures the output in `probe.txt`, and records
its own receipt. A repo-local cache wins when both exist.

A `research-agent` can build the cache (it preloads the rubric). Hand it the library, the version and
the APIs the plan leans on, and the directory to write.

## Execute one load-bearing API

Install the pinned version in a scratch project inside the repo's gitignored working dir, not in
`/tmp`, and call the API the plan depends on most. Run it inline (`bun -e '…'`, `python3 - <<'PY'`)
and capture the output in `probe.txt`. Reading the docs is not executing: the rubric returns
`AMENDED` until the probe has run, and `BLOCKING` if the plan relies on an API nobody ran.

## Receipt

Commit and push each fired library's `research/<lib>@<version>/` cache on the issue's branch before
recording, then record one receipt per fired library. The probe output goes inline
through `--log`:

```bash
git add research/<lib>@<version>/
git commit -m "docs(research): cache <lib>@<version> for <KEY>"
git push
eris gate record emerging-tech-research --issue <KEY> --verdict PASS \
  --artifact research/<lib>@<version>/README.md --rubric emerging-tech-research@1 \
  --log research/<lib>@<version>/probe.txt --evidence "<probe command> -> <the line it proved>"
```

Use `AMENDED` when the cache is present but the probe has not run yet, and name the API that is
outstanding. The premise ledger (`thoughts/shared/premise/<YYYY-MM-DD>-<KEY>.md`) cites each receipt's comment id.

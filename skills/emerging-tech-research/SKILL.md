---
name: emerging-tech-research
kind: rubric
version: 1
description: Rubric emerging-tech-research@1 for research on a library the model can't know. The version is pinned, sources dated and pruned into a `research/` cache, one load-bearing API executed with its output. Use when a plan depends on a library missing from the lockfile, released after the model cutoff, or a major above the installed one.
---

# emerging-tech-research@1

**Trigger (mechanical):** a plan depends on a library that is missing from the lockfile, was
released after the model's knowledge cutoff, or is a major version above the installed one.
**Producer:** the research stage (`research-agent`).
**Judge:** `plan-review`, before the plan that depends on it is receipted.

The cache lives at `research/<lib>@<version>/`: a `README.md` with the pinned version and
the date, the pruned source excerpts each with its URL and retrieval date, and the executed
probe with its output.

## Verdicts

- **PASS**: the version is pinned, the cache holds dated and pruned sources, and one
  load-bearing API was executed, with its output in the cache.
- **AMENDED**: the cache is present, but an API the plan leans on has not been executed yet.
  The judge names it, and the plan adds the probe before the phase that uses it.
- **BLOCKING**:
  - the trigger fired and there is no cache;
  - the plan relies on an API nobody executed;
  - the sources are undated, so their currency can't be checked.

## Examples

- PASS: `research/opentui@0.5.1/`: pinned; 4 dated excerpts; `bun run probe.ts` output
  shows `SchemaTextView` rendering without a YAML parser.
- AMENDED: `research/effect@3.12/` has the docs, but `Layer.scoped` was only read, not run.
- BLOCKING: a plan uses a workflow SDK's `context.invoke` from memory; no cache, no probe.

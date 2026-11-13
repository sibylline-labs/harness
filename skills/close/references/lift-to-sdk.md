# Stage: lift-to-sdk

File each SDK gap that was built locally in more than one place as a suggestion against the SDK that
should own it. The input is the `lift-candidate` marker listing from `work`'s `sdk-check` stage
(`rg -n 'lift-candidate:' <repo>`). It runs in the `tpm-merge` and `next` profiles.

All Linear writes go through `/linear-workflow`.

## 1. Read the mode

The close reads `close.lift-to-sdk` from the active doctrine posture (`eris doctrine gates`) and runs
this stage only for `on` or `file-only`. For `off` it does not call the stage:
`eris gate check --profile <tpm-merge|next>` records the doctrine `SKIPPED` itself.

| Mode | What the stage does |
|---|---|
| `file-only` | files the suggestions; nothing downstream builds them |
| `on` | files them and prints a `follow-up: <KEY> <title>` line per filed suggestion, which the scoped `/tpm` report reads under `next`, or which `tpm-merge` lists on the ledger's `follow-ups:` line for the TPM |

The stage never launches a session itself.

**Done when:** you have the mode and the repo checkouts the session's work touched.

## 2. Scan and judge

List every marker in every repo the session touched (call sites add up across repos):

```bash
rg -n 'lift-candidate:' <checkout> [<checkout> ...]
```

The pattern is the first token after the colon; an optional dash-led note follows. Group the markers
by SDK (the SDK for the marker's language) and by pattern, and judge each group:

- **PASS**: one pattern at two or more call sites (each named `file:line`) that collapses the design
  space into a single primitive. It is filed, not built.
- **AMENDED** (one call site): left alone. The marker stays until a second site appears.
- **BLOCKING**: a speculative abstraction with no current consumer; a lift built in the consumer
  repo instead of filed against the SDK; one issue bundling several patterns.

**Done when:** every group has a verdict.

## 3. File each PASS

One suggestion per PASS pattern, into the SDK's own Linear project (find it with `list_projects`),
under that project's day Epic titled `[lift-to-sdk] <SDK project> — <YYYY-MM-DD>` (found by title,
created on the first filing of the day; the workspace's existing `Epic` label).

- **Hash.** The suggestion carries a `hash: <12 hex>` line: the first 12 hex characters of the
  sha256 of the SDK key and the pattern, joined by `\037`. A hash that already sits on any issue in
  the project, in any state, is a `duplicate` and is not filed again; a canceled suggestion is how a
  lift is rejected.
- **Cap.** An Epic takes at most 5 suggestions a day; the rest are `capped` and file on a later day,
  since their markers stay.
- **Body.** The pattern, each call site as `file:line`, and the primitive it collapses into.
- **Label.** The existing `Improvement` label.

**Done when:** every PASS group is filed, duplicate or capped.

## 4. Record the receipt

The gate is required in `tpm-merge` and `next`, so record it even when nothing files. Write the
judged groups and outcomes to `lift-to-sdk.json` (or any scratch file under `$RUN`) first.

```bash
eris gate record lift-to-sdk --issue <KEY> --verdict PASS --artifact lift-to-sdk.json \
  --doctrine <doctrine file> \
  --evidence "filed: <KEY> linear-pagination (3 sites)" \
  --evidence "duplicate: <pattern>; capped: <pattern>; amended: <n> single-site markers"
```

With nothing filed, one line: `--evidence "no-op: <n> candidates, 0 PASS"`. On a Linear failure
record `BLOCKING` with the error line as evidence. Under `on`, hand the `follow-up:` lines to the
scoped `/tpm` report (`next`) or to the ledger's `follow-ups:` line (`tpm-merge`).

**Done when:** `record` printed the comment id.

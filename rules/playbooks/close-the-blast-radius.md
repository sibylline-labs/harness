# Close the Blast Radius

> **Playbook for** [`close-the-blast-radius.md`](~/.claude/rules/close-the-blast-radius.md): the resident core carries the statement, trigger and red flags; this file is the full body.

**A change is complete only when its entire blast radius (every reference, location, and consumer
that participates in it) is enumerated and closed as one unit.**

## Pattern

A change presents itself at one focal site: the file being edited, the component being created, the
module being refactored. Every surface makes the focal site feel like the whole change: the compiler
passes, the focal tests are green, the new file exists. But the sites that actually complete the
change live elsewhere: the YAML workflow and Dockerfile that reference the renamed variable, the
validator that silently strips the new schema field, the parent that must import and render the new
component, the adjacent files in the same diff. Those are exactly the sites no type-checker guards,
so a partial change ships green and fails silently, later, somewhere else.

The economics are constant: the enumeration (one grep before, one grep after) costs seconds; the
missed site costs a silent production failure or a review round. "Done" is therefore not "the focal
edit works"; it is "the enumerated radius is closed": every site found *before* changing anything,
every site changed or verified in the same unit (one commit, one edit, one verification pass), and
nothing left for a future session to discover.

The unit matters as much as the enumeration. A radius closed across several commits leaves
intermediate states where the change is half-applied, which is precisely what pre-flight hooks
(correctly) block, what reviewers flag, and what production experiences when only half deploys.

## The surfaces

| Surface | The sentence applied there |
|---|---|
| renames (vars, env vars, functions, fields) | grep every reference, especially non-type-checked files (YAML, env, Docker, shell), before committing |
| AI tool schemas | the input schema, the validator and the tool description update as one unit, or the field is silently stripped |
| functionality moves / absorptions | the old component, its exports and its dead state leave in the same commit the absorption lands |
| edits under pre-flight hooks | the radius must close in a single edit: the hook turns a half-applied change into a hard block |
| newly created components | the radius includes the consumer: verify the parent imports AND renders it, then see it on screen |
| PR-wide verification | the radius is every file in the diff: scan and test all of them, not just the focal module |

## Applying it on a new surface

1. Before changing anything, enumerate: grep for every site that references, consumes, or is fed by
   the thing you're changing. Include surfaces no tool checks: config, CI workflows, docs, env files,
   matrix entries, the parent that renders what you built.
2. The count from step 1 is the definition of done. Close all of it in one unit: one commit, one
   atomic edit where hooks demand it.
3. After changing, run the same enumeration again: zero remaining references to the old name, the
   deleted component, the unwired artifact.
4. Verify across the whole set, not the focal site: the change's tests, scans and rendered checks
   cover every enumerated file.

## Red Flags — class level

- You edited N sites without ever running the grep that says whether the total is N.
- The change touches a name, schema, or contract that non-type-checked files (YAML, env, Dockerfile,
  shell, docs) consume.
- "Done" was declared from the focal module's green signal while adjacent files in the same diff were
  never scanned.
- Something was created but nothing was checked for *consuming* it, or something was absorbed and the
  original still exists.
- A matrix or consumer list has M entries and you touched N < M of them.

## Related

A shared tool's radius is its *cross-context consumers*: exercise one real consumer from a foreign
repo, worktree or subagent before you close, because a green in the home repo cannot see callers it
does not own.

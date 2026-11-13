# The Codebase Is the Pattern Authority

> **Playbook for** [`codebase-is-the-pattern-authority.md`](~/.claude/rules/codebase-is-the-pattern-authority.md): the resident core carries the statement, trigger and red flags; this file is the full body.

**The codebase is the pattern authority; a secondhand description of it is checked against it before
it shapes code.**

## Pattern

Most code is written from a description of the codebase rather than the codebase: a plan's code
block, a generic rule's example names, a reviewer bot's suggestion, a generated doc, a design doc's
schema. Each is written by someone (often an earlier session of you) who was not looking at the
sibling file, so each is plausible, specific and quietly wrong about the local shape. The description
is also the thing already in your context, while the codebase costs a grep, which is why every
surface mints its own incident. The grep costs seconds. Skipping it produces a third convention, a
hallucinated contract or a defensively-correct change that contradicts the domain, and each of those
costs a review cycle.

## The surfaces

| Surface | The sentence applied there |
|---|---|
| implementation plans | the plan carries intent; adapt its code to sibling patterns and keep its vocabulary (ticket IDs, phases, decision labels) out of shipped and consumer-facing text |
| generic rules applied to a codebase | a rule's example names are shape, not contract; grep the sibling-most precedent and match it |
| automated code-review suggestions | a bot's defensive suggestion is checked against the domain model before it is accepted or rejected |
| generated API documentation | every header, status code, enum value and transition is traced to source before it ships |
| data artifacts handed over in a design doc | the doc owns the content and the repo owns the form; prefer the executable representation |
| greenfield repos, packages and SDKs | an empty repo mirrors its nearest sibling repo for directory structure, small single-responsibility files, extracted helpers, and first-wave docs (`README.md`, `CLAUDE.md`, a layout doc) |

## Precedence when they disagree

1. **Codebase conventions win**, except mid-migration: when the repo carries two substrates or its
   project has a live migration epic, the migration's target seam beats the convention of the file
   you are editing.
2. **Rules win over plans**: rules are cross-session, plans are session-local.
3. **Plans win only for a new domain** with no sibling to mirror.

## Applying it on a new surface

Name the description you are working from and who wrote it. Find the nearest sibling in the codebase
that already does the thing, using `rg`/`ast-grep` on the names and shapes the description uses, and
diff the two. Where they differ, the codebase wins unless you can say why it is wrong, and then that
reason goes in the PR.

## Red Flags — class level

- You are about to paste or transcribe a block from a document into the repo.
- A name, parameter or shape you are introducing has no precedent you can point to.
- The only justification for a line is "the plan / the rule / the reviewer / the doc said so".
- Consumer-facing text carries ticket IDs, phase numbers or internal decision labels.

## Sibling

[`premise-observed-not-inferred.md`](~/.claude/rules/premise-observed-not-inferred.md) governs whether
a *load-bearing premise* was observed; this rule governs whose *shape* wins once the facts are known.

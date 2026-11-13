# Plan Before Code, Not After

> **Playbook for** [`plan-before-code-not-after.md`](~/.claude/rules/plan-before-code-not-after.md): the resident core carries the statement, trigger and red flags; this file is the full body.

A plan committed after the code it describes is documentation, not planning. It serves no design
purpose because there's no checkpoint at which the plan could redirect the work.

## Pattern

A plan's value is the moment it creates between "we want to do X" and "here is the code". That
moment is when:

- The user can redirect (*"actually, let's not do step 5"*)
- Architectural drift is caught (*"step 3 disagrees with the existing pattern"*)
- Scope is questioned (*"do we really need step 7 in this PR?"*)
- The plan is validated against memory, skills, and codebase conventions

If the plan lands after the code, none of this happens. The plan is a transcription of decisions that
have already shipped. The reviewer reading it sees a polished narrative that ratifies whatever the
code does: the work could have any shape and the plan would still claim "this was always the design".

## DO

- **Under `/work plan`:** the `plan` stage commits `thoughts/shared/plans/<plan>.md` as the branch's
  first plan commit, pushes, and opens the issue's single draft PR (`gh pr create --draft`) before
  `/plan-review` and `/work implement` run, and `/plan-review` commits `## Gate Amendments` and binds
  its receipt to that commit SHA before code is written. This structurally guarantees the plan
  precedes implementation commits, so no manual timestamp check is needed on `/work` runs.
- **On ad-hoc branches or mid-PR pivots outside `/work`:** commit the plan before the first feature
  commit it describes. For ad-hoc plans, the plan timestamp must be **earlier** than the first
  feature commit it describes; if it isn't, flag the inversion before merging the PR.

```bash
# Plan first
git log -1 --format=%ai thoughts/shared/plans/<plan>.md
# Code second: the first commit on the branch that touches source
git log --reverse --format='%h %ai %s' main..HEAD -- src/ | head -1
```

## DON'T

- Write the plan retroactively to "explain what happened".
- Treat a plan as a deliverable in its own right (it's a process artifact).
- Add a plan to a PR after review feedback has already shaped the code: the plan won't reflect the
  as-built design honestly.
- Use a plan as a way to ratify a controversial architectural choice that wasn't validated up front.

## Verification (ad-hoc plans outside `/work` only)

Under `/work plan`, the `plan-review` receipt enforces plan-first ordering structurally. For an
ad-hoc plan created outside `/work`, run before opening the PR:

```bash
PLAN_FILE=thoughts/shared/plans/<plan>.md
PLAN_TS=$(git log -1 --format=%at -- "$PLAN_FILE")
FIRST_CODE_TS=$(git log --reverse --format=%at main..HEAD -- src/ | head -1)

if [ -n "$PLAN_TS" ] && [ -n "$FIRST_CODE_TS" ] && [ "$PLAN_TS" -gt "$FIRST_CODE_TS" ]; then
    echo "PLAN INVERSION: plan committed after code it describes"
fi
```

Adjust `src/` to the repo's source roots.

## When This Applies

- Ad-hoc plans landing in `thoughts/shared/plans/` or `thoughts/plans/` outside `/work plan`.
- Mid-PR plans created in response to scope changes (the temptation to retroactively plan a pivot is
  high).
- Plans created during retro or cleanup sessions.

## What to do if you've inverted

If the plan is already after the code:

1. **Don't pretend it was first.** Note in the plan's frontmatter: *"This plan documents work already
   shipped on commits X-Y. It is retrospective, not prospective."*
2. Or: delete the plan and treat the work as ad-hoc.
3. Or: treat the *next* phase as the planned work, and update the plan to describe what's still ahead.

The goal is to never have a plan that pretends to be planning when it's actually documentation.
Either the plan drives the code, or it follows the code and is honest about that.

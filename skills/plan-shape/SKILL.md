---
name: plan-shape
kind: rubric
description: plan-shape@1 — the criteria an implementation plan in thoughts/shared/plans must meet before code is written. Preloaded by `work` (its producer); judged by `/plan-review`.
---

# plan-shape@1

Judge: `/plan-review`, over one plan file. Producer: the `work` plan stage.

## Criteria

| # | Criterion | Fails when |
|---|---|---|
| 1 | **One-sentence change.** The Overview says in one sentence what changes (states, files, tokens) and names each term it interprets | the Overview is a paragraph of intent with no named files or states |
| 2 | **Premises observed.** Every load-bearing premise has an observation source; an inverted one is marked and the plan amended | a row says "should", "presumably" or cites only a doc |
| 3 | **Every invariant has a rung.** `## Invariants and Their Rung` has one row per invariant: rung, artifact, why not higher; a lint row says `severity: error` | an invariant lives only in prose, or a test holds what a lint could |
| 4 | **Red first.** Each new check names its observed red on unfixed main | "will fail" with no count |
| 5 | **Out of scope has destinations.** Each deferred defect names a filed issue or "not filed because …" | "follow-up" with no ID |
| 6 | **Phases are verifiable.** Each phase has success criteria split into automated (commands) and manual | "works as expected" |
| 7 | **No open questions.** Every decision is made before the plan is final | a `TBD`, `?` or "decide later" left in |
| 8 | **Mirrored fields have write paths.** A `## Mirrored-field write paths` table has one row per external field the plan stores (an identity-provider name, an IdP role, a token scope): its insert, update and revoke path, each a `file:function` or `none (reason)`; authority fields (role, scope, entitlement) are marked. A plan that mirrors nothing writes `none` | an authority field with update or revoke `none` and no reason, a mirrored field with no row, or the section missing |

## Verdict

- `PASS`: all eight hold.
- `AMENDED`: a criterion failed and the plan was changed to meet it in the same review.
- `BLOCKING`: a criterion fails and cannot be fixed in the plan (a premise is unobservable, a
  decision belongs to a human).

## Examples

PASS (criterion 3):

```markdown
| No handler imports the db module | lint | ast-grep rule `no-db-import-in-handlers`, `severity: error`, `make lint` | types cannot see imports |
```

FAIL (criterion 3, test where lint would hold it):

```markdown
| No handler imports the db module | test | test_no_db_imports walks the AST | — |
```

FAIL (criterion 5):

```markdown
| Retry storm on 429 | out of scope | follow-up |
```

FAIL (criterion 8, the refresh path leaves the authority out):

```markdown
| members.role | insert: members.ts:join | update: members.ts:refresh (name only) | revoke: none |
```

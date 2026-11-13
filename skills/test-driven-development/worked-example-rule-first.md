# Worked Example: A Rule Before the Fix

Read it when you want to see the rule-first loop run end to end.

**The defect.** Twelve `except sqlalchemy.exc.IntegrityError` handlers in ten files wrapped the service's `ctx.db.create` / `update` calls. The data-layer wrapper raises its own `IntegrityError`, which is not a subclass of SQLAlchemy's, so none of the handlers could ever run. They covered a slug-collision retry, an idempotent replay and eight other paths.

| Step | What happened |
|---|---|
| 1. Premise, executed | An in-process `DatabaseService` against sqlite inserted a duplicate: `isinstance(e, sqlalchemy IntegrityError)` was `False`, and `__cause__` was SQLAlchemy's. That was observed by running it, not by reading the source. |
| 2. Rule first | A ruff `TID251` `banned-api` entry for `sqlalchemy.exc.IntegrityError` and each alias that resolves to it. Every alias was confirmed with a probe. The message names the fix. |
| 3. See it fail | `ruff check --select TID251 .` found **52 hits** on the unmodified tree, against the ticket's guess of 5. Every hit was triaged as fixed, a scoped `per-file-ignores` for raw-engine scripts, or an inline `noqa` with a reason. `tests/**` was deliberately not blanket-ignored. |
| 4. Fix | Every handler switched to the wrapper's class, with control flow unchanged. The rule passed. |
| 5. Behaviour tests, only where no rule reaches | The slug retry asserts `create.await_count == 3`. A new test covers the replay that loses an insert race. Both were shown red with only the two handlers reverted, then green with the fix. The other handlers got no new tests, because the rule guards them. |
| 6. Tautology tests found | Nine existing tests in six files mocked `ctx.db` to raise SQLAlchemy's class, the exception the real call never raises. They had passed against dead code. That is the "mocks the very thing under question" failure mode. |

**The lesson.** The rule measured the real scope (52 hits where the ticket guessed 5), and it now prevents the class repo-wide. The mocked tests had certified the bug.

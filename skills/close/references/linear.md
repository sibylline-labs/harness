# Stage: linear

Every profile. Follow [linear sweep](linear-sweep.md). Observe the primary issue's auto-close rather
than assume it. Close each issue whose acceptance criteria the merged diff meets, and comment on each
one it only advances. Read each issue's full comment thread before judging it. Write through
`/linear-workflow`.

An open blocking ask on an issue is a hold. Done is refused, naming each ask id; leave the issue
open, report that id as the hold, and close it once the ask is answered (only a human withdraws a
one-way ask).

Record the actual effort on every issue the work closed: run `active_time.py`
(`/linear-workflow` § Estimates) and overwrite `estimate` with its `points`. Post the `effort:`
receipt line, then raise any parent below its children's sum. The `close-ledger` ledger comment
carries the receipt lines.

**Done when:** every issue row is Done with a receipt comment, or commented as partial with what
remains, and a re-read confirms each state. Every closed issue's `estimate` matches its `effort:`
line, and no parent the work touched sits below its children's sum.

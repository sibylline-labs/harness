# Yak watch

A recurring TPM pass over the yak queue that finds yaks worth expediting into a loop. Yaks are the
best evidence available of the impact the harness is having on operations.

## Sample two frames, every pass

1. **Hot clusters.** Rank every open `Yak` issue in Triage, Todo or Backlog by observation count
   (the latest `Occurrence count` in its comments), with the observations since the last pass as a
   tie-breaker. A cluster with 3 or more observations that no loop or PR covers is a candidate,
   however old its last update.
2. **New arrivals.** Yaks created or updated since the last pass.

Recency alone is not a frame: a cluster that keeps gaining observations without anyone filing a new
issue never appears in an "updated recently" list. A yak can sit in Triage for days with twenty
observations and never surface.

## Expedite bar

Expedite through a fresh `/work` session, or a single class-fix session for a cluster, only when the
yak meets at least one of these, and nothing contradicts a ruling the human has made:

- it hits work in flight;
- it has multiple observations;
- it blocks a gate or a peer TPM.

Fold same-class yaks into one better-scoped issue. Route yaks another TPM owns to that TPM.

## Report

The report names its frames: "N hot clusters checked (top: ABC-123, 20 obs); M new since HH:MMZ".
It then lists only the yaks acted on, each with its launch receipt (a session id or comment id).
"Nothing qualified" without both frames is not a valid report: an absence claim names its search and
a positive control.

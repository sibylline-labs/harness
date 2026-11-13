# Stage: socrates

Every profile. Dispatch a **separate subagent**, in parallel with `tpm-report` under `next`. The
mandate does not travel on its own, so put it in the brief word for word.

First observe enrolment mechanically, before any subagent: list the enrolled projects once and check
each ledger issue's `project.id` UUID (never the project name), with the block below (`<project.id>`
is the issue's project UUID, and `<enrolled label id>` is the id of the project label that marks a
project as enrolled in Socrates, from `list_project_labels`):

```bash
if ! eris linear projects --label-id <enrolled label id> --output json > "$RUN/enrolled-projects.json"; then
  echo "hold: read failed"
elif ! jq -e '(.projects | length) > 0' "$RUN/enrolled-projects.json" >/dev/null; then
  echo "hold: empty enrolment list"
elif jq -e --arg pid "<project.id>" 'any(.projects[]; .id == $pid)' "$RUN/enrolled-projects.json" >/dev/null; then
  echo "enrolled"
else
  echo "not enrolled"
fi
```

The verb exits 3 with nothing on stdout when it could not read the list whole (no proxy config, rate
limit, unreachable, `linear-list-truncated`); an `eris` that predates it answers
`Unknown linear command: projects` (run `eris update`). Linear answers an unknown label id with zero
projects, not an error. `hold:` is a hold, never "not enrolled"; log it, launch nothing, and add
`Resolve the enrolment read for <project>` to the ledger's Held for the reviewer. Only `not enrolled`
for every ledger issue's project is the "not run" case: log `not run: <project> not Socrates-enrolled`,
launch nothing, and add `Enrol <project> in Socrates?` to the ledger's Held for the reviewer.

Run it when the project is Socrates-enrolled and the work made or changed a decision or practice.
Scope it to this close-out's work only, never a sweep of the stint: list the ledger's PR URLs, the
`thoughts/` paths the work added or changed, and its Linear issue keys, and pass that list in the
brief.

Brief: *"Close-out under the reviewer's LGTM on `<PR>`: capture this work's candidates, over exactly
these artifacts: `<artifact list>`. For each decision or practice the artifacts made or changed, run
`eris socrates classify` on it, then
`eris socrates submit --title <t> --statement <s> --kind <decision|practice> --project <name>
--source <PR url> --evidence <one line: why, then repo@sha:path#L or the PR url>
[--section <target section heading, when the artifact names one>]`. Print any refusal from `submit`
verbatim, log it as `not run: <project>: <refusal slug>`, and hand the item back as held; don't
branch on the refusal's status code and don't retry. Don't run `eris socrates resolve` unless the
review Epic is already closed, don't run `eris socrates discover --advance`, and don't widen past this
list. Don't ask the reviewer."*

The enrolment read above gates the launch; a `submit` refusal is still a hold, never a silent drop.
Each held item goes to the ledger's Held for the reviewer.

Verify the hand-back against Linear. A subagent's narration is not evidence. A hand-back that cites a
source outside the artifact list, or reports an advanced cursor, broke scope: log it as a hold.

**Done when:** enrolment was read, and every candidate has a `submitted: <id>` or
`already submitted: <id>` receipt observed in Linear, or is logged "not run: <why>" and listed in
Held for the reviewer.

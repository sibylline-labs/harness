# Stage: close-ledger

Every profile. Post the ledger as one comment on the primary Linear issue. Linear is the record. When
the work has no Linear issue, post it as a comment on the PR. Then give the reviewer the same
content as the final report.

```
## Close-out — <PR link> (LGTM <date>) · profile <terminus|tpm-merge|next>
Merged <sha> · Deployed <how / none> · CI <green>
Report: /tpm <scope> → <applied / asked>   (next only; "not run: <why>" otherwise; terminus: "not in terminus"; tpm-merge: "TPM runs its own pass")
effort: est <old> → actual <new> (active <h>h, agent <h>h, gap 15m, sessions <n>)   (one per closed issue, prefixed with its key)
| Item | Disposition | Receipt |
Assumptions: assumed <X> because <Y>   (one per judgement call)
Held for the reviewer: <item> — <the one thing needed>   (or "none")
follow-ups: <filed issue IDs, post-merge checks, or kept session-cwd worktree cleanup command; never under `needs input:`; under tpm-merge also every `dispatch: allowed` suggestion and `follow-up:` lift line, for the TPM to dispatch>
Gates: <the profile check's stdout lines>
result: <one-line clean exit summary>
```

Keep credential locations, secret names and storage paths out of it: a written note that says where
a credential lives and which slots hold it has the blast radius of the credential itself.

## Receipt and the profile check

Write the ledger text to `$RUN/ledger.md` and record it, then check the profile with every comment id
this run's `record` calls printed:

```bash
eris gate record close-ledger --issue <primary> --verdict PASS \
  --artifact "$RUN/ledger.md" --evidence "profile <terminus|tpm-merge|next>: <rows> rows, <holds> held"
eris gate check --issue <primary> --profile <terminus|tpm-merge|next> \
  --profiles ~/.claude/skills/close/profiles.yaml --expect <ids, comma-separated>
```

Paste the check's lines into the `Gates:` line before posting. Exit 3 is a hold naming the failing
lines: a `forbidden` row under `terminus` means this run recorded a `next`-only stage, and
re-recording never clears it. Under `tpm-merge` it means the loop ran `/tpm` beside the TPM that
merged it: report the hold to the TPM, and never re-check the issue as `next`, which would pass a
second TPM pass. A `skipped` row is a doctrine `close.*: off` stage that the check recorded itself.
With no Linear issue there is nowhere to record: write `Gates: no Linear issue, not checked`
instead.

**Done when:** every ledger row appears with a receipt or a hold, the comment URL is in hand, the
check exited 0 (or its failing lines are a hold), and `rg -n 'TODO|<[a-z][a-z /|]*>'` over the
posted text comes back empty (no unfilled template slots). When running inside a background loop
session (or invoked with `authorized: TPM merge <repo>#<n> <sha>`), stop your own background session
as the very last step after posting the ledger comment (`claude stop <session-id>`, keeping the
conversation).

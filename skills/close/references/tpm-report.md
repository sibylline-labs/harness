# Stage: tpm-report

`next` only. The `terminus` and `tpm-merge` profiles forbid this gate: under `tpm-merge` the TPM that
merged the PR runs its own `/tpm` pass.

Dispatch a **separate subagent** running `/tpm <epic or project>`, scoped and never bare, when the
close-out finished an epic or milestone, unblocked issues, or exposed a carve gap. Hand it the filed
follow-ups, the `dispatch: allowed` improvement suggestions and the `follow-up:` lift lines from the
earlier stages as Delegate candidates. Brief, word for word: *"Close-out under the reviewer's LGTM:
the LGTM is the batch approval for the **Apply after the batch approval** rows of the
decision-rights table, for this scope only. Apply those. Return every **Ask the human first** row
unapplied, as a question with a recommended answer."* The LGTM does not cover a **Delegate** row
(`/tpm` decision rights): it comes back as a question for the reviewer.

Verify the hand-back against Linear: a subagent's narration is not evidence.

**Receipt.** Write the applied rows (each with its Linear receipt) and the returned questions to
`$RUN/tpm-report.md`, then:

```bash
eris gate record tpm-report --issue <primary> --verdict PASS \
  --artifact "$RUN/tpm-report.md" --evidence "/tpm <scope>: <n> applied, <m> asked"
```

When nothing earns a pass, write `not run: <why>` to the file and record PASS with that evidence.
Keep the printed comment id for the `close-ledger` check.

**Done when:** the pass is dispatched with its applied writes observed, or logged "not run: <why>",
and `record` printed an id.

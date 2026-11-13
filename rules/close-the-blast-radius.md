# Close the Blast Radius

**A change is complete only when its entire blast radius — every reference,
location, and consumer that participates in it — is enumerated and closed as
one unit.**

Fires on any change to a name, schema, contract, component or module. Before you
edit, grep every site that references, consumes or is fed by it. Include the files
no type-checker guards: YAML, env, Dockerfiles, shell, docs, matrix entries, and
the parent that renders what you built. That count defines done. Close it in one
commit or one atomic edit, then re-run the grep and expect zero. Read the
playbook,
[`~/.claude/rule-playbooks/close-the-blast-radius.md`](~/.claude/rule-playbooks/close-the-blast-radius.md),
for the mechanism and the surfaces it covers (renames, schemas, absorbed code,
new components, PR-wide verification).

## Red Flags

- You edited N sites without running the grep that says whether the total is N.
- The change touches something non-type-checked files consume.
- "Done" came from the focal module's green while other files in the diff went unscanned.
- Something was created and nothing checked it is consumed, or absorbed and the original still exists.
- A matrix or consumer list has M entries and you touched fewer.

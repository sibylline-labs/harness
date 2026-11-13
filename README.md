# harness

A starter kit for coding agents: workflow, gate, rubric and mode skills, subagents,
resident rules and hooks. It is built to run with Gates (`eris gate`, `eris doctrine`)
and to be installed on every machine with `eris org-skills install`.

| Path | What |
|---|---|
| `skills/` | `tpm`, `work`, `close`, `linear-workflow`, `retro`, `self-retro`, `systematic-debugging`, `test-driven-development`, `customize-harness` (workflows); `premise-gate`, `plan-review`, `prd-review`, `posture-check`, `thermo-nuclear-code-quality-review`, `verification-before-completion` (gates); `plan-shape`, `user-impact`, `unit-test-admission`, `improvement`, `emerging-tech-research` (rubrics); `bro`, `pls`, `lock-in` (modes) |
| `agents/` | `tpm-auditor`, `impl-generic`, `verify-adversarial`, `explore`, `research-agent` (Claude Code) |
| `opencode/agents/` | the same agents in OpenCode's format |
| `rules/` | resident rules, with their depth in `rules/playbooks/` |
| `hooks/` | opt-in hook scripts (`hooks/README.md`) |

## Use it

```bash
eris login
eris org-skills install
```

Your org installs this repository unless an admin sets another one under
**Gates → Settings → Skills repo**. To make it your own, read
[`skills/customize-harness/SKILL.md`](skills/customize-harness/SKILL.md).

## Checks

CI runs two gates on every change:

- `scrub`: `bun scripts/scrub-check.ts --history`. It finds no private names, tracker keys,
  tracker links, home paths or tokens in any file, path or commit.
- `skills-lint`: `eris skills lint .`, which checks every skill against its kind contract.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

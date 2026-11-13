---
name: customize-harness
kind: workflow
description: Make this harness your organisation's own — fork or template it, point your Gates org at it, install it on each machine, and change skills, agents, rules and hooks without breaking the kind contracts. Use when the user asks to customize, fork, extend or install the team harness, add or edit a skill, or wire it into a new machine or project.
---

# Customize the harness

This repository is a template. Use it as-is, or make it your organisation's own: every
machine in the org then installs the same skills, agents, rules and hooks from your copy.

## 1. Make your copy

- **Public or private fork:** on GitHub, use **Use this template** (a clean history) or
  fork it. A private repository works: `eris org-skills install` clones with each user's
  own `git` credentials, so anyone who can `git clone` it can install it.
- Keep `scripts/scrub-check.ts` and CI if your copy is public. Add the names your org
  must keep out with `bun scripts/scrub-check.ts --hash <term>`, one line each in
  `scripts/scrub-denylist.sha256`.

**Done when:** `git clone https://github.com/<owner>/<repo>.git` works for a teammate.

## 2. Point your org at it

In the Gates dashboard, open **Gates → Settings** and set **Skills repo** to
`<owner>/<repo>`. Left blank, the org installs `sibylline-labs/harness`.

**Done when:** the setting shows your `<owner>/<repo>`.

## 3. Install it

```bash
eris login                     # once per machine
eris org-skills install        # clone into ~/.eris/skills/<orgId>/ and link it
```

The install lints the checkout first and refuses to link a tree that breaks a kind
contract. It links:

| From your repo | To |
|---|---|
| `skills/<name>/` | `~/.agents/skills/<name>` and `~/.claude/skills/<name>` |
| `agents/<name>.md` | `~/.claude/agents/<name>.md` |
| `rules/<name>.md` | `~/.claude/rules/<name>.md` |
| `opencode/<path>` | `~/.config/opencode/<path>` |

Any real file it replaces is backed up first, and a failed install undoes what it linked.
A `$HOME` already linked to another org refuses to switch silently. Use one of:

- `eris org-skills install --project` links into the current repository's `.claude/`
  instead (kept out of git through `.git/info/exclude`);
- `eris org-skills install --switch-global` re-points `$HOME` at the new org.

Re-run `eris org-skills install` to pick up changes from your repo.

**Done when:** `ls -l ~/.claude/skills/` shows links into `~/.eris/skills/<orgId>/`.

## 4. Change a skill

- Every `skills/<name>/SKILL.md` declares one `kind:` in its frontmatter: `tool`, `gate`,
  `rubric`, `workflow`, `reference` or `mode`.
- `tool` ships a non-empty `scripts/`.
- `reference` holds no numbered procedure.
- A `workflow` over 200 lines keeps its stages in `references/*.md`.
- A `rubric` stays at 60 lines or fewer. It is preloaded by some agent's or skill's
  `skills: [...]` line, and named by some `gate` skill.

Run the check before you push:

```bash
eris skills lint .
```

**Done when:** `eris skills lint .` exits 0 and CI is green.

## 5. Add agents, rules and hooks

- An agent is `agents/<name>.md` with Claude Code frontmatter. Put its OpenCode twin at
  `opencode/agents/<name>.md`.
- A rule is `rules/<name>.md`, loaded into every session, so keep it short. Put the depth
  in `rules/playbooks/<name>.md` and link it.
- A hook goes in `hooks/` and is opted into per machine (`hooks/README.md`). The install
  never edits your agent's settings.

**Done when:** the new file is linked after a re-install and CI is green.
